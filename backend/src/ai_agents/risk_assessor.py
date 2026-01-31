from typing import Dict, Any
import json
from src.ai_agents.base_agent import BaseAgent, DecisionLayer
from src.ai_agents.communication import MessageType
from src.utils.logger import logger

class RiskAssessorAgent(BaseAgent):
    """
    风险评估AI (Risk Assessor)
    评估每个交易决策的风险并提供风险控制建议。
    """
    
    SYSTEM_PROMPT = """
你是一个风险管理专家。

**职责:**
评估每个交易决策的风险并提供风险控制建议。

**分析要点:**
- 当前持仓风险暴露
- 波动率风险
- 流动性风险
- 止损止盈位设置

**输出格式:**
{
  "risk_level": "低/中/高",
  "risk_score": 0-100,
  "position_size_recommendation": "仓位比例建议 (如 0.05)",
  "stop_loss": "建议止损价位",
  "take_profit": "建议止盈价位",
  "max_drawdown_warning": "最大回撤预警",
  "recommendation": "允许/拒绝/调整仓位",
  "reasoning": "风险评估理由"
}
"""

    def __init__(self):
        super().__init__(
            agent_id="risk_assessor",
            agent_type="RISK_ASSESSOR",
            role_description="Risk Management Expert",
            layer=DecisionLayer.ANALYSIS
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input keys: current_positions, proposed_trade (optional), market_volatility
        """
        logger.info("Risk Assessor processing...")
        
        user_content = json.dumps(input_data, indent=2)
        
        try:
            response_text = await self.call_llm(
                system_prompt=self.SYSTEM_PROMPT,
                user_content=user_content,
                temperature=0.2 # 风险控制需严谨
            )
            
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                result = json.loads(response_text[start_idx:end_idx])
            else:
                raise ValueError("No JSON found")
            
            await self.log_decision(result, confidence=0.9)
            return result
            
        except Exception as e:
            logger.error(f"Risk Assessment Failed: {e}")
            return {"error": str(e)}

    async def handle_message(self, message):
         await super().handle_message(message)
         if message.message_type == MessageType.TASK_ASSIGNMENT:
             result = await self.process(message.content)
             await self.communicate(message.sender, MessageType.ANALYSIS_REPORT, result)
