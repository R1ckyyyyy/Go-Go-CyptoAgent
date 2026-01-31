import sys
import os
from loguru import logger
import pandas as pd
import time

# 将 src 目录添加到 Python 路径 (如果是作为脚本运行)
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.operations import db, Position
from src.api.binance_api import BinanceConnector
from src.collectors.market_collector import MarketDataCollector
from src.collectors.news_collector import NewsCollector
from src.collectors.onchain_collector import OnChainCollector

def test_database():
    logger.info("--- Testing Database ---")
    try:
        # 尝试写入一个假配置
        db.set_config("test_key", "test_value_123")
        val = db.get_config("test_key")
        logger.info(f"Database Read/Write Test: {val == 'test_value_123'}")
        
        # 获取持仓 (应该为空)
        positions = db.get_all_positions()
        logger.info(f"Current Positions Count: {len(positions)}")
    except Exception as e:
        logger.error(f"Database Test Failed: {e}")

def test_api():
    logger.info("--- Testing Binance API ---")
    connector = BinanceConnector(use_testnet=True)
    if connector.client:
        try:
            # 获取 Ticker (不需要 API Key)
            ticker = connector.get_ticker("BTCUSDT")
            logger.info(f"BTC Price: {ticker.get('price')}")
            
            # 获取深度
            depth = connector.get_order_book("BTCUSDT", limit=5)
            logger.info(f"Order Book Bids: {len(depth.get('bids', []))}")
        except Exception as e:
            logger.error(f"API Test Failed (Check Network/Keys): {e}")
    else:
        logger.warning("Binance Client not initialized.")

def test_collectors():
    logger.info("--- Testing Collectors ---")
    
    # Market Collector
    try:
        market = MarketDataCollector(symbols=["BTCUSDT"])
        market.fetch_current_price()
        logger.info("MarketDataCollector: Fetch executed.")
    except Exception as e:
         logger.error(f"MarketDataCollector Failed: {e}")

    # News Collector
    try:
        news = NewsCollector()
        latest = news.fetch_latest_news(limit=1)
        logger.info(f"NewsCollector: Fetched {len(latest)} items.")
    except Exception as e:
         logger.error(f"NewsCollector Failed: {e}")

def main():
    logger.info("Crypto Trading AI System - Integration Test Starting...")
    
    test_database()
    test_api()
    test_collectors()
    
    logger.info("Integration Test Completed.")

if __name__ == "__main__":
    main()
