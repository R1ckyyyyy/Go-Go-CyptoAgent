import asyncio
import os
from src.ai_agents.base_agent import BaseAgent
from src.ai_agents.communication import MessageType
from src.database.models import DecisionLayer
from src.utils.logger import logger

# 简单的Mock实现用于演示
class MockMacroPlanner(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="macro_planner", 
            agent_type="MACRO", 
            role_description="Macro Planner",
            layer=DecisionLayer.MACRO
        )
    
    async def process(self, input_data):
        logger.info(f"Macro Planner processing: {input_data}")
        # 模拟思考
        await asyncio.sleep(0.1)
        # 发送任务给分析师
        await self.communicate(
            to_agent="tech_analyst",
            message_type=MessageType.TASK_ASSIGNMENT,
            content={"task": "Analyze BTC"}
        )
        return {"strategy": "HOLD"}

class MockTechAnalyst(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="tech_analyst", 
            agent_type="ANALYST", 
            role_description="Technical Analyst",
            layer=DecisionLayer.ANALYSIS
        )
        
    async def process(self, input_data):
        return {}

    # 重写handle_message以演示接收
    async def handle_message(self, message):
        await super().handle_message(message)
        if message.message_type == MessageType.TASK_ASSIGNMENT:
            logger.info("Tech Analyst received task, starting analysis...")
            # 模拟回复
            await self.communicate(
                to_agent=message.sender,
                message_type=MessageType.ANALYSIS_REPORT,
                content={"result": "Bullish"}
            )

async def main():
    # 初始化
    planner = MockMacroPlanner()
    analyst = MockTechAnalyst()
    
    # 模拟流程
    logger.info("--- Starting Demo ---")
    await planner.process({"market_data": "raw"})
    await asyncio.sleep(0.5) # 等待异步消息处理
    logger.info("--- Demo Finished ---")

if __name__ == "__main__":
    # 确保有API KEY或 mock
    asyncio.run(main())
