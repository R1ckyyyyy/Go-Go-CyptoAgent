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

class PerformanceResponse(BaseModel):
    total_pnl: float
    pnl_percentage: float
    win_rate: float

# --- Routes ---

@router.get("/balance", response_model=BalanceResponse)
async def get_balance():
    """获取账户余额 (Mock for now, should connect to Exchange/DB)"""
    # TODO: Connect to Exchange API or store in DB
    return BalanceResponse(
        total_balance=10500.0,
        available_balance=5000.0,
        currency="USDT"
    )

@router.get("/positions", response_model=List[PositionResponse])
async def get_positions():
    """获取当前持仓"""
    try:
        positions = db.get_all_positions()
        return [
            PositionResponse(
                symbol=p.symbol,
                amount=p.amount,
                avg_price=p.avg_price,
                current_price=p.current_price,
                pnl=p.pnl
            ) for p in positions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/performance", response_model=PerformanceResponse)
async def get_performance():
    """获取账户表现"""
    # TODO: Calculate from trade history
    return PerformanceResponse(
        total_pnl=1500.0,
        pnl_percentage=14.2,
        win_rate=0.65
    )
