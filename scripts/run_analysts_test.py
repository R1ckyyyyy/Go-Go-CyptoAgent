import sys
import os
import asyncio
import json
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

# Load environment variables
root_env = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(root_env):
    load_dotenv(root_env)
backend_env = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
if os.path.exists(backend_env):
    load_dotenv(backend_env)

# Force Gemini Provider
os.environ['LLM_PROVIDER'] = 'gemini'

from src.ai_agents.technical_analyst import TechnicalAnalystAgent
from src.ai_agents.fundamental_analyst import FundamentalAnalystAgent
from src.ai_agents.sentiment_analyst import SentimentAnalystAgent
from src.ai_agents.risk_assessor import RiskAssessorAgent

async def test_agent(agent_name, agent_class, input_data):
    print(f"\n--- Testing {agent_name} ---")
    try:
        agent = agent_class()
        print(f"🤖 Agent Initialized (Model: {getattr(agent, 'gemini_model', 'Unknown')})")
        
        print("📥 Sending Input Data...")
        # print(json.dumps(input_data, indent=2))
        
        print("🧠 Thinking...")
        result = await agent.process(input_data)
        
        print("t📤 Result Received:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if "error" in result:
             print(f"❌ {agent_name} Failed: {result['error']}")
             return False
        else:
             print(f"✅ {agent_name} Passed")
             return True
             
    except Exception as e:
        print(f"❌ Exception testing {agent_name}: {e}")
        return False

async def main():
    print("🚀 Starting Specialized Analysts Batch Test")
    
    # 1. Technical Analyst Mock Data
    tech_input = {
        "symbol": "BTCUSDT",
        "current_price": 42000,
        "identifiers": {"RSI": 75, "MACD": "Bullish Cross"}, # Simplified
        "kline_summary": "Uptrend on 4H, consolidation on 1H"
    }
    
    # 2. Fundamental Analyst Mock Data
    fund_input = {
        "symbol": "ETHUSDT",
        "onchain_data": {"net_exchange_flow": "-5000 ETH (Outflow)", "large_tx_count": 120},
        "funding_rate": "0.01%",
        "news_summary": "Ethereum upgrade successful, gas fees stabilizing."
    }
    
    # 3. Sentiment Analyst Mock Data
    sent_input = {
        "fear_greed_index": 75,
        "social_media_data": "Trending #Bitcoin on Twitter, generally positive sentiment.",
        "news_data": "Major institutions buying the dip."
    }
    
    # 4. Risk Assessor Mock Data
    risk_input = {
        "current_positions": [{"symbol": "BTCUSDT", "amount": 0.5, "entry": 40000}],
        "market_volatility": "High",
        "proposed_trade": {"symbol": "SOLUSDT", "action": "BUY", "amount": 10}
    }

    results = []
    results.append(await test_agent("Technical Analyst", TechnicalAnalystAgent, tech_input))
    results.append(await test_agent("Fundamental Analyst", FundamentalAnalystAgent, fund_input))
    results.append(await test_agent("Sentiment Analyst", SentimentAnalystAgent, sent_input))
    results.append(await test_agent("Risk Assessor", RiskAssessorAgent, risk_input))
    
    print("\n" + "="*30)
    print(f"📊 Test Summary: {sum(results)}/{len(results)} Agents Passed")
    print("="*30)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
