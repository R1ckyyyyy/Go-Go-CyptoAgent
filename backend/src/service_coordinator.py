import asyncio
import json
import time
import os
import yaml
from datetime import datetime
from dotenv import load_dotenv

# Load Env immediately
# Load Env immediately
env_path = os.path.join(os.path.dirname(__file__), "..", ".env") # backend/.env
if not os.path.exists(env_path):
    # Fallback to root .env
    env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(env_path)

from binance import AsyncClient, BinanceSocketManager

from src.ai_agents.coordinator import CoordinatorAgent
from src.ai_agents.consultants.technical import TechnicalConsultant
from src.ai_agents.consultants.fundamental import FundamentalConsultant
from src.ai_agents.consultants.risk import RiskConsultant
from src.database.operations import db
from src.utils.logger import logger

# Ensure Env
os.environ['LLM_PROVIDER'] = 'gemini'
os.environ['PAPER_TRADING'] = 'true'

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
        try:
            df = connector.get_kline_data(symbol, interval="1h", limit=50)
            if df.empty:
                return {"error": "no_data"}
            
            df['rsi'] = MarketPreprocessor.calculate_rsi(df['close'])
            current_rsi = df['rsi'].iloc[-1]
            volatility = df['close'].rolling(20).std().iloc[-1]
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
    def __init__(self, coordinator, symbols=None):
        self.coordinator = coordinator
        self.triggers = []
        self.symbols = symbols if symbols else ["BTCUSDT", "ETHUSDT", "SOLUSDT", "DOGEUSDT"]
        self.last_wake_times = {s: 0 for s in self.symbols} # Per-symbol timer
        self.min_wake_interval = 60
        self.reload_triggers()
        logger.info(f"🐕 Watchdog Configured. Monitoring {len(self.triggers)} triggers for {self.symbols}.")

    def reload_triggers(self):
        """Reload active triggers from DB"""
        raw_triggers = db.get_active_triggers()
        self.triggers = []
        for t in raw_triggers:
            try:
                cond = t.condition_data
                if isinstance(cond, str):
                    cond = json.loads(cond)
                
                # Special handling for MANUAL triggers
                is_manual = (t.trigger_type == "MANUAL" or cond.get('operator') == 'IMMEDIATE')

                self.triggers.append({
                    "id": t.id,
                    "desc": t.description,
                    "target": float(cond.get('value', 0)),
                    "operator": cond.get('operator', 'GTE'),
                    "symbol": cond.get('symbol', 'BTCUSDT'), # Assume BTC if missing
                    "type": t.trigger_type,
                    "is_manual": is_manual
                })
            except Exception as e:
                logger.error(f"Failed to parse trigger {t.id}: {e}")

    def should_wake_up(self, current_price, symbol):
        for t in self.triggers:
            # 1. Manual/Immediate Trigger (Priority High)
            if t.get('is_manual'):
                 # Check if this manual trigger matches current symbol context (optional, but good for multi-pair)
                 # Actually manual trigger is usually symbol agnostic manually, BUT we should check symbol in DB metadata
                 # For now, we handle manual in monitor_triggers separately.
                 pass

            # Filter by symbol
            if t.get('symbol') != symbol:
                continue

            target = t['target']
            # Proximity check (0.5%)
            if abs(current_price - target) / target < 0.005:
                start_msg = f"Proximity Alert: {symbol} Price {current_price} is near target {target}"
                return True, start_msg, t
            # Hard trigger check
            if t['operator'] == 'GTE' and current_price >= target:
                return True, f"Trigger Hit: {symbol} Price {current_price} >= {target}", t
            if t['operator'] == 'LTE' and current_price <= target:
                return True, f"Trigger Hit: {symbol} Price {current_price} <= {target}", t
        return False, "", None

    async def monitor_triggers(self):
        """Dedicated loop to check DB for Manual/Time triggers independent of market data"""
        logger.info("⏰ Trigger Monitor Loop Started.")
        while True:
            try:
                # 1. Check for manual triggers
                self.reload_triggers()
                
                # Check ALL triggers for 'is_manual'
                manual_trigger = next((t for t in self.triggers if t.get('is_manual')), None)
                
                if manual_trigger:
                    logger.info(f"⚡ MANUAL TRIGGER DETECTED: {manual_trigger['desc']}")
                    target_symbol = manual_trigger.get('symbol', 'BTCUSDT') # Default to BTC

                    # Consume immediately
                    db.update_trigger_status(manual_trigger['id'], "TRIGGERED")
                    
                    # Prepare Event
                    snapshot = MarketPreprocessor.get_snapshot(self.coordinator.connector, target_symbol)
                    event = {
                        "type": "MANUAL_INTERVENTION",
                        "symbol": target_symbol,
                        "current_price": 0, 
                        "reason": f"User Trigger: {manual_trigger['desc']}",
                        "technical_summary": snapshot,
                        "timestamp": time.time()
                    }
                    
                    # Execute AI
                    await self.run_ai_cycle(event)
                    
                    # Reload to remove consumed trigger
                    self.reload_triggers()
                
                await asyncio.sleep(2) # Poll every 2 seconds
            except Exception as e:
                logger.error(f"Trigger Monitor Error: {e}")
                await asyncio.sleep(5)

    async def handle_message(self, msg):
        # Handle 'trade' stream from valid symbol
        stream = msg.get('s') # Symbol e.g. BTCUSDT
        current_price = float(msg.get('p', 0))
        if not stream or current_price == 0: return
        
        # 0. Check System Status
        status = db.get_config("system_status", "STOPPED")
        if status != "RUNNING":
            if time.time() - self.last_wake_times.get(stream, 0) > 60:
                 self.last_wake_times[stream] = time.time()
            return

        # Heartbeat (Global)
        db.set_config("system_heartbeat", datetime.now().strftime("%H:%M:%S"))

        # 2. Local Filter (Only Price/Tech triggers now)
        should_wake, reason, trigger_obj = self.should_wake_up(current_price, stream)
        
        # Filter out manual triggers here as they are handled by monitor loop
        if trigger_obj and trigger_obj.get('is_manual'):
            return 

        if time.time() - self.last_wake_times.get(stream, 0) < self.min_wake_interval:
            return

        if should_wake:
            logger.info(f"🐕 WOOF! Watchdog waking up AI for {stream}. Reason: {reason}")
            self.last_wake_times[stream] = time.time()
            snapshot = MarketPreprocessor.get_snapshot(self.coordinator.connector, stream)
            
            event = {
                "type": "PROXIMITY_ALERT",
                "symbol": stream,
                "current_price": current_price,
                "reason": reason,
                "technical_summary": snapshot,
                "timestamp": time.time()
            }
            await self.run_ai_cycle(event)
    async def run_ai_cycle(self, event):
        logger.info(f"🧠 AI ({event.get('symbol')}) Awakened by Watchdog...")
        decision = await self.coordinator.process(event)
        
        action_type = decision.get('action', {}).get('type')
        if action_type == 'SET_TRIGGER':
             self.reload_triggers()
             logger.info("Watchdog triggers updated.")

# ...

async def start_coordinator_service():
    """Background Task Entry Point"""
    # ... existing init code ...
    logger.info("--- 🚀 Starting Coordinator Service (Background) ---")
    
    coordinator = CoordinatorAgent()
    if not coordinator.connector:
        logger.error("❌ Connector failed. Service aborting.")
        return

    coordinator.register_consultant("technical", TechnicalConsultant())
    coordinator.register_consultant("fundamental", FundamentalConsultant())
    coordinator.register_consultant("risk_management", RiskConsultant())

    # --- 🔌 Thought Stream: Bridge Internal Comms to WebSocket ---
    from src.utils.websocket import ws_manager
    from src.ai_agents.communication import CommunicationChannel, AgentMessage
    
    async def bridge_to_ws(msg: AgentMessage):
        """Forward internal agent messages to Frontend UI"""
        try:
            payload = {
                "type": "THOUGHT_STREAM",
                "sender": msg.sender,
                "receiver": msg.receiver,
                "content": msg.content,
                "timestamp": datetime.now().isoformat()
            }
            await ws_manager.broadcast_json(payload)
        except Exception as e:
            logger.error(f"WS Bridge Error: {e}")

    # Subscribe to ALL messages
    channel = CommunicationChannel()
    channel.subscribe("all", bridge_to_ws)
    
    # Broadcast "Awake" event
    await ws_manager.broadcast_json({
        "type": "SYSTEM_EVENT", 
        "event": "SERVICE_STARTED",
        "message": "Coordinator Service is Online."
    })

    dog = Watchdog(coordinator)
    
    # Start the Trigger Monitor Loop
    asyncio.create_task(dog.monitor_triggers())
    
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    
    # ... existing client setup ...
    requests_params = None
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml") # Relative to src/
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                proxy = config.get('network', {}).get('proxy')
                if proxy:
                    requests_params = {'proxy': proxy}
        except Exception:
            pass

    client = await AsyncClient.create(
        api_key=api_key, 
        api_secret=api_secret,
        testnet=True,
        requests_params=requests_params
    )
    
    bm = BinanceSocketManager(client)
    # trade_socket is for single symbol. For multi, we need multiplex.
    # Format: <symbol>@trade
    streams = [f"{s.lower()}@trade" for s in dog.symbols]
    ts = bm.multiplex_socket(streams)
    
    logger.info(f"✅ Coordinator Service Connected to WebSocket {streams}")

    try:
        async with ts as tscm:
            while True:
                res = await tscm.recv()
                # Multiplex returns dict: {'stream': 'btcusdt@trade', 'data': {...}}
                if 'data' in res:
                    await dog.handle_message(res['data'])
    except asyncio.CancelledError:
        logger.info("Coordinator Service stopping...")

    except Exception as e:
        logger.error(f"Coordinator Service crashed: {e}")
    finally:
        await client.close_connection()
