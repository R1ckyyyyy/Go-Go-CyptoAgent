from typing import Dict, Any
import json
from src.ai_agents.base_agent import BaseAgent, DecisionLayer
from src.utils.logger import logger

class FundamentalConsultant(BaseAgent):
    """
    基本面顾问 (Fundamental Consultant)
    
    整合了原本的 FundamentalAnalyst (基本面) 和 SentimentAnalyst (情绪)。
    
    职责:
    回答 Coordinator 关于大局、链上数据、新闻事件及市场情绪的问题。
    """
    
    SYSTEM_PROMPT = """
你是一个资深加密货币基本面与情绪顾问。
Coordinator（协调AI）会向你咨询关于市场宏观环境、项目基本面或市场情绪的问题。

**你的数据源包括:**
1. 宏观经济 (美联储政策, 通胀)
2. 链上数据 (资金流向, 大额转账)
3. 市场情绪 (恐慌贪婪指数, 社交媒体热度)
4. 项目动态 (升级, 合作)

**输入:**
Coordinator 的具体问题 (Query) + 相关数据 (Context: news, onchain_data, fear_greed_index 等)

**输出:**
客观、有洞察力的分析解答。不要做交易决策，只提供背景信息和环境判断。

**示例:**
Q: "当前市场情绪如何？是否过热？"
A: "当前恐慌贪婪指数达到 82 (极度贪婪)。社交媒体上关于 BTC 的讨论热度创 3 个月新高，且散户做多情绪高涨。资金费率已升至 0.05%，表明杠杆过热，存在去杠杆（回调）风险。"

Q: "ETH 坎昆升级对价格有什么潜在影响？"
A: "坎昆升级将显著降低 L2 Gas 费用，从长远看利好 ETH 生态基本面。但目前市场已部分定价（Priced-in），短期内需警惕'利好兑现即利空'的抛压。"
"""

    def __init__(self):
        super().__init__(
            agent_id="fund_consultant",
            agent_type="CONSULTANT",
            role_description="Fundamental & Sentiment Expert",
            layer=DecisionLayer.ANALYSIS
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input keys: query, news_data, onchain_data, fear_greed_index...
        """
        query = input_data.get("query", "")
        logger.info(f"Fundamental Consultant received query: {query}")
        
        user_content = json.dumps(input_data, indent=2)
        
        try:
            response_text = await self.call_llm(
                system_prompt=self.SYSTEM_PROMPT,
                user_content=user_content,
                temperature=0.3 # 基本面分析需要一定的发散性但保持客观
            )
            return {"answer": response_text}
            
        except Exception as e:
            logger.error(f"Fundamental Consultant Error: {e}")
            return {"error": str(e)}
