from typing import Dict, Any
import json
from src.ai_agents.base_agent import BaseAgent, DecisionLayer
from src.ai_agents.communication import MessageType
from src.utils.logger import logger

class TechnicalAnalystAgent(BaseAgent):
    """
    技术分析AI (Technical Analyst)
    仅基于技术指标和图表形态进行分析。
    """
    
    SYSTEM_PROMPT = """
你是一个专业的加密货币技术分析师。

**职责:**
仅基于技术指标和图表形态进行分析，不考虑基本面。

**分析要点:**
- K线形态(头肩顶、双底、三角形等)
- 技术指标(MA, EMA, RSI, MACD, 布林带)
- 支撑位和阻力位
- 成交量配合
- 趋势强度

**输出格式:**
{
  "symbol": "BTCUSDT",
  "trend": "上涨/下跌/震荡",
  "strength": 0-100,
  "support_levels": [42000, 41500],
  "resistance_levels": [43000, 43500],
  "signals": [
    {
      "indicator": "RSI",
      "value": 75,
      "signal": "超买",
      "weight": 0.8
    }
  ],
  "recommendation": "买入/卖出/观望",
  "confidence": 0-1,
  "reasoning": "详细分析理由"
}
"""

    def __init__(self):
        super().__init__(
            agent_id="technical_analyst",
            agent_type="TECHNICAL_ANALYST",
            role_description="Technical Analysis Specialist",
            layer=DecisionLayer.ANALYSIS
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input keys: symbol, kline_data, indicators, current_price
        """
        symbol = input_data.get("symbol", "UNKNOWN")
        logger.info(f"Technical Analyst processing for {symbol}...")
        
        user_content = json.dumps(input_data, indent=2)
        
        try:
            response_text = await self.call_llm(
                system_prompt=self.SYSTEM_PROMPT,
                user_content=user_content,
                temperature=0.3 # 技术分析需要更理性、确定性
            )
            
            # Extract JSON
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                result = json.loads(response_text[start_idx:end_idx])
            else:
                raise ValueError("No JSON found")
                
            # Log decision
            await self.log_decision(result, confidence=result.get("confidence", 0.5))
            
            # If triggered by task assignment, maybe reply? 
            # (Logic handled outside or via handle_message usually, but here is pure process)
            
            return result
            
        except Exception as e:
            logger.error(f"Technical Analysis Failed: {e}")
            return {"error": str(e)}

    async def handle_message(self, message):
        await super().handle_message(message)
        if message.message_type == MessageType.TASK_ASSIGNMENT:
            # 假设message.content 包含数据或数据引用
            # 实际中可能需要根据task去Database拉数据
            # 这里简化为直接处理传递过来的数据
            result = await self.process(message.content)
            
            # 回复报告
            await self.communicate(
                to_agent=message.sender,
                message_type=MessageType.ANALYSIS_REPORT,
                content=result
            )
