from typing import Dict, Any, List, Optional
import json
import asyncio
from datetime import datetime
import os

from src.ai_agents.base_agent import BaseAgent, DecisionLayer
from src.ai_agents.communication import MessageType
from src.database.models import CoordinatorTrigger, TriggerType, TriggerStatus, AIDecision
from src.database.operations import db
from src.utils.logger import logger
from src.api.binance_api import BinanceConnector
from src.api.paper_connector import PaperTradingConnector
from src.trading.executor import TradeExecutor

class CoordinatorAgent(BaseAgent):
    """
    协调AI (Coordinator AI) - 新架构的核心大脑
    
    职责:
    1. 目标管理 (Profit + Risk Control)
    2. 上下文持有 (Context Holder)
    3. 动态调度 (Dynamic Dispatcher)
    4. 自驱动触发 (Self-Triggering)
    """

    SYSTEM_PROMPT = """
你是一个高级加密货币交易协调员(Coordinator)。你是整个系统的核心大脑。

**你的目标:**
1. **盈利**: 在控制风险的前提下捕捉市场机会。
2. **风控**: 永远将本金安全放在第一位。

**你的能力:**
1. **感知**: 你可以直接获取市场价格、账户持仓。
2. **咨询**: 你拥有一支专家顾问团队（技术、基本面、风控），你可以随时向他们提问。
3. **决策**: 你是唯一的决策者。顾问只提供建议，不负责决策。
4. **记忆**: 你拥有完整的上下文记忆，知道之前的计划。
5. **规划**: 你可以设置"触发器"(Trigger)，让系统在特定价格或时间再次唤醒你。

**工作流程:**
收到触发事件 -> 分析现状 -> (按需咨询顾问) -> 综合思考 -> 做出行动 (交易/调整/设置新触发器)

**输出格式:**
你的思考过程必须清晰，最终输出一个JSON Action。
{
  "thought_process": "收到BTC价格提醒。当前65000。技术顾问认为是牛市回调。风控计算允许加仓。决定买入。",
  "consultations": [
    {"consultant": "technical", "query": "BTC 1小时级别趋势如何？支撑位在哪里？"}
  ],
  "action": {
    "type": "TRADE",  // 或 "SET_TRIGGER", "WAIT", "NOTIFY_USER"
    "params": {
      "symbol": "BTCUSDT",
      "side": "BUY",
      "quantity": 0.1,
      "stop_loss": 64000
    }
  },
  "next_triggers": [
    {
      "type": "PRICE_LEVEL",
      "condition": {"symbol": "BTCUSDT", "operator": "LTE", "value": 64000},
      "description": "止损触发"
    }
  ]
}
"""

    def __init__(self):
        super().__init__(
            agent_id="coordinator",
            agent_type="COORDINATOR",
            role_description="Core System Brain",
            layer=DecisionLayer.EXECUTION
        )
        self.consultants = {} # 注册的顾问列表
        self.executor = TradeExecutor() # Initialize Execution Hand
        
        # 初始化交易所连接器
        try:
            real_connector = BinanceConnector(use_testnet=True) # 默认 Testnet，可配
            
            # 检查是否开启模拟交易
            if os.getenv("PAPER_TRADING", "true").lower() == "true":
                logger.info("🟢 enabling PAPER TRADING mode")
                self.connector = PaperTradingConnector(real_connector)
            else:
                logger.warning("🔴 enabling REAL TRADING mode")
                self.connector = real_connector
                
        except Exception as e:
            logger.error(f"Failed to init BinanceConnector: {e}")
            self.connector = None
        
    def register_consultant(self, name: str, agent_instance: BaseAgent):
        """注册顾问"""
        self.consultants[name] = agent_instance
        logger.info(f"Consultant registered: {name}")

    async def process(self, input_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理输入事件 (Trigger Event / New Data)
        """
        logger.info(f"Coordinator activated by event: {input_event}")
        
        # [THOUGHT STREAM] Notify Start
        await self.communicate("all", MessageType.STATUS_UPDATE, {
            "status": "THINKING",
            "trigger": input_event.get("type", "UNKNOWN"),
            "reason": input_event.get("reason", "Manual Analysis"),
            "msg": f"Received event. Analyzing market data..."
        })
        
        # 1. 构建上下文 (Context)
        context = await self._build_context(input_event)
        
        # [THOUGHT STREAM] Notify Context
        await self.communicate("all", MessageType.DATA_RESPONSE, {
            "msg": f"Context Loaded. Market Price: {context['market_snapshot'].get('BTC', 'N/A')}",
            "data_snapshot": context['market_snapshot']
        })
        
        # 2. 思考循环 (Thinking Loop)
        response = await self.call_llm(
            system_prompt=self.SYSTEM_PROMPT,
            user_content=json.dumps(context, indent=2),
            temperature=0.1
        )
        
        # 3. 解析与执行
        try:
            result = self._parse_json(response)
            
            # [THOUGHT STREAM] Notify Thought Process (Extract from result)
            thought = result.get("thought_process", "No thought process returned.")
            await self.communicate("all", MessageType.ANALYSIS_REPORT, {
                "thought_process": thought,
                "msg": f"🧠 Strategy: {thought[:100]}..." 
            })

            # Notify Consultations (Mock for now, just showing intent)
            consultations = result.get("consultations", [])
            if consultations:
                 for c in consultations:
                      await self.communicate("all", MessageType.DATA_REQUEST, {
                          "target": c.get("consultant"),
                          "query": c.get("query"),
                          "msg": f"Consulting {c.get('consultant')}..."
                      })

            await self.communicate("all", MessageType.ACTION_REQUEST, result)

            # --- [ENHANCED LOGGING] Save Full Context to DB ---
            # Map Context -> Input Data
            # Map Result -> Output Recommendation
            decision_entry = {
                "decision_type": result.get("action", {}).get("type", "Review"),
                "layer": DecisionLayer.EXECUTION,
                "input_data": context,  # Save the full context including market snapshot
                "output_recommendation": result, # Save the full LLM output (thoughts + action)
                "confidence": 0.9
            }
            await self.log_decision(decision_entry, confidence=0.9)
            
            await self._handle_action(result.get("action"))
            await self._set_triggers(result.get("next_triggers", []))
            
            return result
            
        except Exception as e:
            logger.error(f"Coordinator process error: {e}")
            logger.error(f"Raw Response: {response}") # Log raw response for debugging
            
            # [THOUGHT STREAM] Notify Error
            await self.communicate("all", MessageType.ERROR_REPORT, {
                "error": str(e),
                "msg": "Crashed during thought process."
            })
            return {"error": str(e), "raw_response": response}

    def _parse_json(self, text: str) -> Dict:
        # Strip markdown code blocks if present
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                raise
        raise ValueError("Invalid JSON: No JSON object found")

    async def _build_context(self, event: Dict) -> Dict:
        """构建包含市场数据、持仓、记忆的完整上下文"""
        # 1. 获取基础数据 (Real Data)
        market_price = 0.0
        positions = []
        
        if self.connector:
            try:
                # 获取 BTC 价格
                ticker = self.connector.get_ticker("BTCUSDT")
                market_price = ticker.get('price', 0.0)
                
                # 获取持仓
                positions = self.connector.get_current_positions()
            except Exception as e:
                logger.error(f"Error fetching real data: {e}")
                
        # Fallback for offline testing
        if market_price == 0:
            market_price = event.get('current_price', 43000)

        # 2. 获取记忆与触发器状态
        memories = [m.content for m in db.get_recent_memories(limit=5)]
        active_triggers = [
            f"{t.description} ({t.condition_data})" 
            for t in db.get_active_triggers()
        ]
        
        context = {
            "timestamp": datetime.now().isoformat(),
            "trigger_event": event,
            "market_snapshot": {"BTC": market_price},
            "active_triggers": active_triggers,
            "recent_memories": memories,
            "positions": positions
        }
        return context

    async def _handle_action(self, action: Dict):
        """执行行动"""
        if not action: return
        action_type = action.get("type")
        logger.info(f"Executing Action: {action_type} - {action.get('params')}")
        
        # 1. Log decision is now handled in process()
        
        # 2. Execute via TradeExecutor
        if action_type == "TRADE":
            mock_decision = AIDecision(
                decision_type="TRADE",
                output_recommendation=action.get("params", {}),
                confidence=0.9
            )
            
            result = await self.executor.execute_decision(mock_decision)
            if result.success:
                logger.info(f"✅ Trade Executed: {result.message}")
            else:
                logger.warning(f"❌ Trade Blocked/Failed: {result.message}")
                
        elif action_type == "NOTIFY_USER":
            pass

    async def _set_triggers(self, triggers: List[Dict]):
        """设置新的触发器"""
        for t in triggers:
            trigger_data = {
                "description": t.get("description", "Auto Trigger"),
                "trigger_type": t.get("type", "PRICE_LEVEL"),
                "condition_data": t.get("condition", {}),
                "status": "ACTIVE"
            }
            logger.info(f"Setting Trigger in DB: {trigger_data}")
            db.add_trigger(trigger_data)
