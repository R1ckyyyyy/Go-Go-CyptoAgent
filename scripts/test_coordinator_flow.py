import sys
import os
import asyncio
import json
from dotenv import load_dotenv

# Path setup
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

# Load env variables (Robust)
root_env = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(root_env):
    load_dotenv(root_env)
    print(f"Loaded root .env from {root_env}")

backend_env = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
if os.path.exists(backend_env):
    load_dotenv(backend_env)
    print(f"Loaded backend .env from {backend_env}")

os.environ['LLM_PROVIDER'] = 'gemini'

from src.ai_agents.coordinator import CoordinatorAgent
from src.ai_agents.consultants.technical import TechnicalConsultant

async def main():
    print("\n--- 🧠 Testing Coordinator + Consultant Architecture ---")
    
    # 1. Initialize Agents
    print("\n[Init] Initializing Coordinator and Technical Consultant...")
    coordinator = CoordinatorAgent()
    tech_consultant = TechnicalConsultant()
    
    # 2. Register Consultant (In a real app, this might be auto-discovery)
    # Simulator: We manually bridge them or Mock the registry inside Coordinator
    # Since my Coordinator implementation currently just calls LLM and doesn't *actually* call the python method of consultant yet (MVP),
    # I will verify the Coordinator's *intent* to consult in its thought process.
    # OR better: I can inject the Consultant into the Coordinator if I modify Coordinator to support it.
    
    # Let's test them individually first, then the flow intention.
    
    # Test Consultant Response
    print("\n[Test 1] Asking Technical Consultant directly...")
    query = {"query": "BTC price dropped to 42000, is this a support level?", "market_snapshot": {"BTC": 42000}}
    tech_response = await tech_consultant.process(query)
    print(f" >>> Tech Answer: {tech_response.get('answer')}")
    
    # Test Coordinator Logic
    print("\n[Test 2] Triggering Coordinator with Event...")
    trigger_event = {
        "type": "PRICE_ALERT",
        "message": "BTC fell below 42800",
        "current_price": 42000
    }
    
    # Ideally, we pass the tech_response into the Coordinator's context to simulate "After consulting"
    # But for now, let's see if the Coordinator *asks* for it in "consultations" field.
    
    decision = await coordinator.process(trigger_event)
    print("\n >>> Coordinator Output:")
    print(json.dumps(decision, indent=2, ensure_ascii=False))
    
    # Check Result
    if "consultations" in decision:
        print("\n✅ Coordinator correctly identified need for consultation.")
    else:
        print("\n⚠️ Coordinator made a decision without consultation (might be intended based on prompt).")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
