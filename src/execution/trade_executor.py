from typing import Dict, Any, Optional
import uuid

from src.execution.order_types import Order, OrderSide, OrderType
from src.execution.position_manager import PositionManager
from src.execution.safety_checks import SafetyChecker
from src.utils.logger import logger
from src.api.binance_api import BinanceConnector

class TradeExecutor:
    """
    交易执行器
    """
    def __init__(self, mode: str = "simulated"):
        self.mode = mode
        self.position_manager = PositionManager(mode=mode)
        self.account_manager = self.position_manager.account_manager # Shortcut
        self.safety_checker = SafetyChecker()
        self.api = BinanceConnector() if mode == "live" else None

    def execute_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行决策层传入的指令
        decision: {
            "decision": "BUY",
            "symbol": "BTCUSDT",
            "quantity": 0.1,
            "action_type": "MARKET"|"LIMIT",
            "target_price": ...
        }
        """
        action = decision.get("decision")
        symbol = decision.get("symbol")
        
        if action == "HOLD":
            logger.info(f"Execution: HOLD decision for {symbol}")
            return {"status": "skipped", "reason": "HOLD"}
            
        quantity = float(decision.get("quantity", 0))
        target_price = float(decision.get("target_price", 0))
        action_type = decision.get("action_type", "MARKET")
        
        # 1. 获取当前市场价格 (用于验证/市价估算)
        current_price = 0.0
        try:
             # 实盘用 API，模拟盘也用 API 获取最新参考价
             # 注意：模拟盘如果不联网，这里会失败，需要 mock
             if self.api: 
                ticker = self.api.get_ticker(symbol)
                current_price = ticker['price']
             else:
                # 尝试从 BinanceConnector 获取 (它默认会 init)
                # 如果是完全离线模式，这里需要一个 PriceSource 抽象
                # 暂时假设总能连网获取价格
                current_price = BinanceConnector().get_ticker(symbol)['price']
        except Exception as e:
            logger.warning(f"Could not fetch current price for {symbol}: {e}")
            # 如果是市价单且获取不到价格，无法估算成本 -> 风险
            if action_type == "MARKET":
                return {"status": "failed", "reason": "Price unavailable for validation"}
            current_price = target_price # Fallback for Limit

        # 2. 构造订单对象
        try:
            order = Order(
                symbol=symbol,
                side=OrderSide(action),  # BUY/SELL
                order_type=OrderType(action_type), # MARKET/LIMIT
                quantity=quantity,
                price=target_price if action_type == "LIMIT" else current_price,
            )
        except ValueError as e:
             return {"status": "failed", "reason": f"Invalid order parameters: {e}"}

        # 3. 安全检查
        account_info = self.account_manager.get_account_info()
        if not self.safety_checker.check_all(order.to_dict(), account_info):
            logger.warning("Safety check failed!")
            return {"status": "rejected", "reason": "Safety check failed"}
            
        # 4. 资金验证
        if not self.account_manager.validate_balance(
            symbol, quantity, 
            order.price if order.price else current_price, 
            order.side.value
        ):
             return {"status": "rejected", "reason": "Insufficient funds/balance"}

        # 5. 执行交易
        logger.info(f"Executing {self.mode} trade: {action} {symbol} {quantity} @ {order.price}")
        result = {}
        
        if self.mode == "live":
            result = self._execute_live(order)
        else:
            result = self._execute_simulated(order)
            
        return result

    def _execute_live(self, order: Order) -> Dict:
        # 调用 API 下单
        # api.place_order(symbol, side, type, qty, price)
        try:
            resp = self.api.place_order(
                symbol=order.symbol,
                side=order.side.value,
                order_type=order.order_type.value,
                quantity=order.quantity,
                price=order.price if order.order_type == OrderType.LIMIT else None
            )
            return {"status": "executed", "order_id": resp.get("orderId"), "detail": resp}
        except Exception as e:
            logger.error(f"Live execution failed: {e}")
            return {"status": "failed", "reason": str(e)}

    def _execute_simulated(self, order: Order) -> Dict:
        # 模拟盘直接调用 PositionManager 更新
        # 模拟即时成交 (对于 Market) 或 简化成交
        
        trade_data = {
            "symbol": order.symbol,
            "side": order.side.value,
            "quantity": order.quantity,
            "price": order.price, # Use the estimated price or limit price
            "fee": 0.0,
            "timestamp": order.timestamp,
            "order_id": f"sim_{uuid.uuid4().hex[:8]}", # Mock ID
            "status": "FILLED"
        }
        
        try:
            self.position_manager.update_position(trade_data)
            return {"status": "executed", "order_id": trade_data["order_id"], "detail": trade_data}
        except Exception as e:
            logger.error(f"Simulated execution failed: {e}")
            return {"status": "failed", "reason": str(e)}
