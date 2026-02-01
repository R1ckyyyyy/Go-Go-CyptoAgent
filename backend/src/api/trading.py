from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from src.database.operations import db

router = APIRouter()

# --- Models ---
class TradeResponse(BaseModel):
    id: int
    symbol: str
    side: str
    amount: float
    price: float
    timestamp: datetime
    pnl: Optional[float] = None

class OrderRequest(BaseModel):
    symbol: str
    side: str
    amount: float
    price: Optional[float] = None # Market order if None
    type: str = "market"

class OrderResponse(BaseModel):
    order_id: str
    status: str
    message: str

# --- Routes ---

@router.get("/history", response_model=List[TradeResponse])
async def get_trade_history(limit: int = 50):
    """获取历史成交记录"""
    try:
        trades = db.get_trades(limit=limit)
        return [
            TradeResponse(
                id=t.id,
                symbol=t.symbol,
                side=t.side.name if hasattr(t.side, 'name') else str(t.side),
                amount=t.quantity,
                price=t.price,
                timestamp=t.timestamp,
                pnl=getattr(t, 'pnl', None)
            ) for t in trades
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/manual", response_model=OrderResponse)
async def manual_order(order: OrderRequest):
    """手动下单 (Mock)"""
    # TODO: Call TradeExecutor
    return OrderResponse(
        order_id="mock_order_123",
        status="filled",
        message=f"Manual {order.side} order for {order.symbol} executed."
    )

@router.get("/orders")
async def get_open_orders():
    """获取当前活动订单 (Mock)"""
    return []

@router.delete("/order/{order_id}")
async def cancel_order(order_id: str):
    """撤销订单 (Mock)"""
    return {"message": f"Order {order_id} cancelled"}
