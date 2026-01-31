import pandas as pd
import pandas_ta as ta
import numpy as np
from typing import Dict, Any

class TechnicalIndicators:
    """技术指标计算器 (使用 pandas_ta)"""

    @staticmethod
    def calculate_ma(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """简单移动平均线 (SMA)"""
        # pandas_ta 需要确保 df 有 datetime index 或者指定列
        return df.ta.sma(length=period)

    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """指数移动平均线 (EMA)"""
        return df.ta.ema(length=period)

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """相对强弱指数 (RSI)"""
        return df.ta.rsi(length=period)

    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """MACD 指标"""
        macd_df = df.ta.macd(fast=fast, slow=slow, signal=signal)
        
        if macd_df is None or macd_df.empty:
            return {'macd': pd.Series(), 'signal': pd.Series(), 'hist': pd.Series()}
            
        # pandas_ta 返回的列名通常是 MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9
        # 我们通过 iloc 按位置获取比较稳健: 0=MACD, 1=Histogram, 2=Signal
        return {
            'macd': macd_df.iloc[:, 0],
            'hist': macd_df.iloc[:, 1],
            'signal': macd_df.iloc[:, 2]
        }

    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, nbdev: float = 2.0) -> Dict[str, pd.Series]:
        """布林带 (Bollinger Bands)"""
        bb_df = df.ta.bbands(length=period, std=nbdev)
        
        if bb_df is None or bb_df.empty:
             return {'lower': pd.Series(), 'middle': pd.Series(), 'upper': pd.Series()}

        # 同样按位置: 0=Lower, 1=Middle, 2=Upper, 3=Bandwidth, 4=Percent
        return {
            'lower': bb_df.iloc[:, 0],
            'middle': bb_df.iloc[:, 1],
            'upper': bb_df.iloc[:, 2]
        }
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """平均真实波幅 (ATR)"""
        return df.ta.atr(length=period)

    @staticmethod
    def get_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """计算主要指标并添加到 DataFrame"""
        try:
            # 确保数据量足够
            if len(df) < 50:
                # print("Warning: Data length insufficient for indicators calculation.")
                return df
                
            # pandas_ta 需要 close 列
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
            # 记录错误但不中断
            print(f"Error calculating indicators: {e}")
            import traceback
            traceback.print_exc()
            
        return df
