from typing import Dict, Any
import json
from src.ai_agents.base_agent import BaseAgent, DecisionLayer
from src.utils.logger import logger

class TechnicalConsultant(BaseAgent):
    """
    技术顾问 (Technical Consultant)
    
    角色变更:
    - 旧: 主动分析全场，输出买卖建议。
    - 新: 被动响应 Coordinator 的具体咨询 (Query-Response)。
    """
    
    SYSTEM_PROMPT = """
你是一个资深加密货币技术顾问。
Coordinator（协调AI）会向你咨询具体的技术问题，你只需要回答问题本身，不要做最终交易决策。

**输入:**
Coordinator 的具体问题 (Query) + 相关市场数据 (Context)

**输出:**
客观、专业的技术解答。

**示例:**
Q: "BTC 1小时级别趋势如何？"
A: "1小时级别RSI为72（超买），价格触及布林带上轨，呈现回调需求。支撑位在42500。"
"""

    def __init__(self):
        super().__init__(
            agent_id="tech_consultant",
            agent_type="CONSULTANT",
            role_description="Technical Expert",
            layer=DecisionLayer.ANALYSIS
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input keys: query, market_snapshot
        """
        query = input_data.get("query", "")
        logger.info(f"Technical Consultant received query: {query}")
        
        user_content = json.dumps(input_data, indent=2)
        
        try:
            response_text = await self.call_llm(
                system_prompt=self.SYSTEM_PROMPT,
                user_content=user_content,
                temperature=0.2
            )
            return {"answer": response_text}
            
        except Exception as e:
            logger.error(f"Technical Consultant Error: {e}")
            return {"error": str(e)}
