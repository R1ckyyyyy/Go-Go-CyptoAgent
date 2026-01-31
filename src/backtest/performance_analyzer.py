import pandas as pd
import numpy as np
from typing import List, Dict

class PerformanceAnalyzer:
    """
    回测性能分析器
    计算收益率、回撤、夏普比率等指标。
    """
    
    def __init__(self, start_balance: float):
        self.start_balance = start_balance
        self.equity_curve = [] # List of {'timestamp': ..., 'equity': ...}
        self.trades = []
        
    def record_equity(self, timestamp, equity):
        self.equity_curve.append({'timestamp': timestamp, 'equity': equity})
        
    def record_trade(self, trade: Dict):
        self.trades.append(trade)
        
    def calculate_metrics(self) -> Dict:
        if not self.equity_curve:
            return {}
            
        df = pd.DataFrame(self.equity_curve)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # 1. Total Return
        final_equity = df['equity'].iloc[-1]
        total_return = (final_equity - self.start_balance) / self.start_balance
        
        # 2. Daily Returns for Sharpe
        # Resample to daily to calculate standard sharpe
        daily_df = df.resample('D').last().dropna()
        if len(daily_df) < 2:
            sharpe_ratio = 0.0
        else:
            daily_df['pct_change'] = daily_df['equity'].pct_change()
            mean_ret = daily_df['pct_change'].mean()
            std_ret = daily_df['pct_change'].std()
            sharpe_ratio = (mean_ret / std_ret * np.sqrt(365)) if std_ret != 0 else 0.0
            
        # 3. Max Drawdown
        df['peak'] = df['equity'].cummax()
        df['drawdown'] = (df['equity'] - df['peak']) / df['peak']
        max_drawdown = df['drawdown'].min()
        
        # 4. Trade Stats
        win_trades = [t for t in self.trades if t.get('pnl', 0) > 0] # Need realized PnL
        # Note: SimulatedPositionManager logs trades but maybe not realized PnL explicitly in the trade dict 
        # unless we improved it. For now, we count purely "winning trades" if we had that info.
        # Assuming trade dict has 'realized_pnl'
        
        return {
            "initial_balance": self.start_balance,
            "final_balance": final_equity,
            "total_return_pct": round(total_return * 100, 2),
            "max_drawdown_pct": round(max_drawdown * 100, 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "total_trades": len(self.trades)
        }
        
    def generate_report(self) -> str:
        metrics = self.calculate_metrics()
        report = []
        report.append("=== Backtest Performance Report ===")
        report.append(f"Initial Balance: {metrics.get('initial_balance')}")
        report.append(f"Final Balance:   {metrics.get('final_balance')}")
        report.append(f"Total Return:    {metrics.get('total_return_pct')}%")
        report.append(f"Max Drawdown:    {metrics.get('max_drawdown_pct')}%")
        report.append(f"Sharpe Ratio:    {metrics.get('sharpe_ratio')}")
        report.append(f"Total Trades:    {metrics.get('total_trades')}")
        return "\n".join(report)
