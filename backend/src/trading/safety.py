import yaml
import os
from typing import Dict, Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta

from src.database.operations import db
from src.utils.logger import logger

# Load Config
CONFIG_PATH = os.path.join(os.getcwd(), "config", "config.yaml")

class OrderParams(BaseModel):
    symbol: str
    side: str # BUY / SELL
    order_type: str # LIMIT / MARKET
    quantity: float
    price: Optional[float] = None
    notional: Optional[float] = None # Calculated value (price * quantity)

class SafetyGuard:
    """
    风控卫士 (The Shield)
    在订单发出前执行硬编码的安全检查。
    """
    
    def __init__(self):
        self.config = self._load_config()
        self.risk_config = self.config.get('risk', {})
        self.limits = {
            'max_daily_loss': self.risk_config.get('max_daily_loss', 0.05), # 5%
            'max_single_loss': self.risk_config.get('max_single_loss', 0.02), # 2% per trade intent (not slippage)
            'max_order_pct': 0.20, # Max 20% of account per order (Fat Finger)
            'daily_trade_limit': self.risk_config.get('daily_trade_limit', 20),
            'min_notional': 10.0, # Binance Min $10
        }
        logger.info(f"SafetyGuard initialized with limits: {self.limits}")

    def _load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def check_order(self, account_balance: float, order: OrderParams) -> bool:
        """
        综合安全检查
        :param account_balance: 当前账户总权益 (Equity)
        :param order: 拟发送的订单参数
        :return: True=Pass, False=Block
        """
        try:
            # 1. 基础合法性检查
            if order.quantity <= 0:
                logger.error(f"SAFETY: Invalid quantity {order.quantity}")
                return False
                
            # 计算预估名义价值
            estimated_price = order.price if order.price else 0 # Market order needs current price fetch externally, assuming caller passed notional or valid price
            # 如果是市价单且没传价格，这层检查很难精确。建议 Executor 传进来最近成交价
            notional = order.notional if order.notional else (order.quantity * estimated_price)
            
            if notional <= 0:
                 logger.warning(f"SAFETY: Cannot calculate notional value for {order.symbol}")
                 # Pass cautiously or block? Let's Block if undefined
                 return False

            # 2. 最小金额检查 (Dust Check)
            if notional < self.limits['min_notional']:
                logger.warning(f"SAFETY: Order value ${notional:.2f} below minimum ${self.limits['min_notional']}")
                return False

            # 3. 胖手指检查 (Fat Finger) - 单笔最大仓位
            max_order_val = account_balance * self.limits['max_order_pct']
            if notional > max_order_val:
                logger.error(f"SAFETY: Fat Finger detected! Order ${notional:.2f} > Limit ${max_order_val:.2f} (20% of Equity)")
                return False

            # 4. 每日亏损熔断 (Circuit Breaker)
            # 需要查当天已实现盈亏
            if self._is_circuit_broken(account_balance):
                logger.error("SAFETY: Daily loss limit reached. Trading halted.")
                return False

            # 5. 高频交易检查 (Frequency Check)
            if self._is_frequency_limit_reached():
                logger.error("SAFETY: Trading too frequently. Cooldown active.")
                return False

            logger.info(f"SAFETY: Order PASSED checks. {order.symbol} {order.side} ${notional:.2f}")
            return True

        except Exception as e:
            logger.error(f"SAFETY: Exception during check: {e}")
            return False # Fail safe

    def _is_circuit_broken(self, current_equity: float) -> bool:
        """
        检查今日是否亏损超标
        """
        # 简单逻辑: 比较当前权益 vs 昨日收盘权益 (或者初始权益)
        # 这里暂时用 Config 里的 initial_balance 近似，理想情况是读 DB 里的 daily_snapshot
        initial = self.config.get('trading', {}).get('initial_balance', 10000)
        drawdown = (initial - current_equity) / initial
        if drawdown > self.limits['max_daily_loss']:
            return True
        return False

    def _is_frequency_limit_reached(self) -> bool:
        """
        检查过去 1 小时的下单数量
        """
        # 从 DB 查询过去 1h 的 Trades 数量
        # count = db.get_recent_trade_count(minutes=60)
        # return count > self.limits['daily_trade_limit']
        return False # TODO: Implement DB query
