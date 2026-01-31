from typing import Dict, Any, List
import json
import asyncio
from datetime import datetime

from src.ai_agents.base_agent import BaseAgent
from src.ai_agents.communication import MessageType
from src.database.models import DecisionLayer
from src.utils.logger import logger

class MacroPlannerAgent(BaseAgent):
    """
    宏观规划AI (Macro Planner)
    负责理解市场整体状况，制定高层策略，并将任务分配给下层分析AI。
    """

    SYSTEM_PROMPT = """
你是一个加密货币交易的宏观策略规划师。

**职责:**
1. 分析当前市场整体环境(牛市/熊市/震荡)
2. 识别当前主要交易机会
3. 将分析任务分配给专业分析AI团队
4. 汇总分析结果制定宏观策略

**可用数据源:**
- 市场数据: BTC/ETH/SOL的价格、成交量、资金费率
- 当前持仓: 实时仓位信息
- 历史记忆: 过往决策和市场表现

**输出格式:**
以JSON格式输出:
{
  "market_environment": "牛市/熊市/震荡市",
  "market_sentiment": "贪婪/恐惧/中性",
  "focus_symbols": ["BTC", "ETH", "SOL"],
  "strategy_direction": "激进/稳健/保守",
  "tasks_to_assign": [
    {
      "assign_to": "technical_analyst",
      "task": "分析BTC 4小时图形态",
      "priority": "high"
    },
    ...
  ],
  "reasoning": "决策理由"
}

**约束条件:**
- 只交易BTC, ETH, SOL
- 不追涨杀跌，等待明确信号
- 风险控制优先
"""

    def __init__(self):
        super().__init__(
            agent_id="macro_planner",
            agent_type="MACRO_PLANNER",
            role_description="Macro Strategy Planner",
            layer=DecisionLayer.MACRO
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理输入数据并制定宏观策略
        input_data 应包含: market_data, positions, memory_context
        """
        logger.info("Macro Planner started processing...")
        
        # 构建用户提示词
        user_content = self._build_user_content(input_data)
        
        # 调用通用LLM接口
        response_text = await self.call_llm(
            system_prompt=self.SYSTEM_PROMPT,
            user_content=user_content,
            temperature=0.7
        )
        
        # 解析JSON输出
        try:
            # 尝试找到JSON部分 (Claude有时会输出多余文本)
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                strategy_plan = json.loads(json_str)
            else:
                logger.error("Failed to find JSON in Macro Planner response")
                raise ValueError("Invalid JSON response")
                
            logger.info(f"Macro Strategy: {strategy_plan.get('strategy_direction')} - {strategy_plan.get('market_environment')}")
            
            # 记录决策
            await self.log_decision(strategy_plan, confidence=0.9) # 宏观层通常较为主观，置信度仅供参考
            
            # 分配任务
            await self.assign_tasks(strategy_plan.get("tasks_to_assign", []))
            
            return strategy_plan
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON Parsing Error: {e}\nResponse: {response_text}")
            return {"error": "JSON parse error", "raw_response": response_text}
        except Exception as e:
            logger.error(f"Macro Process Error: {e}")
            return {"error": str(e)}

    def _build_user_content(self, data: Dict[str, Any]) -> str:
        """构建详细的用户提示内容"""
        market_stats = data.get("market_data", {})
        positions = data.get("positions", [])
        
        content = f"Current Time: {datetime.now().isoformat()}\n\n"
        
        content += "== Market Data ==\n"
        content += json.dumps(market_stats, indent=2)
        content += "\n\n"
        
        content += "== Current Positions ==\n"
        content += json.dumps(positions, indent=2)
        content += "\n\n"
        
        # 可以在此添加更多上下文，如新闻摘要等
        
        return content

    async def assign_tasks(self, tasks: List[Dict]):
        """根据策略分配任务给分析AI"""
        for task_info in tasks:
            target_agent = task_info.get("assign_to")
            if target_agent:
                logger.info(f"Assigning task to {target_agent}: {task_info.get('task')}")
                await self.communicate(
                    to_agent=target_agent,
                    message_type=MessageType.TASK_ASSIGNMENT,
                    content=task_info
                )

    async def plan_strategy(self, market_data: Dict, positions: List):
        """便携调用入口"""
        return await self.process({"market_data": market_data, "positions": positions})
