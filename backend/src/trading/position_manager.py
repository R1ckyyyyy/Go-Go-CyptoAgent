from typing import Dict, Optional
from src.database.operations import db
from src.database.models import Trade, TradeSide, Position
from src.utils.logger import logger

class PositionManager:
    """
    仓位管理器 (The Warehouse Keeper)
    负责维护持仓状态，计算平均成本和盈亏。
    
    Paper Mode: 基于 TradeHistory 模拟累加。
    Real Mode: (Future) 定时从交易所同步。
    """
    
    def __init__(self):
        pass

    def update_from_trade(self, trade: Dict):
        """
        根据成交记录更新持仓
        :param trade: dict like {'symbol': 'BTCUSDT', 'side': 'BUY', 'quantity': 0.1, 'price': 50000}
        """
        symbol = trade.get('symbol')
        side = trade.get('side') # TradeSide enum or string
        qty = float(trade.get('quantity', 0))
        price = float(trade.get('price', 0))
        
        if not symbol or qty <= 0:
            return

        # Normalize side string
        side_str = side.name if hasattr(side, 'name') else str(side)
        
        # 1. 获取当前持仓 (从 DB)
        # Note: db.get_all_positions returns list, we need specific one.
        # operations.py update_position logic is low-level, we should implement higher level logic here.
        # But operations.py `update_position` overwrites, doesn't calculate avg price for multiple adds.
        # So we need to fetch -> calc -> save.
        
        # We need a get_position method in db operations or filter from all.
        # For efficiency let's reuse get_all_positions for now or add get_position.
        # Existing `update_position` in db operations does: (current - avg) * amount for PnL
        
        # Let's implement the logic to get current state first
        # operations.py doesn't have `get_position_by_symbol`, let's add it or work around.
        # Workaround: get_all and find.
        all_positions = db.get_all_positions()
        current_pos = next((p for p in all_positions if p.symbol == symbol), None)
        
        old_amount = current_pos.amount if current_pos else 0.0
        old_avg = current_pos.avg_price if current_pos else 0.0
        
        new_amount = old_amount
        new_avg = old_avg
        
        # 2. 计算新持仓 (加权平均)
        if side_str == "BUY":
            # 加权平均成本
            total_cost = (old_amount * old_avg) + (qty * price)
            new_amount = old_amount + qty
            new_avg = total_cost / new_amount if new_amount > 0 else 0.0
            logger.info(f"Position Update [BUY]: {symbol} {old_amount}->{new_amount}, Avg {old_avg:.2f}->{new_avg:.2f}")
            
        elif side_str == "SELL":
            # 卖出不改变平均成本，只减少数量 (FIFO/LIFO impact on Realized PnL is not tracked here yet)
            new_amount = max(0.0, old_amount - qty)
            if new_amount == 0:
                new_avg = 0.0 # Reset if closed
            logger.info(f"Position Update [SELL]: {symbol} {old_amount}->{new_amount}")
            
        # 3. 更新 DB
        # operations.py `update_position` signature: (symbol, amount, avg_price, current_price)
        # It also updates PnL based on current_price.
        db.update_position(
            symbol=symbol,
            amount=new_amount,
            avg_price=new_avg,
            current_price=price # Use last trade price as current market price mark
        )
