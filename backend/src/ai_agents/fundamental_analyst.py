from typing import Dict, Any
import json
from src.ai_agents.base_agent import BaseAgent, DecisionLayer
from src.ai_agents.communication import MessageType
from src.utils.logger import logger

class FundamentalAnalystAgent(BaseAgent):
    """
    基本面分析AI (Fundamental Analyst)
    分析影响加密货币价值的基本面因素。
    """
    
    SYSTEM_PROMPT = """
你是一个加密货币基本面分析师。

**职责:**
分析影响加密货币价值的基本面因素。

**分析要点:**
- 链上数据(交易所流入流出、巨鲸动向)
- 市场情绪(资金费率、持仓量)
- 宏观经济(美联储政策、通胀数据)
- 项目动态(升级、合作)

**输出格式:**
{
  "symbol": "ETHUSDT",
  "fundamental_score": 0-100,
  "key_factors": [
    {
      "factor": "资金费率",
      "status": "正向/负向",
      "impact": "high/medium/low"
    }
  ],
  "recommendation": "买入/卖出/观望",
  "confidence": 0-1,
  "reasoning": "分析理由"
}
"""

    def __init__(self):
        super().__init__(
            agent_id="fundamental_analyst",
            agent_type="FUNDAMENTAL_ANALYST",
            role_description="Fundamental Analysis Expert",
            layer=DecisionLayer.ANALYSIS
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input keys: symbol, onchain_data, funding_rate, news_summary
        """
        symbol = input_data.get("symbol", "UNKNOWN")
        logger.info(f"Fundamental Analyst processing for {symbol}...")
        
        user_content = json.dumps(input_data, indent=2)
        
        try:
            response_text = await self.call_llm(
                system_prompt=self.SYSTEM_PROMPT,
                user_content=user_content,
                temperature=0.4
            )
            
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                result = json.loads(response_text[start_idx:end_idx])
            else:
                raise ValueError("No JSON found")
            
            await self.log_decision(result, confidence=result.get("confidence", 0.5))
            return result
            
        except Exception as e:
            logger.error(f"Fundamental Analysis Failed: {e}")
            return {"error": str(e)}
    
    async def handle_message(self, message):
         await super().handle_message(message)
         if message.message_type == MessageType.TASK_ASSIGNMENT:
             result = await self.process(message.content)
             await self.communicate(message.sender, MessageType.ANALYSIS_REPORT, result)
