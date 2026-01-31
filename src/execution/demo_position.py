import asyncio
import os
from src.execution.position_manager import PositionManager
from src.utils.logger import logger

def run_demo():
    print("=== Position Manager Demo ===")
    
    # 1. Simulated Mode Demo
    print("\n[Mode: Simulated]")
    sim_pm = PositionManager(mode="simulated")
    
    # Initial State
    print("Initial Summary:", sim_pm.get_summary())
    
    # Execute a Virtual Trade
    trade = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "quantity": 0.5,
        "price": 40000.0,
        "fee": 0.0
    }
    print(f"Executing Trade: {trade}")
    sim_pm.update_position(trade)
    
    # Result State
    summary = sim_pm.get_summary()
    print("Updated Summary:")
    print(f"Total Balance: {summary['account_summary']['total_balance']}")
    print(f"Positions: {len(summary['positions'])}")
    if summary['positions']:
        print(f"First Position: {summary['positions'][0]}")

    # 2. Live Mode Demo (Safety Check)
    # Only run if explicitly enabled to avoid accidental API calls during demo
    # Here we just show initialization
    print("\n[Mode: Live]")
    try:
        live_pm = PositionManager(mode="live")
        # NOTE: get_summary() requires valid API keys and network access
        # print("Live Summary:", live_pm.get_summary()) 
        print("Live PositionManager initialized successfully (API connection required for data).")
    except Exception as e:
        print(f"Live init failed (expected if no API keys): {e}")

if __name__ == "__main__":
    # Ensure logs folder exists
    os.makedirs("data/logs", exist_ok=True)
    run_demo()
