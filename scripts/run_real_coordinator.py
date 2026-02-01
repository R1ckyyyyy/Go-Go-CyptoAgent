import sys
import os
import asyncio
import json
import time
from datetime import datetime
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from binance import AsyncClient, BinanceSocketManager
import yaml

# Path setup
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

# Load env
root_env = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(root_env):
    load_dotenv(root_env)

backend_env = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
if os.path.exists(backend_env):
    load_dotenv(backend_env)

os.environ['LLM_PROVIDER'] = 'gemini'
os.environ['PAPER_TRADING'] = 'true' # Default safe mode

from src.ai_agents.coordinator import CoordinatorAgent
from src.ai_agents.consultants.technical import TechnicalConsultant
from src.ai_agents.consultants.fundamental import FundamentalConsultant
from src.ai_agents.consultants.risk import RiskConsultant
from src.database.operations import db
from src.utils.logger import logger

# --- Token Saver: Local Python Pre-processor ---
class MarketPreprocessor:
    @staticmethod
    def calculate_rsi(prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def get_snapshot(connector, symbol="BTCUSDT"):
        """
        Locally calculate indicators to avoid sending raw K-lines to LLM.
        Result: A tiny JSON summarizing market state.
        """
        try:
            # Get last 50 candles (1h)
            # Note: For async context, we might want an async version, but connector uses sync client.
            # This is acceptable for now.
            df = connector.get_kline_data(symbol, interval="1h", limit=50)
            if df.empty:
                return {"error": "no_data"}
            
            # Calc RSI
            df['rsi'] = MarketPreprocessor.calculate_rsi(df['close'])
            current_rsi = df['rsi'].iloc[-1]
            
            # Calc Volatility (Std Dev of last 20 closes)
            volatility = df['close'].rolling(20).std().iloc[-1]
            
            # Trend (SMA 20 vs Price)
            sma20 = df['close'].rolling(20).mean().iloc[-1]
            price = df['close'].iloc[-1]
            trend = "BULLISH" if price > sma20 else "BEARISH"
            
            return {
                "rsi_1h": round(current_rsi, 2),
                "volatility": round(volatility, 2),
                "trend_1h": trend,
                "price_vs_sma20": f"{round((price - sma20)/sma20 * 100, 2)}%"
            }
        except Exception as e:
            logger.error(f"Preprocessor Error: {e}")
            return {"error": str(e)}

# --- Watchdog Core ---
class Watchdog:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.triggers = []
        self.last_wake_time = 0
        self.min_wake_interval = 60 # Prevent AI spamming (max 1 wake per min)
        self.symbol = "BTCUSDT"
        
        # Load initial triggers
        self.reload_triggers()
        logger.info(f"🐕 Watchdog started. Monitoring {len(self.triggers)} triggers.")

    def reload_triggers(self):
        """Reload active triggers from DB"""
        raw_triggers = db.get_active_triggers()
        self.triggers = []
        for t in raw_triggers:
            try:
                # Parse condition: e.g., {'symbol': 'BTCUSDT', 'operator': 'GTE', 'value': 80000}
                # Assuming condition_data is stored as dict or json string in DB model
                cond = t.condition_data
                if isinstance(cond, str):
                    cond = json.loads(cond)
                
                self.triggers.append({
                    "id": t.id,
                    "desc": t.description,
                    "target": float(cond.get('value', 0)),
                    "operator": cond.get('operator', 'GTE')
                })
            except Exception as e:
                logger.error(f"Failed to parse trigger {t.id}: {e}")
        
        if not self.triggers:
            pass

    def should_wake_up(self, current_price):
        """
        The Core Logic: 
        Check if we are CLOSE ENOUGH to any trigger to wake up the AI.
        Threshold: 0.5% (0.005)
        """
        for t in self.triggers:
            target = t['target']
            # Proximity check
            if abs(current_price - target) / target < 0.005:
                return True, f"Proximity Alert: Price {current_price} is near target {target} ({t['desc']})"
                
            # Hard trigger check (crossed)
            if t['operator'] == 'GTE' and current_price >= target:
                return True, f"Trigger Hit: Price {current_price} >= {target} ({t['desc']})"
            if t['operator'] == 'LTE' and current_price <= target:
                return True, f"Trigger Hit: Price {current_price} <= {target} ({t['desc']})"
                
        return False, ""

    async def handle_message(self, msg):
        """Async Callback from WebSocket"""
        if msg['e'] != 'trade':
            return
            
        current_price = float(msg['p'])
        
        # 0. Check System Status (Control Switch)
        status = db.get_config("system_status", "STOPPED")
        if status != "RUNNING":
            # Optional: Log once every minute to say "I'm paused"
            if time.time() - self.last_wake_time > 60:
                 logger.info("💤 System is PAUSED via Dashboard.")
                 self.last_wake_time = time.time()
            return

        # Heartbeat Update (Proof of Life)
        db.set_config("system_heartbeat", datetime.now().strftime("%H:%M:%S"))

        # 1. Check Rate Limit (Don't wake up too often)
        if time.time() - self.last_wake_time < self.min_wake_interval:
            return

        # 2. Local Filter (Zero Token Cost)
        should_wake, reason = self.should_wake_up(current_price)
        
        if should_wake:
            logger.info(f"🐕 WOOF! Watchdog waking up AI. Reason: {reason}")
            self.last_wake_time = time.time()
            
            # 3. Pre-process Data (Token Saver)
            snapshot = MarketPreprocessor.get_snapshot(self.coordinator.connector, self.symbol)
            
            event = {
                "type": "PROXIMITY_ALERT",
                "symbol": self.symbol,
                "current_price": current_price,
                "reason": reason,
                "technical_summary": snapshot, # Compact data
                "timestamp": time.time()
            }
            
            # 4. Invoke AI in Async Loop
            await self.run_ai_cycle(event)

    async def run_ai_cycle(self, event):
        """Async wrapper for the AI cycle"""
        print(f"\n[{time.strftime('%H:%M:%S')}] 🧠 AI Awakened by Watchdog...")
        decision = await self.coordinator.process(event)
        
        # Print Result
        print(f" -> Decision: {decision.get('action', {}).get('type')}")
        if decision.get('action', {}).get('type') == 'SET_TRIGGER':
             self.reload_triggers() # Update local cache immediately
             print(" -> 🔄 Watchdog triggers updated.")

async def main():
    print("\n--- 🚀 Starting Coordinator (Watchdog Mode - Async) ---")
    
    # Init Coordinator
    coordinator = CoordinatorAgent()
    if not coordinator.connector:
        print("❌ Error: Connector failed.")
        return

    # Init Consultants
    coordinator.register_consultant("technical", TechnicalConsultant())
    coordinator.register_consultant("fundamental", FundamentalConsultant())
    coordinator.register_consultant("risk_management", RiskConsultant())
    print("✅ System Initialized.")

    # Start Watchdog
    dog = Watchdog(coordinator)
    
    # Start WebSocket using AsyncClient
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    
    # Load Proxy from Config
    config_path = os.path.join(os.path.dirname(__file__), "..", "backend", "config", "config.yaml")
    requests_params = None
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                proxy_url = config.get('network', {}).get('proxy')
                if proxy_url:
                    print(f"🔗 Using Proxy: {proxy_url}")
                    requests_params = {'proxy': proxy_url}
        except Exception as e:
            print(f"⚠️ Failed to load proxy config: {e}")

    # Initialize AsyncClient with Proxy and Testnet
    client = await AsyncClient.create(
        api_key=api_key, 
        api_secret=api_secret,
        testnet=True,
        requests_params=requests_params
    )
    bm = BinanceSocketManager(client)
    
    print(f"✅ Connecting to Binance WebSocket for {dog.symbol}...")
    ts = bm.trade_socket(dog.symbol)
    
    print("🐕 Watchdog is silent. Waiting for price triggers... (Ctrl+C to stop)")
    print(f"🎯 Current Triggers: {[t['desc'] for t in dog.triggers]}")

    try:
        async with ts as tscm:
            while True:
                msg = await tscm.recv()
                await dog.handle_message(msg)
                
    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close_connection()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
