import sys
import os
import time
from loguru import logger

# 添加 src 到 path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

from src.api.binance_api import BinanceConnector

def verify_proxy():
    logger.info("Starting Proxy Verification...")
    
    # 初始化 Connector (会自动读取 config.yaml 中的代理)
    try:
        connector = BinanceConnector(use_testnet=True)
        if connector.client is None:
            logger.error("Client initialization failed (check config/logs).")
            return

        logger.info("Attempting to fetch BTCUSDT ticker via Proxy...")
        
        # 尝试获取公开数据
        ticker = connector.get_ticker("BTCUSDT")
        
        if ticker and 'price' in ticker:
            logger.success(f"✅ Connection Successful! BTCUSDT Price: {ticker['price']}")
        else:
            logger.warning("Received empty or invalid response.")
            
    except Exception as e:
        logger.error(f"❌ Connection Failed: {e}")
        if "451" in str(e):
             logger.error("Still getting 451 error. Proxy might not be working or not applied.")
        elif "ProxyError" in str(e):
             logger.error(f"Proxy Connection Error: {e}")

if __name__ == "__main__":
    verify_proxy()
