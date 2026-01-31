import pandas as pd
import numpy as np
from typing import Dict, Any

class TechnicalIndicators:
    """技术指标计算器 (使用纯 Pandas 实现，避免依赖问题)"""

    @staticmethod
    def calculate_ma(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """简单移动平均线 (SMA)"""
        return df['close'].rolling(window=period).mean()

    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """指数移动平均线 (EMA)"""
        return df['close'].ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """相对强弱指数 (RSI)"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0))
        loss = (-delta.where(delta < 0, 0))

        # 使用 Wilder's Smoothing (类似于 EMA)
        avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """MACD 指标"""
        exp1 = df['close'].ewm(span=fast, adjust=False).mean()
        exp2 = df['close'].ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line

        return {
            'macd': macd,
            'signal': signal_line,
            'hist': histogram
        }

    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, nbdev: float = 2.0) -> Dict[str, pd.Series]:
        """布林带 (Bollinger Bands)"""
        ma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        upper = ma + (std * nbdev)
        lower = ma - (std * nbdev)
        
        return {
            'upper': upper,
            'middle': ma,
            'lower': lower
        }
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """平均真实波幅 (ATR)"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        
        # ATR 使用 EMA smoothing 或 SMA
        atr = true_range.rolling(window=period).mean()
        return atr

    @staticmethod
    def get_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """计算主要指标并添加到 DataFrame"""
        try:
            # 确保数据量足够
            if len(df) < 50:
                # print("Warning: Data length insufficient for indicators calculation.")
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
            import traceback
            traceback.print_exc()
            
        return df
