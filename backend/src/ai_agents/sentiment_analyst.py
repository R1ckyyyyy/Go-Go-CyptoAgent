from typing import Dict, Any
import json
from src.ai_agents.base_agent import BaseAgent, DecisionLayer
from src.ai_agents.communication import MessageType
from src.utils.logger import logger

class SentimentAnalystAgent(BaseAgent):
    """
    情绪分析AI (Sentiment Analyst)
    评估市场参与者的情绪和恐慌/贪婪程度。
    """
    
    SYSTEM_PROMPT = """
你是一个市场情绪分析师。

**职责:**
评估市场参与者的情绪和恐慌/贪婪程度。

**分析要点:**
- 新闻情绪
- 社交媒体热度
- 恐慌贪婪指数
- 市场极端情绪识别

**输出格式:**
{
  "overall_sentiment": "极度贪婪/贪婪/中性/恐惧/极度恐惧",
  "sentiment_score": 0-100,
  "contrarian_opportunity": true/false,
  "recommendation": "买入/卖出/观望",
  "reasoning": "情绪分析理由"
}
"""

    def __init__(self):
        super().__init__(
            agent_id="sentiment_analyst",
            agent_type="SENTIMENT_ANALYST",
            role_description="Market Sentiment Expert",
            layer=DecisionLayer.ANALYSIS
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input keys: news_data, social_media_data, fear_greed_index
        """
        logger.info("Sentiment Analyst processing...")
        
        user_content = json.dumps(input_data, indent=2)
        
        try:
            response_text = await self.call_llm(
                system_prompt=self.SYSTEM_PROMPT,
                user_content=user_content,
                temperature=0.5
            )
            
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                result = json.loads(response_text[start_idx:end_idx])
            else:
                raise ValueError("No JSON found")
            
            await self.log_decision(result, confidence=0.7) # 情绪分析通常不确定性较大
            return result
            
        except Exception as e:
            logger.error(f"Sentiment Analysis Failed: {e}")
            return {"error": str(e)}

    async def handle_message(self, message):
         await super().handle_message(message)
         if message.message_type == MessageType.TASK_ASSIGNMENT:
             result = await self.process(message.content)
             await self.communicate(message.sender, MessageType.ANALYSIS_REPORT, result)
