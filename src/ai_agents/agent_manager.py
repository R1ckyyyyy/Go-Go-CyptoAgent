from typing import Dict, List, Optional
from src.ai_agents.base_agent import BaseAgent
from src.utils.logger import logger

class AgentManager:
    """代理管理器"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}

    def register_agent(self, agent: BaseAgent):
        """注册代理"""
        if agent.agent_id in self.agents:
            logger.warning(f"Agent {agent.agent_id} already registered. Overwriting.")
        self.agents[agent.agent_id] = agent
        logger.info(f"Agent registered: {agent.agent_id} ({agent.agent_type})")

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """获取代理实例"""
        return self.agents.get(agent_id)

    def get_agents_by_type(self, agent_type: str) -> List[BaseAgent]:
        """按类型获取代理"""
        return [a for a in self.agents.values() if a.agent_type == agent_type]

    def list_agents(self) -> List[str]:
        """列出所有代理ID"""
        return list(self.agents.keys())
    
    async def shutdown(self):
        """关闭所有代理相关资源 (如需要)"""
        pass

# 全局Manager单例
agent_manager = AgentManager()
