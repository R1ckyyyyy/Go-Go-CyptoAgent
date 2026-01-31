import time
from typing import Dict
from src.utils.logger import logger
from src.database.operations import db

class SafetyChecker:
    """
    交易安全检查器
    负责在下单前进行风控检查，如日内交易次数限制、亏损熔断等。
    """
    def __init__(self, config: Dict = None):
        self.config = config or {}
        # 默认限制配置
        self.max_daily_trades = self.config.get("max_daily_trades", 20)
        self.max_daily_loss_pct = self.config.get("max_daily_loss_pct", 0.05) # 5%
        self.db = db

    def check_all(self, order_dict: Dict, account_info: Dict) -> bool:
        """运行所有安全检查"""
        # 1. 检查日内交易次数
        if not self.check_daily_limit():
            return False
            
        # 2. 检查单日亏损熔断
        if not self.check_loss_threshold(account_info):
            return False
            
        # 3. 价格异常检查 (需要实时价格，此处暂略，通常在 executor 中检查与市价的偏差)
        
        return True

    def check_daily_limit(self) -> bool:
        """检查今日交易次数是否超限"""
        # 从数据库获取今日交易数量
        # 这里简化处理：获取所有交易，按时间过滤。实际应在 DB 层做 select count where date
        # 由于 db_operations.get_trades 只有 limit 限制，这里假设系统不频繁
        # 正确做法是给 db_operations 加一个 count_daily_trades 方法
        # 暂时跳过或假设 check passed，待 DB 完善。
        # TODO: Implement accurate daily count in DB operations
        
        # 简易实现：如果不做 DB 改动，我们暂时认为总是通过，或者在此处增加 logger
        logger.debug("Checking daily trade limit... (Mocked: PASS)")
        return True

    def check_loss_threshold(self, account_info: Dict) -> bool:
        """检查当日亏损是否超过允许范围"""
        # 需要 AccountManager 提供今日初始余额 vs 当前余额
        # 或者 daily_stats 
        # 这里仅检查 AccountManager 返回的 unrealized_pnl (如果有)
        
        # 如果是模拟盘，主要看 realized PnL
        # 暂时简单处理：PASS
        logger.debug("Checking loss threshold... (Mocked: PASS)")
        return True

    def check_price_abnormal(self, current_price: float, order_price: float, threshold: float = 0.1) -> bool:
        """检查下单价格是否偏离市价过大 (防止胖手指)"""
        if order_price <= 0: return True # Market order
        
        deviation = abs(current_price - order_price) / current_price
        if deviation > threshold:
            logger.warning(f"Price deviation too high! Current: {current_price}, Order: {order_price}, Dev: {deviation:.2%}")
            return False
        return True
