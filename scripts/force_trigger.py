import sys
import os
import asyncio
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from src.database.operations import db
from src.api.binance_api import BinanceConnector
from src.utils.logger import logger

async def inject_trigger():
    print("💉 Preparing to inject test trigger...")
    
    # 1. Get Real Price
    connector = BinanceConnector()
    ticker = connector.get_ticker("BTCUSDT")
    price = float(ticker['price'])
    print(f"📉 Current BTC Price: ${price}")
    
    # 2. Create a trigger VERY close to current price to force immediate wake-up
    # Watchdog threshold is usually 0.5%. We set it 0.1% away.
    trigger_price = price * 0.999 
    
    trigger_data = {
        "description": "TEST: Immediate Wakeup Check",
        "trigger_type": "PRICE_LEVEL",
        "condition_data": {
            "symbol": "BTCUSDT",
            "operator": "LTE", # Wake up if price <= trigger_price
            "value": trigger_price
        },
        "status": "ACTIVE"
    }
    
    # 3. Insert to DB
    db.add_trigger(trigger_data)
    print(f"✅ Injected Trigger: {trigger_data}")
    print("👉 Now run 'scripts/run_real_coordinator.py' and it should wake up immediately!")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(inject_trigger())
