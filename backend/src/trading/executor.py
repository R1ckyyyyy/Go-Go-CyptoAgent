import yaml
import os
import uuid
from datetime import datetime
from typing import Dict, Optional, Tuple

from src.database.operations import db
from src.database.models import Trade, OrderStatus, TradeSide, AIDecision
from src.api.binance_api import BinanceConnector
from src.trading.safety import SafetyGuard, OrderParams
from src.trading.position_manager import PositionManager
from src.utils.logger import logger

# Load Config
CONFIG_PATH = os.path.join(os.getcwd(), "config", "config.yaml")

class ExecutionResult:
    def __init__(self, success: bool, order_id: str, message: str, filled_price: float = 0.0, filled_qty: float = 0.0):
        self.success = success
        self.order_id = order_id
        self.message = message
        self.filled_price = filled_price
        self.filled_qty = filled_qty

class TradeExecutor:
    """
    交易执行器 ("Hand")
    负责根据 AI 决策执行具体交易（实盘或模拟）。
    """
    
    def __init__(self):
        self.config = self._load_config()
        self.trading_mode = self.config.get('trading', {}).get('mode', 'PAPER').upper()
        self.connector = BinanceConnector(use_testnet=False) # Config handles API keys
        self.guard = SafetyGuard()
        self.position_manager = PositionManager()
        
        logger.info(f"TradeExecutor initialized in [{self.trading_mode}] mode.")

    def _load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    async def execute_decision(self, decision: AIDecision) -> ExecutionResult:
        """
        执行 AI 决策
        :param decision: DB 中的 AIDecision 对象 (或者包含 decision dict)
        """
        try:
            # 1. 解析决策内容
            # decision.output_recommendation 应该是 {"action": "BUY", "symbol": "BTCUSDT", "quantity": 0.01, ...}
            rec = decision.output_recommendation
            action = rec.get("action", "HOLD").upper()
            symbol = rec.get("symbol")
            
            if action not in ["BUY", "SELL"]:
                return ExecutionResult(False, "", f"Ignored action: {action}")

            # 获取当前价格 (用于计算名义价值和模拟成交)
            ticker = self.connector.get_ticker(symbol)
            current_price = ticker['price']
            
            # 计算/获取数量
            quantity = rec.get("quantity")
            if not quantity:
                 # TODO: Calculate based on risk % if not provided
                 # For now, require quantity from AI
                 return ExecutionResult(False, "", "Missing quantity in decision")

            # 构建订单参数
            order_params = OrderParams(
                symbol=symbol,
                side=action,
                order_type="MARKET", # V1 默认市价单
                quantity=quantity,
                price=current_price,
                notional=quantity * current_price
            )

            # 2. 获取账户余额 (用于风控)
            # 在模拟模式下，可能需要从 DB 读虚拟余额，这里简化：统一定义 Risk Base
            # 简单起见，实盘读实盘余额，模拟盘暂读初始配置
            if self.trading_mode == "REAL":
                balances = self.connector.get_account_balance()
                # 估算总权益 (USDT + Assets) -> 简化为 USDT 余额 + 持仓市值
                # 这里先只传 USDT 余额作为保守风控基准
                equity = balances.get("USDT", 0.0) 
            else:
                equity = self.config.get('trading', {}).get('initial_balance', 10000.0)

            # 3. 安全检查 (Shield)
            if not self.guard.check_order(equity, order_params):
                return ExecutionResult(False, "", "Blocked by SafetyGuard")

            # 4. 执行路由 (Dual Mode)
            if self.trading_mode == "REAL":
                return await self._execute_real(order_params)
            else:
                return await self._execute_paper(order_params)

        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return ExecutionResult(False, "", str(e))

    async def _execute_real(self, order: OrderParams) -> ExecutionResult:
        """实际发送到 Binance"""
        try:
            logger.warning(f"🚀 SENDING REAL ORDER: {order.symbol} {order.side} {order.quantity}")
            
            binance_res = self.connector.place_order(
                symbol=order.symbol,
                side=order.side,
                order_type=order.order_type,
                quantity=order.quantity
            )
            # Response example: {'symbol': 'BTCUSDT', 'orderId': 28, ... 'cummulativeQuoteQty': '...', 'executedQty': '...'}
            
            # 记录到 DB
            trade_dict = {
                "symbol": order.symbol,
                "side": TradeSide[order.side],
                "price": float(binance_res.get('cummulativeQuoteQty', 0)) / float(binance_res.get('executedQty', 1)),
                "quantity": float(binance_res.get('executedQty', order.quantity)),
                "fee": 0.0,
                "order_id": str(binance_res['orderId']),
                "status": OrderStatus.FILLED
            }
            db.record_trade(trade_dict)
            
            # Update Position
            self.position_manager.update_from_trade(trade_dict)
            
            return ExecutionResult(True, str(binance_res['orderId']), "Real order filled", trade_dict['price'], trade_dict['quantity'])

        except Exception as e:
            logger.error(f"Real execution error: {e}")
            return ExecutionResult(False, "", f"Binance Error: {e}")

    async def _execute_paper(self, order: OrderParams) -> ExecutionResult:
        """模拟执行"""
        logger.info(f"📝 SIMULATION ORDER: {order.symbol} {order.side} {order.quantity} @ ${order.price}")
        
        # 模拟 100% 成交
        fake_id = f"sim-{uuid.uuid4().hex[:8]}"
        
        trade_record = Trade(
            symbol=order.symbol,
            side=TradeSide[order.side],
            price=order.price,
            quantity=order.quantity,
            fee=order.notional * 0.001, # 0.1% fee simulation
            order_id=fake_id,
            status=OrderStatus.FILLED
        )
        
        # 写入 DB (关键：这样前端 Position/History 才能看到)
        # 注意：需要把 Trade 对象转为 dict，或者 update record_trade 接受 object
        # existing operations.py record_trade takes dict
        trade_dict = {
            "symbol": trade_record.symbol,
            "side": trade_record.side,
            "price": trade_record.price,
            "quantity": trade_record.quantity,
            "fee": trade_record.fee,
            "order_id": trade_record.order_id,
            "status": trade_record.status
        }
        db.record_trade(trade_dict) 
        
        # Update Position
        self.position_manager.update_from_trade(trade_dict)
        
        return ExecutionResult(True, fake_id, "Paper order filled", order.price, order.quantity)
