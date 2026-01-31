from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"

@dataclass
class Order:
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None # Required for LIMIT
    stop_price: Optional[float] = None # for Stop orders
    client_order_id: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
    
    def to_dict(self):
        return {
            "symbol": self.symbol,
            "side": self.side.value,
            "order_type": self.order_type.value,
            "quantity": self.quantity,
            "price": self.price,
            "stop_price": self.stop_price,
            "client_order_id": self.client_order_id,
            "timestamp": self.timestamp.isoformat()
        }
