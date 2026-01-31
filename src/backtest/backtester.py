import pandas as pd
from typing import Dict, List, Callable, Any
from datetime import datetime
import asyncio
from src.execution.trade_executor import TradeExecutor
from src.backtest.performance_analyzer import PerformanceAnalyzer
from src.utils.logger import logger
from src.execution.position_manager import PositionManager

class Backtester:
    """
    回测引擎
    """
    def __init__(self, initial_balance: float = 10000.0, strategy_func: Callable = None):
        """
        :param strategy_func: async function(market_snapshot, positions) -> decision_dict
        """
        self.initial_balance = initial_balance
        self.strategy_func = strategy_func
        
        # 初始化组件 (全模拟模式)
        self.trade_executor = TradeExecutor(mode="simulated")
        # Reset balance
        self.trade_executor.account_manager.simulated_balance = {"USDT": initial_balance}
        # Clear positions (in DB, user might need to ensure clean DB for backtest)
        # Note: For strict backtest, we should use a temporary in-memory DB or similar.
        # Here we assume the "simulated" DB is acceptable for usage.
        
        self.analyzer = PerformanceAnalyzer(initial_balance)
        self.data_feed = [] # List of (timestamp, market_snapshot)

    def load_data(self, data: List[Dict]):
        """
        data format: [{"timestamp":..., "symbol": "BTCUSDT", "price":..., "indicators":...}, ...]
        Assume sorted by time.
        """
        self.data_feed = data

    async def run(self):
        logger.info(f"Starting Backtest with {len(self.data_feed)} data points...")
        
        for i, tick in enumerate(self.data_feed):
            timestamp = tick.get("timestamp")
            
            # 1. Update Market Price in Simulated Environment
            # Since PositionManager (Simulated) usually checks API for price valuation,
            # we need to mock or inject the current price into it.
            # We can monkeypatch or injection. A cleaner way for the future is PriceService.
            # Here: Mock the api.get_ticker inside executor.position_manager
            
            current_price = tick.get("price")
            symbol = tick.get("symbol", "BTCUSDT") # Support single symbol backtest for now
            
            # Temporary mock for this tick
            class MockTickerAPI:
                def get_ticker(self, s):
                    return {"symbol": s, "price": current_price}
            
            # Patching both executor's pm and local scope if needed
            self.trade_executor.position_manager.impl.api = MockTickerAPI() # Patch simulated pm
            self.trade_executor.api = MockTickerAPI() # Patch executor (if it checks price)

            # 2. Get Strategy Decision
            decision = None
            if self.strategy_func:
                positions = self.trade_executor.position_manager.get_positions()
                decision = await self.strategy_func(tick, positions)
            
            # 3. Execute Decision
            if decision:
                # Enforce current price for LIMIT comparison or MARKET execution
                # Logic inside executor handles this, but for LIMIT orders in backtest
                # we need a matching engine. Current Executor only supports immediate execution sim.
                # So we assume "Immediate Fill" at current price for MARKET, or check price for LIMIT.
                
                # For simplified backtest, we treat decision as "Action to take NOW"
                result = self.trade_executor.execute_decision(decision)
                
                if result.get("status") == "executed":
                    self.analyzer.record_trade(result)
            
            # 4. Record Equity
            summary = self.trade_executor.position_manager.get_summary()
            total_equity = summary["account_summary"]["total_balance"]
            self.analyzer.record_equity(timestamp, total_equity)
            
            if i % 10 == 0:
                logger.debug(f"Progress: {i}/{len(self.data_feed)} Equity: {total_equity}")

        logger.info("Backtest completed.")
        return self.analyzer.generate_report()
