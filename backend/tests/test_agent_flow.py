import pytest
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.ai_agents.base_agent import BaseAgent
from src.database.models import DecisionLayer
from src.utils.logger import logger

# Load env
load_dotenv()

class TestAgent(BaseAgent):
    """Simple concrete implementation for testing"""
    async def process(self, input_data: str):
        # Simple thinking process
        response = await self.call_llm(
            system_prompt="You are a helpful test agent. Reply briefly.",
            user_content=f"Hello, please echo this: {input_data}"
        )
        return {"response": response}

@pytest.mark.asyncio
async def test_agent_initialization():
    agent = TestAgent(
        agent_id="test_agent_01",
        agent_type="tester",
        role_description="A test agent",
        layer=DecisionLayer.ANALYSIS
    )
    assert agent.agent_id == "test_agent_01"
    assert agent.provider in ["gemini", "anthropic"]
    print(f"\n[Test] Agent initialized with provider: {agent.provider}")

@pytest.mark.asyncio
async def test_llm_connection():
    """Tests actual connection to LLM provider defined in .env"""
    agent = TestAgent(
        agent_id="test_agent_02",
        agent_type="tester",
        role_description="Connection tester",
        layer=DecisionLayer.ANALYSIS
    )
    
    auth_key = agent.gemini_key if agent.provider == "gemini" else agent.anthropic_key
    if not auth_key:
        pytest.skip(f"Skipping LLM test: No API key found for {agent.provider}")
        
    print(f"\n[Test] Testing LLM connection using {agent.provider}...")
    try:
        result = await agent.process("Test Ping")
        print(f"[Test] LLM Response: {result['response']}")
        assert len(result['response']) > 0
    except Exception as e:
        pytest.fail(f"LLM Connection failed: {str(e)}")

if __name__ == "__main__":
    # Allow running directly: python tests/test_agent_flow.py
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_llm_connection())
