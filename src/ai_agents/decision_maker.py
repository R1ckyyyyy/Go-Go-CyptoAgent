from typing import Dict, Any, List
import json
from src.ai_agents.base_agent import BaseAgent, DecisionLayer
from src.ai_agents.communication import MessageType
from src.utils.logger import logger

class DecisionMakerAgent(BaseAgent):
    """
    决策层AI (Decision Maker)
    汇总所有分析结果并做出交易决策。
    """
    
    SYSTEM_PROMPT_TEMPLATE = """
你是最终决策者，负责综合所有分析师的建议并做出交易决策。

**职责:**
1. 接收并理解所有分析AI的报告
2. 识别分析意见的一致性和分歧
3. 根据当前市场环境调整决策权重
4. 做出最终交易决策(买入/卖出/持有)
5. 确定具体的交易参数(数量、价格、止损止盈)

**当前市场环境权重配置:**
{weight_config}

**输出格式:**
{
  "decision": "BUY/SELL/HOLD",
  "symbol": "BTCUSDT",
  "action_type": "MARKET/LIMIT",
  "quantity": 0.05,
  "target_price": 45000,
  "stop_loss": 43000,
  "take_profit": 48000,
  "confidence": 0.85,
  "consensus_level": "一致/分歧/强烈分歧",
  "reasoning": "综合决策理由...",
  "dissenting_views": "分歧观点(如果有)"
}

**决策原则:**
1. 风险控制优先 - 如果风险评估为"高",则拒绝交易
2. 一致性优先 - 如果3个以上分析AI意见一致,增加置信度
3. 仓位管理 - 单个币种不超过总资产30%
4. 止损必设 - 每笔交易必须设置止损
5. 分批建仓 - 大额交易分批执行
"""

    def __init__(self):
        super().__init__(
            agent_id="decision_maker",
            agent_type="DECISION_MAKER",
            role_description="Final Decision Maker",
            layer=DecisionLayer.EXECUTION
        )
        self.current_market_env = "UNKNOWN"

    def calculate_weights(self, market_env: str) -> str:
        """根据市场环境计算权重配置字符串"""
        self.current_market_env = market_env
        if market_env == "牛市":
            return "技术分析 40%, 基本面 30%, 情绪 20%, 风险 10%"
        elif market_env == "熊市":
            return "风险评估 40%, 技术分析 30%, 基本面 20%, 情绪 10%"
        elif "震荡" in market_env:
            return "技术分析 35%, 风险评估 30%, 基本面 25%, 情绪 10%"
        else:
            return "均衡: 技术 25%, 基本面 25%, 情绪 25%, 风险 25%"

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input keys: macro_plan, technical, fundamental, sentiment, risk, positions, balance
        """
        logger.info("Decision Maker processing...")
        
        # 提取宏观环境以设定权重
        macro = input_data.get("macro_plan", {})
        market_env = macro.get("market_environment", "震荡市") # 默认震荡
        weight_config = self.calculate_weights(market_env)
        
        system_prompt = self.SYSTEM_PROMPT_TEMPLATE.replace("{weight_config}", weight_config)
        user_content = json.dumps(input_data, indent=2)
        
        try:
            response_text = await self.call_llm(
                system_prompt=system_prompt,
                user_content=user_content,
                temperature=0.2
            )
            
            # 调试日志：记录原始响应
            logger.debug(f"Raw Decision output: {response_text[:500]}...")

            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                json_str = response_text[start_idx:end_idx]
                decision = json.loads(json_str)
            else:
                logger.error(f"Invalid JSON format in response: {response_text}")
                raise ValueError("No valid JSON found in response")
            
            # 验证决策 (简单逻辑验证)
            if not self.validate_decision(decision, input_data.get("risk", {})):
                 logger.warning("Decision validation failed, overriding to HOLD")
                 decision["decision"] = "HOLD"
                 decision["reasoning"] = "Validation failed: Risk too high or stop loss missing"

            await self.log_decision(decision, confidence=decision.get("confidence", 0.0))
            
            # 广播最终决策
            await self.communicate("all", MessageType.DECISION_OUTPUT, decision)
            
            return decision
            
        except Exception as e:
            logger.error(f"Decision Making Failed: {e}")
            return {"error": str(e)}

    def validate_decision(self, decision: Dict, risk_assessment: Dict) -> bool:
        """
        验证决策安全性和合规性
        """
        # 规则1: 如果决定交易，必须有止损
        if decision.get("decision") in ["BUY", "SELL"]:
            if not decision.get("stop_loss"):
                return False
        
        # 规则2: 如果风险评估拒绝，则不能交易 (除非人工覆盖，这里暂只考虑自动)
        risk_rec = risk_assessment.get("recommendation", "")
        if "拒绝" in risk_rec and decision.get("decision") != "HOLD":
            return False
            
        return True

    async def handle_message(self, message):
         # 决策层通常由工作流引擎触发process，或者收集齐所有报告后触发
         # 这里暂不自动触发，依赖WorkflowEngine调度
         await super().handle_message(message)
