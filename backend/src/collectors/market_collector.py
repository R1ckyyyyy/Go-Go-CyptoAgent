import time
import schedule
import pandas as pd
from datetime import datetime, timezone
from src.api.binance_api import BinanceConnector
from src.database.operations import db, DatabaseManager
from src.collectors.indicators import TechnicalIndicators
from src.utils.logger import logger

class MarketDataCollector:
    """市场数据采集器"""

    def __init__(self, symbols: list = None):
        self.api = BinanceConnector()
        self.db = db
        # 默认采集 BTC, ETH, SOL
        self.symbols = symbols if symbols else ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        logger.info(f"MarketDataCollector initialized for symbols: {self.symbols}")

    def fetch_current_price(self):
        """获取当前价格并存储"""
        for symbol in self.symbols:
            try:
                ticker = self.api.get_ticker(symbol)
                price = float(ticker['price'])
                
                # 存入数据库 market_data 表 (简单快照)
                self.db.save_market_data({
                    'symbol': symbol,
                    'price': price,
                    'timestamp': datetime.now(timezone.utc)
                })
                logger.debug(f"Saved price for {symbol}: {price}")
            except Exception as e:
                logger.error(f"Error fetching price for {symbol}: {e}")

    def fetch_and_process_klines(self, interval: str = "1h"):
        """获取K线数据并计算指标，然后更新数据库或缓存"""
        # 注意: 实际项目中可能需要更复杂的存储策略 (如存储到时序数据库或 CSV)
        # 这里仅演示获取并计算流程
        for symbol in self.symbols:
            try:
                # 获取数据
                df = self.api.get_kline_data(symbol, interval, limit=100)
                
                # 计算指标
                df = TechnicalIndicators.get_all_indicators(df)
                
                # 获取最新一行数据
                latest = df.iloc[-1]
                
                # 记录主要指标状态 (假设这里我们只关心最新的)
                logger.info(f"Analysis for {symbol} ({interval}): Price={latest['close']}, RSI={latest['RSI']}, MACD={latest['MACD']}")
                
                # 这里可以扩展将完整的 K 线数据存入数据库的逻辑
                # 但考虑到 SQL 性能，通常只存最新的分析结果或使用专门的时序库
                
            except Exception as e:
                logger.error(f"Error processing klines for {symbol}: {e}")

    def start(self, interval_seconds: int = 60):
        """启动定时采集任务"""
        logger.info("Starting market data collection loop...")
        
        # 定义任务 schedule
        schedule.every(interval_seconds).seconds.do(self.fetch_current_price)
        schedule.every(5).minutes.do(self.fetch_and_process_klines, interval="15m")
        schedule.every(1).hours.do(self.fetch_and_process_klines, interval="1h")
        
        # 阻塞式运行 (实际部署时应在独立线程或进程中运行)
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    collector = MarketDataCollector()
    collector.fetch_current_price() # 单次运行测试
