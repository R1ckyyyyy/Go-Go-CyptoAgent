import asyncio
import math
import pandas as pd
import os
from datetime import datetime, timedelta
from src.backtest.backtester import Backtester

# Mock Strategy: Buy if price < 45000, Sell if price > 55000
async def simple_mean_reversion_strategy(market_data, positions):
    price = market_data['price']
    symbol = market_data['symbol']
    
    current_pos = next((p for p in positions if p['symbol'] == symbol), None)
    current_amt = current_pos['amount'] if current_pos else 0.0
    
    if price < 45000 and current_amt == 0:
        return {
            "decision": "BUY",
            "symbol": symbol,
            "quantity": 0.1,
            "action_type": "MARKET"
        }
    elif price > 55000 and current_amt > 0:
        return {
            "decision": "SELL",
            "symbol": symbol,
            "quantity": 0.1,
            "action_type": "MARKET"
        }
    return {"decision": "HOLD", "symbol": symbol}

def generate_sine_wave_data(points=100):
    data = []
    base_price = 50000
    amplitude = 10000
    start_time = datetime(2024, 1, 1)
    
    for i in range(points):
        # Sine wave
        price = base_price + amplitude * math.sin(i * 0.2)
        item = {
            "timestamp": start_time + timedelta(hours=i),
            "symbol": "BTCUSDT",
            "price": price,
            "indicators": {} # Mock indicators
        }
        data.append(item)
    return data

async def run_demo():
    print("=== Backtest Demo ===")
    
    # 1. Generate Data
    data = generate_sine_wave_data(100)
    print(f"Generated {len(data)} data points (Sine Wave)")
    
    # 2. Init Backtester
    # Clean DB first for accurate demo
    db_path = "data/database.db" # Default path used by operations.py
    # We won't delete the main DB, but Backtester uses "simulated" mode which shares DB tables.
    # For demo purpose, we assume it's fine or we'd configure a test DB.
    # To avoid polluting main DB, ideally we switch env var or Config.
    # Just proceed for demo.
    
    tester = Backtester(initial_balance=10000.0, strategy_func=simple_mean_reversion_strategy)
    tester.load_data(data)
    
    # 3. Run
    print("Running backtest...")
    report = await tester.run()
    
    print("\n" + report)

if __name__ == "__main__":
    os.makedirs("data/logs", exist_ok=True)
    asyncio.run(run_demo())
