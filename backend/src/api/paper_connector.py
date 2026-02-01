from typing import Dict, List, Optional
import time
from src.api.binance_api import BinanceConnector
from src.utils.logger import logger

class PaperTradingConnector:
    """
    模拟盘连接器 (Paper Trading)
    
    原理:
    1. 行情数据 (Market Data) -> 透传给真实的 BinanceConnector (看真盘)
    2. 交易/账户 (Trade/Account) -> 拦截并在本地内存/数据库中模拟 (做假单)
    """
    
    def __init__(self, real_connector: BinanceConnector, initial_balance: float = 10000.0):
        self.real_connector = real_connector
        self.balance = {"USDT": initial_balance}
        self.positions = {} # symbol -> quantity
        logger.info(f"🛡️ Paper Trading Initialized. Virtual Balance: {initial_balance} USDT")

    @property
    def use_testnet(self) -> bool:
        return self.real_connector.use_testnet
        
    def get_ticker(self, symbol: str) -> Dict:
        """透传: 获取真实市场价格"""
        return self.real_connector.get_ticker(symbol)
        
    def get_kline_data(self, symbol: str, interval: str, limit: int = 100):
        """透传: 获取真实K线"""
        return self.real_connector.get_kline_data(symbol, interval, limit)

    def get_account_balance(self) -> Dict[str, float]:
        """模拟: 返回虚拟余额"""
        return self.balance

    def get_current_positions(self) -> List[Dict]:
        """模拟: 返回虚拟持仓"""
        pos_list = []
        for symbol, qty in self.positions.items():
            if qty > 0:
                pos_list.append({"symbol": symbol, "amount": qty})
        return pos_list

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None) -> Dict:
        """模拟: 虚拟下单"""
        # 1. 获取当前价格用于撮合
        current_price = price
        if not current_price:
            ticker = self.get_ticker(symbol)
            current_price = float(ticker['price'])
            
        cost = current_price * quantity
        
        logger.info(f"📝 PAPER TRADE: {side} {quantity} {symbol} @ {current_price} (Est. Cost: {cost})")
        
        # 2. 简单的撮合逻辑
        if side.upper() == "BUY":
            if self.balance.get("USDT", 0) >= cost:
                self.balance["USDT"] -= cost
                self.positions[symbol] = self.positions.get(symbol, 0) + quantity
                status = "FILLED"
            else:
                logger.warning("Paper Trade Failed: Insufficient Fund")
                status = "REJECTED"
        elif side.upper() == "SELL":
            if self.positions.get(symbol, 0) >= quantity:
                self.positions[symbol] -= quantity
                self.balance["USDT"] = self.balance.get("USDT", 0) + cost
                status = "FILLED"
            else:
                logger.warning("Paper Trade Failed: Insufficient Position")
                status = "REJECTED"
                
        # 构造一个像模像样的 Order Response
        return {
            "symbol": symbol,
            "orderId": f"paper_{int(time.time())}",
            "status": status,
            "executedQty": str(quantity),
            "cummulativeQuoteQty": str(cost),
            "side": side
        }

    def cancel_order(self, symbol: str, order_id: str) -> Dict:
        logger.info(f"📝 PAPER TRADE: Cancelled order {order_id}")
        return {"status": "CANCELLED"}
