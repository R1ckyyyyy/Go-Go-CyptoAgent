import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from src.trading.executor import TradeExecutor
from src.database.models import AIDecision
from src.database.operations import db

async def test_paper_trade():
    print("🚀 Starting Execution Test (PAPER MODE)...")
    
    # 1. Initialize Executor
    executor = TradeExecutor()
    print(f"Executor Mode: {executor.trading_mode}")
    
    # 2. Mock an AI Decision
    mock_decision = AIDecision(
        decision_type="TRADE",
        output_recommendation={
            "action": "BUY",
            "symbol": "ETHUSDT",
            "quantity": 0.5 
        },
        confidence=0.95
    )
    
    # 3. Execute
    print(f"🤖 AI Decides: {mock_decision.output_recommendation}")
    result = await executor.execute_decision(mock_decision)
    
    print(f"📝 Execution Result: Success={result.success}, Msg='{result.message}'")
    
    if result.success:
        print("✅ Trade executed successfully.")
        
        # 4. Verify DB Trade
        trades = db.get_trades(limit=1)
        if trades and trades[0].order_id == result.order_id:
            print(f"✅ Trade verified in DB: {trades[0]}")
        else:
            print("❌ Trade NOT found in DB!")
            
        # 5. Verify DB Position
        positions = db.get_all_positions()
        target_pos = next((p for p in positions if p.symbol == "ETHUSDT"), None)
        if target_pos:
            print(f"✅ Position verified in DB: {target_pos.symbol} Qty:{target_pos.amount} Avg:${target_pos.avg_price:.2f}")
        else:
            print("❌ Position NOT found in DB!")
    else:
        print("❌ Execution failed.")

if __name__ == "__main__":
    asyncio.run(test_paper_trade())
