import asyncio
import logging
from typing import Dict, Any, List
import time
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from src.ai_agents.macro_planner import MacroPlannerAgent
from src.ai_agents.technical_analyst import TechnicalAnalystAgent
from src.ai_agents.fundamental_analyst import FundamentalAnalystAgent
from src.ai_agents.sentiment_analyst import SentimentAnalystAgent
from src.ai_agents.risk_assessor import RiskAssessorAgent
from src.ai_agents.decision_maker import DecisionMakerAgent
from src.ai_agents.agent_manager import agent_manager
from src.utils.logger import logger

class WorkflowEngine:
    """
    AI工作流引擎
    负责编排整个决策流程
    """
    
    def __init__(self):
        self._init_agents()
    
    def _init_agents(self):
        """初始化所有Agent并注册"""
        self.macro_agent = MacroPlannerAgent()
        self.tech_agent = TechnicalAnalystAgent()
        self.fund_agent = FundamentalAnalystAgent()
        self.sent_agent = SentimentAnalystAgent()
        self.risk_agent = RiskAssessorAgent()
        self.decision_agent = DecisionMakerAgent()
        
        # 注册到管理器
        agent_manager.register_agent(self.macro_agent)
        agent_manager.register_agent(self.tech_agent)
        agent_manager.register_agent(self.fund_agent)
        agent_manager.register_agent(self.sent_agent)
        agent_manager.register_agent(self.risk_agent)
        agent_manager.register_agent(self.decision_agent)

    async def execute_workflow(self, market_snapshot: Dict, positions: List, news_data: Dict):
        """
        执行完整的一次决策循环
        """
        workflow_id = int(time.time())
        logger.info(f"Starting Workflow {workflow_id}")
        
        try:
            # Step 1: 宏观规划
            logger.info("=== Step 1: Macro Planning ===")
            macro_input = {
                "market_data": market_snapshot,
                "positions": positions
            }
            macro_plan = await self.macro_agent.process(macro_input)
            
            # Step 2: 并行分析
            logger.info("=== Step 2: Parallel Analysis ===")
            # 准备各分析师输入
            # 实际中可能需根据macro_plan分配的任务来裁剪输入
            
            tech_input = {
                "symbol": "BTCUSDT", # 示例，实际应遍历focus_symbols
                "kline_data": market_snapshot.get("klines"),
                "indicators": market_snapshot.get("indicators"),
                "current_price": market_snapshot.get("price")
            }
            
            fund_input = {
                "symbol": "BTCUSDT",
                "onchain_data": {}, # Mock
                "funding_rate": market_snapshot.get("funding_rate"),
                "news_summary": news_data
            }
            
            sent_input = {
                "news_data": news_data,
                "social_media_data": {}, # Mock
            }
            
            # 启动并发任务
            analysis_tasks = [
                self.tech_agent.process(tech_input),
                self.fund_agent.process(fund_input),
                self.sent_agent.process(sent_input)
            ]
            
            # 等待结果 (带超时)
            tech_res, fund_res, sent_res = await asyncio.wait_for(
                asyncio.gather(*analysis_tasks, return_exceptions=True),
                timeout=60 # 60秒超时
            )
            
            # 处理可能的异常
            tech_res = self._handle_result(tech_res, "Technical")
            fund_res = self._handle_result(fund_res, "Fundamental")
            sent_res = self._handle_result(sent_res, "Sentiment")
            
            # Step 2.5: 风险评估 (依赖于持仓和潜在意向，这里假设先评估当前持仓风险)
            # 更好的做法可能是决策层先生成草案，再过风控。
            # 但Prompt流程是: 并行调用4个分析AI(包含风控) -> 决策层。
            # 所以风控在这里是作为独立输入，评估整体风险环境。
            risk_input = {
                "current_positions": positions,
                "market_volatility": market_snapshot.get("volatility", "medium")
            }
            risk_res = await self.risk_agent.process(risk_input)
            
            # Step 3: 综合决策
            logger.info("=== Step 3: Final Decision ===")
            decision_input = {
                "macro_plan": macro_plan,
                "technical_analysis": tech_res,
                "fundamental_analysis": fund_res,
                "sentiment_analysis": sent_res,
                "risk_assessment": risk_res, # 传递给决策者参考
                "positions": positions,
                "balance": {"USDT": 10000} # Mock
            }
            
            final_decision = await self.decision_agent.process(decision_input)
            
            # Step 4: 执行 (通知/下单)
            logger.info(f"=== Workflow Completed. Decision: {final_decision.get('decision')} ===")
            return final_decision

        except asyncio.TimeoutError:
            logger.error("Workflow timed out during analysis phase")
            return {"error": "Timeout"}
        except Exception as e:
            logger.error("Workflow execution failed: {}", e)
            # logger.error(f"Workflow execution failed: {e}", exc_info=True) # Unsafe with loguru if e contains braces
            return {"error": str(e)}

    def _handle_result(self, res, name):
        if isinstance(res, Exception):
            logger.error(f"{name} Analysis failed: {res}")
            return {"error": str(res)}
        return res

# 简单的测试运行
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = WorkflowEngine()
    
    # Mock Data
    mock_market = {
        "price": 43000, 
        "klines": [], 
        "indicators": {"RSI": 60},
        "funding_rate": 0.01
    }
    mock_pos = []
    mock_news = "Bitcoin is rising."
    
    asyncio.run(engine.execute_workflow(mock_market, mock_pos, mock_news))
