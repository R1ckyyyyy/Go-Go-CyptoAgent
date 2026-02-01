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

class EquityPoint(BaseModel):
    date: str
    value: float

class MarketTicker(BaseModel):
    symbol: str
    price: float
    change_24h: float
    volume_24h: str
    trend: List[float]  # For sparkline

# --- Routes ---

@router.get("/balance", response_model=BalanceResponse)
async def get_balance():
    """从 DB 计算模拟账户余额"""
    # 1. 获取所有持仓
    positions = db.get_all_positions()
    
    # 2. 计算当前 PnL 总和
    total_pnl = sum([p.pnl for p in positions])
    
    # 3. 初始资金 (Paper Trading Default)
    initial_balance = 10000.0
    
    # 4. 估算当前总资产 (注意：这只是一个近似值，更严格的做法是 Coordinator 将 Cash 写入 DB)
    # 假设所有未持仓的钱都在 Cash 里
    # Total Balance = Initial + Realized PnL (DB还没存) + Unrealized PnL
    # 暂时简化: Total = Initial + Unrealized PnL
    total_balance = initial_balance + total_pnl
    
    # 计算占用保证金 (简单假设全额现货)
    used_margin = sum([p.amount * p.avg_price for p in positions])
    available = total_balance - used_margin

    return BalanceResponse(
        total_balance=round(total_balance, 2),
        available_balance=round(available, 2),
        currency="USDT",
        today_pnl=round(total_pnl, 2), # 暂用 Total PnL 代替 Today
        total_pnl=round(total_pnl, 2)
    )

@router.get("/positions", response_model=List[PositionResponse])
async def get_positions():
    """从 DB 获取真实持仓"""
    db_positions = db.get_all_positions()
    res = []
    for p in db_positions:
        # 过滤掉数量极小的尘埃
        if p.amount > 0.0001:
            res.append(PositionResponse(
                symbol=p.symbol,
                amount=p.amount,
                avg_price=p.avg_price,
                current_price=p.current_price,
                pnl=p.pnl
            ))
    return res

@router.get("/performance", response_model=PerformanceResponse)
async def get_performance():
    """获取账户表现 (Placeholder)"""
    return PerformanceResponse(
        total_pnl=1245.50,
        pnl_percentage=12.45,
        win_rate=68.5
    )

@router.get("/equity-history", response_model=List[EquityPoint])
async def get_equity_history():
    """
    返回资产历史曲线。
    如果没有历史数据 (BalanceSnapshot 表不存在)，则返回当前余额作为一个点。
    """
    from datetime import datetime
    
    # 获取当前真实余额
    balance_data = await get_balance()
    current_equity = balance_data.total_balance
    
    # 暂时只返回一个当前点 (Real Data Start)
    # 真正的历史需要定时任务每天快照写入 DB
    return [
        EquityPoint(date=datetime.now().strftime("%m-%d"), value=current_equity)
    ]

@router.get("/market-summary", response_model=List[MarketTicker])
async def get_market_summary():
    """返回主要资产的市场快照 (Real Data from Binance)"""
    """返回主要资产的市场快照 (Real Data from Binance)"""
    from src.api.binance_api import get_binance_connector
    connector = get_binance_connector()
    
    target_symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "DOGEUSDT"]
    tickers = connector.get_24hr_ticker(target_symbols)
    
    res = []
    for t in tickers:
        try:
            # Generate fake sparkline trend based on current price (API doesn't provide history in ticker)
            # In production, this should query K-line data
            current_price = float(t['lastPrice'])
            
            # Simple simulation for sparkline: random walk around current price
            # This is a compromise to avoid 5 separate API calls for K-lines just for a sparkline
            import random
            trend = [current_price * (1 + random.uniform(-0.01, 0.01)) for _ in range(10)]
            trend[-1] = current_price
            
            # Format Volume (e.g. 1.2B)
            vol = float(t['quoteVolume'])
            if vol > 1_000_000_000:
                vol_str = f"{vol/1_000_000_000:.1f}B"
            elif vol > 1_000_000:
                vol_str = f"{vol/1_000_000:.1f}M"
            else:
                vol_str = f"{vol:.0f}"

            res.append(MarketTicker(
                symbol=t['symbol'].replace("USDT", ""), 
                price=current_price, 
                change_24h=float(t['priceChangePercent']), 
                volume_24h=vol_str,
                trend=trend
            ))
        except Exception as e:
            print(f"Error parsing ticker {t['symbol']}: {e}")
            
    return res
