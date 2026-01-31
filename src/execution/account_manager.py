from typing import Dict, Any, Optional
from src.api.binance_api import BinanceConnector
from src.database.operations import db
from src.utils.logger import logger

class AccountManager:
    """
    账户资金管理器
    负责获取账户余额、计算总资产、验证交易资金等。
    支持实盘和模拟盘（通过配置区分，此处主要提供统一接口逻辑）。
    """
    def __init__(self, mode: str = "simulated", initial_balance: float = 10000.0):
        self.mode = mode
        self.api = BinanceConnector() if mode == "live" else None
        self.db = db
        # 模拟盘余额 (简单的内存维护，实际应持久化到数据库)
        self.simulated_balance = {
            "USDT": initial_balance
        }
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        获取账户标准信息
        Return format:
        {
            "total_balance": 10000.00, # 折合 USDT
            "available_balance": 7000.00, # USDT 余额
            "unrealized_pnl": 500.00, 
            "mode": "simulated"
        }
        """
        if self.mode == "live":
            return self._get_live_account_info()
        else:
            return self._get_simulated_account_info()

    def _get_live_account_info(self) -> Dict[str, Any]:
        try:
            balances = self.api.get_account_balance()
            
            # 计算总资产 (简化版: USDT余额 + 持仓市值)
            # 注意: 准确计算需要实时价格，这里为避免循环依赖，主要关注 USDT
            usdt_balance = balances.get("USDT", 0.0)
            
            # TODO: 遍历其他币种调用 get_ticker 计算市值
            # 为保持性能，此处暂只返回余额信息，市值计算交由 PositionManager 汇总
            
            return {
                "total_balance": usdt_balance, # 暂用 USDT 代表，后续由 PositionManager 修正
                "available_balance": usdt_balance,
                "unrealized_pnl": 0.0, # 实盘 PnL 需从 API 获取或自行计算
                "mode": "live",
                "raw_balances": balances
            }
        except Exception as e:
            logger.error(f"Failed to get live account info: {e}")
            return {"error": str(e)}

    def _get_simulated_account_info(self) -> Dict[str, Any]:
        # 模拟盘逻辑
        usdt_balance = self.simulated_balance.get("USDT", 0.0)
        return {
            "total_balance": usdt_balance, 
            "available_balance": usdt_balance,
            "unrealized_pnl": 0.0, # 由 PositionManager 计算
            "mode": "simulated"
        }

    def validate_balance(self, symbol: str, quantity: float, price: float, side: str) -> bool:
        """
        验证余额是否充足
        :param side: 'BUY' or 'SELL'
        """
        estimated_cost = quantity * price
        
        info = self.get_account_info()
        if "error" in info:
            return False

        if side == "BUY":
            # 检查 USDT 余额
            available = info.get("available_balance", 0.0)
            if available >= estimated_cost:
                return True
            else:
                logger.warning(f"Insufficient funds for BUY: Need {estimated_cost}, Have {available}")
                return False
        
        elif side == "SELL":
            # 检查持币数量
            if self.mode == "live":
                raw = info.get("raw_balances", {})
                base_asset = symbol.replace("USDT", "") # 简单假设
                available_crypto = raw.get(base_asset, 0.0)
                if available_crypto >= quantity:
                    return True
                else:
                    logger.warning(f"Insufficient asset for SELL: Need {quantity} {base_asset}, Have {available_crypto}")
                    return False
            else:
                # 模拟盘 Sell 验证需查询 PositionManager，此处 AccountManager 主要管钱
                # 可以在 PositionManager 中调用 validat_balance 仅用于买入，
                # 或在此处需访问数据库获取模拟持仓
                # 为解耦，建立简单的数据库查询
                # TODO: Implement simulated position check
                return True 
                
        return False

    def update_simulated_balance(self, change: float):
        """更新模拟盘余额 (仅限 USDT)"""
        if self.mode == "simulated":
            if "USDT" not in self.simulated_balance:
                self.simulated_balance["USDT"] = 0.0
            self.simulated_balance["USDT"] += change
            logger.info(f"Simulated balance updated by {change}. New balance: {self.simulated_balance['USDT']}")
