from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
import json

from src.api.binance_api import BinanceConnector
from src.database.operations import db, DatabaseManager
from src.utils.logger import logger
from src.execution.account_manager import AccountManager

class BasePositionManager(ABC):
    @abstractmethod
    def get_positions(self) -> List[Dict]:
        pass

    @abstractmethod
    def update_position(self, trade_data: Dict):
        pass

    @abstractmethod
    def get_summary(self) -> Dict:
        pass

class PositionManager(BasePositionManager):
    """
    统一入口类，根据模式分发给 Live 或 Simulated
    """
    def __init__(self, mode: str = "simulated"):
        self.mode = mode
        self.account_manager = AccountManager(mode=mode)
        
        if mode == "live":
            self.impl = LivePositionManager(self.account_manager)
        else:
            self.impl = SimulatedPositionManager(self.account_manager)

    def get_positions(self) -> List[Dict]:
        return self.impl.get_positions()

    def update_position(self, trade_data: Dict):
        return self.impl.update_position(trade_data)

    def get_summary(self) -> Dict:
        return self.impl.get_summary()


class LivePositionManager(BasePositionManager):
    """实盘仓位管理"""
    def __init__(self, account_manager: AccountManager):
        self.api = BinanceConnector()
        self.db = db
        self.account_manager = account_manager

    def get_positions(self) -> List[Dict]:
        # 从币安获取最新持仓（余额）
        raw_positions = self.api.get_current_positions()
        
        standardized_positions = []
        for pos in raw_positions:
            symbol = pos['symbol']
            amount = float(pos['amount'])
            
            # 获取当前价格以计算市值
            ticker = self.api.get_ticker(symbol)
            current_price = ticker.get('price', 0.0)
            market_value = amount * current_price
            
            # 实盘难以准确获取"平均持仓成本"和"未实现盈亏"，除非本地记录了所有历史
            # 这里先尝试从数据库获取本地记录的成本，如果无记录则用当前价暂代（会导致PnL为0）
            # 也可以从 API 的 /myTrades 接口重建，但这比较耗时。
            # 简化方案：只显示市值
            
            p_data = {
                "symbol": symbol,
                "amount": amount,
                "current_price": current_price,
                "market_value": market_value,
                "avg_entry_price": 0.0, # Needs local history
                "unrealized_pnl": 0.0,
                "position_ratio": 0.0 # calculate in summary
            }
            standardized_positions.append(p_data)
            
            # 同步到数据库
            self.db.update_position(symbol, amount, 0.0, current_price)
            
        return standardized_positions

    def get_summary(self) -> Dict:
        account_info = self.account_manager.get_account_info()
        positions = self.get_positions()
        
        total_market_value = sum(p['market_value'] for p in positions)
        total_balance = account_info.get('total_balance', 0) + total_market_value # USDT balance + Crypto value
        
        # Recalculate ratios
        for p in positions:
            if total_balance > 0:
                p['position_ratio'] = round(p['market_value'] / total_balance, 4)
            else:
                p['position_ratio'] = 0.0

        return {
            "account_summary": {
                "total_balance": total_balance,
                "available_balance": account_info.get("available_balance", 0),
                "unrealized_pnl": 0.0, # Not available
                "mode": "live"
            },
            "positions": positions
        }

    def update_position(self, trade_data: Dict):
        # 实盘由 API 自动更新，此方法仅用于通知数据库记录交易
        # trade_data format matches Database Trade model
        if trade_data:
            self.db.record_trade(trade_data)
            # Re-fetch is expensive, usually we assume API is source of truth


class SimulatedPositionManager(BasePositionManager):
    """模拟盘仓位管理 - 完全基于本地数据库"""
    def __init__(self, account_manager: AccountManager):
        self.db = db
        self.api = BinanceConnector() # Used for getting current prices only
        self.account_manager = account_manager

    def get_positions(self) -> List[Dict]:
        db_positions = self.db.get_all_positions()
        
        standardized_positions = []
        for pos in db_positions:
            if pos.amount <= 0.000001: # Filter empty
                continue
                
            # Fetch real-time price for valuation
            try:
                ticker = self.api.get_ticker(pos.symbol)
                current_price = ticker.get('price', pos.current_price)
            except:
                current_price = pos.current_price
            
            market_value = pos.amount * current_price
            unrealized_pnl = (current_price - pos.avg_price) * pos.amount
            pnl_pct = (unrealized_pnl / (pos.avg_price * pos.amount)) * 100 if pos.avg_price > 0 else 0
            
            p_data = {
                "symbol": pos.symbol,
                "amount": pos.amount,
                "avg_entry_price": pos.avg_price,
                "current_price": current_price,
                "market_value": round(market_value, 2),
                "unrealized_pnl": round(unrealized_pnl, 2),
                "pnl_percentage": round(pnl_pct, 2),
                "position_ratio": 0.0 # TO be calc
            }
            standardized_positions.append(p_data)
            
        return standardized_positions

    def update_position(self, trade_data: Dict):
        """
        模拟撮合更新本地持仓
        trade_data: {
            "symbol": "BTCUSDT",
            "side": "BUY"|"SELL",
            "quantity": 0.1,
            "price": 50000.0,
            "fee": 0.0
        }
        """
        symbol = trade_data['symbol']
        side = trade_data['side']
        qty = trade_data['quantity']
        price = trade_data['price']
        
        # Get existing from DB
        # Note: DB accessor in operations.py is simple 'update', we need manual calculation here
        # or expand DB operations. 
        # Here we do manual calc and call update.
        
        # 需要直接读取 DB 对象进行计算，operations里的 update_position 参数太简单，
        # 我们这里先用 get_all 找到对应的，虽然效率低点但逻辑清晰
        all_positions = self.db.get_all_positions()
        target_pos = next((p for p in all_positions if p.symbol == symbol), None)
        
        current_amt = target_pos.amount if target_pos else 0.0
        current_avg = target_pos.avg_price if target_pos else 0.0
        
        if side == "BUY":
            # 移动平均成本法
            total_cost = (current_amt * current_avg) + (qty * price)
            new_amt = current_amt + qty
            new_avg = total_cost / new_amt if new_amt > 0 else 0.0
            
            # deduction from balance
            cost = qty * price
            self.account_manager.update_simulated_balance(-cost)
            
        elif side == "SELL":
            # 卖出不影响平均成本，但产生已实现盈亏
            new_amt = current_amt - qty
            new_avg = current_avg # Cost basis doesn't change on sell
            if new_amt < 0: 
                new_amt = 0 # Should validat before
            
            # add to balance
            revenue = qty * price
            self.account_manager.update_simulated_balance(revenue)
            
        # Update DB
        self.db.update_position(symbol, new_amt, new_avg, price)
        self.db.record_trade(trade_data)
        logger.info(f"Simulated position updated for {symbol}: {side} {qty} @ {price}")

    def get_summary(self) -> Dict:
        positions = self.get_positions()
        account_info = self.account_manager.get_account_info()
        
        total_market_value = sum(p['market_value'] for p in positions)
        total_asset = account_info['available_balance'] + total_market_value
        total_pnl = sum(p['unrealized_pnl'] for p in positions)
        
        for p in positions:
            if total_asset > 0:
                p['position_ratio'] = round(p['market_value'] / total_asset, 4)
        
        return {
            "account_summary": {
                "total_balance": total_asset,
                "available_balance": account_info['available_balance'],
                "unrealized_pnl": total_pnl,
                "mode": "simulated"
            },
            "positions": positions
        }
