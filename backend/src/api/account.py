from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from src.database.operations import db
from src.database.models import Position as TIMPosition
from pydantic import BaseModel

router = APIRouter()

# --- Response Models ---
class PositionResponse(BaseModel):
    symbol: str
    amount: float
    avg_price: float
    current_price: float
    pnl: float

class BalanceResponse(BaseModel):
    total_balance: float
    available_balance: float
    currency: str
    today_pnl: float = 0.0
    total_pnl: float = 0.0

class PerformanceResponse(BaseModel):
    total_pnl: float
    pnl_percentage: float
    win_rate: float

# --- Routes ---

@router.get("/balance", response_model=BalanceResponse)
async def get_balance():
    """获取账户余额 (Mock)"""
    return BalanceResponse(
        total_balance=12450.80,
        available_balance=5200.50,
        currency="USDT",
        today_pnl=250.50,
        total_pnl=1450.80
    )

@router.get("/positions", response_model=List[PositionResponse])
async def get_positions():
    """获取当前持仓 (Mock)"""
    # 模拟数据
    return [
        PositionResponse(
            symbol="BTCUSDT",
            amount=0.15,
            avg_price=42000.00,
            current_price=43500.00,
            pnl=225.00
        ),
        PositionResponse(
            symbol="ETHUSDT",
            amount=2.5,
            avg_price=2200.00,
            current_price=2150.00,
            pnl=-125.00
        ),
        PositionResponse(
            symbol="SOLUSDT",
            amount=50.0,
            avg_price=85.00,
            current_price=92.50,
            pnl=375.00
        )
    ]

@router.get("/performance", response_model=PerformanceResponse)
async def get_performance():
    """获取账户表现 (Mock)"""
    return PerformanceResponse(
        total_pnl=475.0,
        pnl_percentage=3.96,
        win_rate=0.68
    )
