import pandas as pd
import numpy as np
from typing import Dict, Any

class TechnicalIndicators:
    """技术指标计算器 (纯 Pandas 实现，无外部 ta依赖)"""

    @staticmethod
    def calculate_ma(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """简单移动平均线 (SMA)"""
        if 'close' not in df: return pd.Series(index=df.index)
        return df['close'].rolling(window=period).mean()

    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """指数移动平均线 (EMA)"""
        if 'close' not in df: return pd.Series(index=df.index)
        return df['close'].ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """相对强弱指数 (RSI)"""
        if 'close' not in df: return pd.Series(index=df.index)
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)

        # 使用 Wilder's Smoothing 方法 (与 ta-lib 一致)
        avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

        rs = avg_gain / avg_loss.replace(0, np.finfo(float).eps) # 避免除零
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """MACD 指标"""
        if 'close' not in df: 
            return {'macd': pd.Series(), 'signal': pd.Series(), 'hist': pd.Series()}
            
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        macd_hist = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'hist': macd_hist
        }

    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, nbdev: float = 2.0) -> Dict[str, pd.Series]:
        """布林带 (Bollinger Bands)"""
        if 'close' not in df:
             return {'lower': pd.Series(), 'middle': pd.Series(), 'upper': pd.Series()}

        middle = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        
        upper = middle + (std * nbdev)
        lower = middle - (std * nbdev)
        
        return {
            'lower': lower,
            'middle': middle,
            'upper': upper
        }
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """平均真实波幅 (ATR)"""
        if not all(col in df for col in ['high', 'low', 'close']):
            return pd.Series(index=df.index)
            
        high = df['high']
        low = df['low']
        close = df['close']
        prev_close = close.shift(1)
        
        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        # ATR 使用 Wilder's Smoothing
        atr = tr.ewm(alpha=1/period, adjust=False).mean()
        
        return atr

    @staticmethod
    def get_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """计算主要指标并添加到 DataFrame"""
        try:
            # 确保数据量足够 (至少要有 period 大小)
            if len(df) < 2:
                return df
                
            if 'close' not in df.columns:
                return df
            
            df['MA20'] = TechnicalIndicators.calculate_ma(df, 20)
            df['MA50'] = TechnicalIndicators.calculate_ma(df, 50)
            df['EMA12'] = TechnicalIndicators.calculate_ema(df, 12)
            
            df['RSI'] = TechnicalIndicators.calculate_rsi(df)
            
            macd_data = TechnicalIndicators.calculate_macd(df)
            df['MACD'] = macd_data['macd']
            df['MACD_SIGNAL'] = macd_data['signal']
            df['MACD_HIST'] = macd_data['hist']
            
            bb_data = TechnicalIndicators.calculate_bollinger_bands(df)
            df['BB_UPPER'] = bb_data['upper']
            df['BB_LOWER'] = bb_data['lower']
            
            df['ATR'] = TechnicalIndicators.calculate_atr(df)
            
        except Exception as e:
            print(f"Error calculating indicators: {e}")
            # 不阻断主流程
            pass
            
        return df
