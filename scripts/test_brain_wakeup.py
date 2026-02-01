import sys
import os
import asyncio
import json

from dotenv import load_dotenv

# Load env (Root and Backend)
root_env = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(root_env):
    load_dotenv(root_env)

backend_env = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
if os.path.exists(backend_env):
    load_dotenv(backend_env)

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# FORCE GEMINI BEFORE IMPORTS
os.environ['LLM_PROVIDER'] = 'gemini'

from src.ai_agents.coordinator import CoordinatorAgent

async def test_brain_wakeup():
    print("🧠 Starting Brain Simulation Test...")
    
    # 1. Initialize Coordinator
    coordinator = CoordinatorAgent()
    print("✅ Coordinator Initialized.")
    
    # 2. Mock a Watchdog Event
    # This is exactly what the Watchdog sends when it detects a trigger
    mock_event = {
        "type": "PROXIMITY_ALERT",
        "symbol": "BTCUSDT",
        "current_price": 78500.0,
        "reason": "Trigger Hit: Price 78500 <= 78550 (TEST Trigger)",
        "technical_summary": {
            "rsi_1h": 32.5,  # Low RSI -> Signal Oversold
            "trend_1h": "BEARISH",
            "volatility": 120.5
        },
        "timestamp": 1700000000
    }
    print(f"📡 Injecting Event: {mock_event['type']} - {mock_event['reason']}")
    
    # 3. Process
    try:
        response = await coordinator.process(mock_event)
        
        print("\n🤖 AI Response:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        # 4. Verify Action
        action = response.get("action", {})
        if action.get("type"):
            print(f"✅ AI Decided to: {action.get('type')}")
        else:
            print("⚠️ AI decided to do nothing (which is also a valid decision).")
            
    except Exception as e:
        print(f"❌ Error during processing: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_brain_wakeup())
