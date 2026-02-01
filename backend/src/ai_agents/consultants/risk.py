from typing import Dict, Any
import json
from src.ai_agents.base_agent import BaseAgent, DecisionLayer
from src.utils.logger import logger

class RiskConsultant(BaseAgent):
    """
    风险顾问 (Risk Consultant)
    
    职责:
    不预测涨跌，只计算数学概率和风险参数。
    回答 Coordinator 关于仓位管理、止损位置、盈亏比的问题。
    """
    
    SYSTEM_PROMPT = """
你是一个严格的风险控制顾问。你没有感情，只看数字。
Coordinator 会告诉你它想做什么（比如"我想买入BTC"），你需要给出风控建议。

**你的原则:**
1. 保本第一。
2. 单笔交易止损不超过总本金的 1-2%。
3. 盈亏比低于 1:2 的交易不建议执行。

**输入:**
计划的交易 (Coordinator Plan) + 账户状态 + 市场波动率 (Volatility)

**输出:**
风控参数建议。

**示例:**
Q: "我想在 43000 买入 BTC，止损放在哪里合适？仓位给多少？"
A: "基于当前的高波动率 (ATR=1500)，建议止损设在 41800 (前低支撑下方)。这距离入场点有 2.8% 的跌幅。为了将账户总风险控制在 1%，你最多只能使用 35% 的仓位（假设 10000U 本金，亏损额为 280U，即 2.8% * PositionSize = 100U -> PositionSize = 3571U）。"
"""

    def __init__(self):
        super().__init__(
            agent_id="risk_consultant",
            agent_type="CONSULTANT",
            role_description="Risk Management Expert",
            layer=DecisionLayer.ANALYSIS
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input keys: query, account_balance, positions, proposed_trade...
        """
        query = input_data.get("query", "")
        logger.info(f"Risk Consultant received query: {query}")
        
        user_content = json.dumps(input_data, indent=2)
        
        try:
            response_text = await self.call_llm(
                system_prompt=self.SYSTEM_PROMPT,
                user_content=user_content,
                temperature=0.1 # 风控必须严谨
            )
            return {"answer": response_text}
            
        except Exception as e:
            logger.error(f"Risk Consultant Error: {e}")
            return {"error": str(e)}
