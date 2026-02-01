import sys
import os
import asyncio
import json
from datetime import datetime
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

# Force Gemini
os.environ['LLM_PROVIDER'] = 'gemini'

from src.ai_agents.macro_planner import MacroPlannerAgent
from src.ai_agents.technical_analyst import TechnicalAnalystAgent
from src.ai_agents.fundamental_analyst import FundamentalAnalystAgent
from src.ai_agents.sentiment_analyst import SentimentAnalystAgent
from src.ai_agents.risk_assessor import RiskAssessorAgent
from src.ai_agents.decision_maker import DecisionMakerAgent

async def main():
    print("\n--- 🧠 Starting Full AI Decision Flow Simulation ---")
    print(f"Timestamp: {datetime.now().isoformat()}")

    # 1. Initialize All Agents
    print("\n[Init] Awakening the AI Council...")
    macro_agent = MacroPlannerAgent()
    tech_agent = TechnicalAnalystAgent()
    fund_agent = FundamentalAnalystAgent()
    sent_agent = SentimentAnalystAgent()
    risk_agent = RiskAssessorAgent()
    decision_agent = DecisionMakerAgent()
    
    # 2. Step 1: Macro Planning (Simulated)
    print("\n[Step 1] Macro Planner analyzing global context...")
    # Mocking Macro output to save time/tokens and control the scenario
    macro_strategy = {
        "market_environment": "牛市 (Bull Market)",
        "market_sentiment": "Greed",
        "strategy_direction": "Aggressive",
        "tasks_to_assign": [
            {"assign_to": "technical_analyst", "task": "Analyze BTC breakup structure"},
            {"assign_to": "risk_manager", "task": "Calculate max position size for aggressive entry"}
        ],
        "reasoning": "Global liquidity increasing, BTC broke previous ATH."
    }
    print(" >>> Macro Strategy Output:")
    print(json.dumps(macro_strategy, indent=2, ensure_ascii=False))

    # 3. Step 2: Analysts Execution (Simulated Parallel Processing)
    print("\n[Step 2] Specialized Analysts executing tasks...")
    
    # Mock inputs for analysts (derived from Macro context + specific data)
    tech_input = {"symbol": "BTCUSDT", "identifiers": {"RSI": 72, "Trend": "Strong Up"}, "current_price": 65000}
    fund_input = {"symbol": "BTCUSDT", "onchain_data": "Inflow Low", "news_summary": "ETF Approved"}
    sent_input = {"fear_greed_index": 80, "social_media": "Very High Hype"}
    risk_input = {"current_positions": [], "proposed_trade": {"symbol": "BTCUSDT", "action": "BUY"}, "market_volatility": "Medium"}

    # Run them concurrently
    print(" >>> Analysts are thinking efficiently...")
    results = await asyncio.gather(
        tech_agent.process(tech_input),
        fund_agent.process(fund_input),
        sent_agent.process(sent_input),
        risk_agent.process(risk_input)
    )
    
    tech_report, fund_report, sent_report, risk_report = results
    
    print(" >>> Reports Received.")
    # (Optional: print one report to verify)
    # print(json.dumps(tech_report, indent=2, ensure_ascii=False))

    # 4. Step 3: Final Decision
    print("\n[Step 3] Decision Maker weighing the evidence...")
    
    decision_input = {
        "macro_plan": macro_strategy,
        "technical": tech_report,
        "fundamental": fund_report,
        "sentiment": sent_report,
        "risk": risk_report,
        "positions": [],
        "balance": {"USDT": 10000}
    }
    
    final_decision = await decision_agent.process(decision_input)
    
    print("\n" + "="*60)
    print("⚖️  FINAL COUNCIL DECISION")
    print("="*60)
    print(json.dumps(final_decision, indent=2, ensure_ascii=False))
    print("="*60)
    
    if final_decision.get("decision") in ["BUY", "SELL", "HOLD"]:
        print("\n✅ Decision Flow Simulation Successful!")
    else:
        print("\n❌ Decision Flow Failed or Ambiguous.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
