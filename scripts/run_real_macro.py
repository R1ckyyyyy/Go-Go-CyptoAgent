import sys
import os
import asyncio
import json
from dotenv import load_dotenv

# Add backend to path to allow imports from src
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from src.ai_agents.macro_planner import MacroPlannerAgent
from src.api.binance_api import BinanceConnector

# Load environment variables
# Try root .env
root_env = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(root_env):
    load_dotenv(root_env)
    print(f"Loaded root .env from {root_env}")

# Try backend .env (where backend module is)
backend_env = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
if os.path.exists(backend_env):
    load_dotenv(backend_env)
    print(f"Loaded backend .env from {backend_env}")

# Force Gemini Provider for this test
os.environ['LLM_PROVIDER'] = 'gemini'

# Debug Key (Masked)
key = os.getenv("GEMINI_API_KEY")
if key:
    print(f"✅ GEMINI_API_KEY found: {key[:5]}...{key[-3:]}")
else:
    print("❌ GEMINI_API_KEY NOT found in environment variables")

async def main():
    print("\n--- 🚀 Starting Real-World AI Macro Planner Test ---")
    
    # 1. Initialize
    print("[1/4] Connecting to Binance...")
    try:
        binance = BinanceConnector()
    except Exception as e:
        print(f"❌ Binance Connection Failed: {e}")
        return

    print("[1/4] Initializing Macro Planner Agent...")
    try:
        agent = MacroPlannerAgent()
    except Exception as e:
        print(f"❌ Agent Initialization Failed: {e}")
        return
    
    # 2. Fetch Real Data
    print("\n[2/4] Fetching Real-time Market Data...")
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    market_data = {}
    
    for sym in symbols:
        try:
            # Fetch Price
            ticker = binance.get_ticker(sym)
            price = ticker['price']
            
            # Fetch 24h Stats (Optional, simplified here)
            # stats = binance.client.get_ticker(symbol=sym) 
            
            market_data[sym] = {
                "current_price": price,
                "timestamp": "Now"
            }
            print(f"      ✅ Got {sym}: ${price}")
        except Exception as e:
            print(f"      ❌ Error fetching {sym}: {e}")
            market_data[sym] = {"error": str(e)}

    # Mock positions for context (Simulated Portfolio)
    current_positions = [
        {"symbol": "BTCUSDT", "amount": 0.5, "entry_price": 40000, "current_value": 0.5 * market_data.get("BTCUSDT", {}).get("current_price", 40000)},
        {"symbol": "ETHUSDT", "amount": 10.0, "entry_price": 2200, "current_value": 10.0 * market_data.get("ETHUSDT", {}).get("current_price", 2200)}
    ]
    
    # 3. AI Analysis
    model_name = getattr(agent, 'gemini_model', getattr(agent, 'claude_model', 'Unknown Model'))
    print(f"\n[3/4] AI Agent (Provider: {agent.provider}, Model: {model_name}) is thinking...")
    print("      (Gathering liquidity data, analyzing trends, formulating strategy...)")
    
    try:
        # The agent will call the LLM internally
        decision = await agent.plan_strategy(market_data, current_positions)
        
        # 4. Output Result
        print("\n[4/4] 🧠 AI Macro Strategy Generated:")
        print("="*60)
        print(json.dumps(decision, indent=2, ensure_ascii=False))
        print("="*60)
        
        print("\n✅ Test Complete. The AI has spoken.")
        
    except Exception as e:
        print(f"\n❌ AI Execution Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Windows specific event loop policy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())
