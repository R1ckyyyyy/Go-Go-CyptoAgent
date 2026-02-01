from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
import pandas as pd
import time
import os
import yaml
from functools import wraps
from typing import Dict, List, Optional, Any

from src.utils.logger import logger

# 加载配置
CONFIG_PATH = os.path.join(os.getcwd(), "config", "config.yaml")
API_KEYS_PATH = os.path.join(os.getcwd(), "config", "api_keys.yaml")

def load_api_keys():
    if os.path.exists(API_KEYS_PATH):
        with open(API_KEYS_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f).get('binance', {})
    return {}

def retry(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except (BinanceAPIException, BinanceOrderException) as e:
                    logger.warning(f"Binance API error in {func.__name__}: {e}. Retrying {retries + 1}/{max_retries}...")
                    retries += 1
                    time.sleep(delay)
                except Exception as e:
                    logger.error(f"Unexpected error in {func.__name__}: {e}")
                    raise
            raise Exception(f"Failed to execute {func.__name__} after {max_retries} retries")
        return wrapper
    return decorator

class BinanceConnector:
    """币安API封装类"""
    
    def __init__(self, use_testnet: bool = True):
        # 优先读取环境变量
        env_api_key = os.getenv('BINANCE_API_KEY')
        env_api_secret = os.getenv('BINANCE_API_SECRET')
        
        if env_api_key and env_api_secret:
            self.api_key = env_api_key
            self.api_secret = env_api_secret
            self.use_testnet = use_testnet # Env var doesn't typically specify testnet boolean, keeping arg
            logger.info("Loaded Binance API keys from environment variables.")
        else:
            # Fallback to YAML
            keys = load_api_keys()
            self.api_key = keys.get('api_key', '')
            self.api_secret = keys.get('api_secret', '')
            self.use_testnet = keys.get('testnet', use_testnet)
            logger.info("Loaded Binance API keys from YAML file.")

        if not self.api_key or not self.api_secret:
            logger.warning("Binance API keys not found! Connector will operate in restricted mode.")
        
        # 加载代理配置
        self.proxies = None
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                proxy_url = config.get('network', {}).get('proxy')
                if proxy_url:
                    self.proxies = {
                        'http': proxy_url,
                        'https': proxy_url
                    }
                    logger.info(f"Using proxy: {proxy_url}")

        try:
            # 传递 requests_params 以支持代理
            self.client = Client(
                self.api_key, 
                self.api_secret, 
                testnet=self.use_testnet,
                requests_params={'proxies': self.proxies} if self.proxies else None
            )
            logger.info(f"Binance client initialized (Testnet: {self.use_testnet})")
        except Exception as e:
            logger.error(f"Failed to initialize Binance client: {e}")
            self.client = None

    @retry()
    def get_account_balance(self) -> Dict[str, float]:
        """获取所有非零余额"""
        account = self.client.get_account()
        balances = {}
        for asset in account['balances']:
            free = float(asset['free'])
            locked = float(asset['locked'])
            if free > 0 or locked > 0:
                balances[asset['asset']] = free + locked
        return balances

    @retry()
    def get_current_positions(self) -> List[Dict]:
        """获取当前持仓 (现货和期货需要区分，这里暂时只取现货余额作为持仓)"""
        # 注意: 真正的"持仓"通常指期货合约，现货即余额
        # 这里为了统一接口，返回格式化的持仓列表
        balances = self.get_account_balance()
        positions = []
        for symbol, amount in balances.items():
            if symbol != 'USDT': # 假设 USDT 是计价货币
                positions.append({
                    'symbol': f"{symbol}USDT", # 假设交易对
                    'amount': amount
                })
        return positions

    @retry()
    def get_kline_data(self, symbol: str, interval: str, limit: int = 100) -> pd.DataFrame:
        """获取K线数据"""
        klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        return df

    @retry()
    def get_ticker(self, symbol: str) -> Dict:
        """获取最新价格"""
        ticker = self.client.get_symbol_ticker(symbol=symbol)
        return {'symbol': symbol, 'price': float(ticker['price'])}

    @retry()
    def get_order_book(self, symbol: str, limit: int = 10) -> Dict:
        """获取订单簿深度"""
        depth = self.client.get_order_book(symbol=symbol, limit=limit)
        return depth

    @retry()
    def get_24hr_ticker(self, symbols: List[str] = None) -> List[Dict]:
        """获取24小时价格变动统计 (Bulk)"""
        # Binance API 支持无参数获取所有 ticker，或者单个。python-binance 有 get_ticker 接口
        # 为了效率，我们直接获取所有然后过滤，或者循环获取（如果有cache）
        # 这里直接调用 client.get_ticker() 如果不传 symbol 会返回所有
        all_tickers = self.client.get_ticker()
        
        if not symbols:
            # 默认返回 TOP 关注的 -> 这里简单处理，如果有指定列表则过滤
            # 实际业务中不建议返回几千个，太慢
            return all_tickers
        
        # Filter list
        target_set = set(symbols)
        filtered = [t for t in all_tickers if t['symbol'] in target_set]
        return filtered

    @retry()
    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None) -> Dict:
        """下单"""
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity
        }
        if price:
            params['price'] = str(price)
            params['timeInForce'] = 'GTC'  # Good Till Cancel
            
        order = self.client.create_order(**params)
        logger.info(f"Order placed: {order}")
        return order

    @retry()
    def cancel_order(self, symbol: str, order_id: str) -> Dict:
        """撤单"""
        result = self.client.cancel_order(symbol=symbol, orderId=order_id)
        logger.info(f"Order cancelled: {result}")
        return result

    @retry()
    def get_order_status(self, symbol: str, order_id: str) -> Dict:
        """查询订单"""
# ... existing code ...

# --- Singleton Logic ---
_connector_instance: Optional['BinanceConnector'] = None

def get_binance_connector(use_testnet: bool = True) -> 'BinanceConnector':
    global _connector_instance
    if _connector_instance is None:
        _connector_instance = BinanceConnector(use_testnet=use_testnet)
    return _connector_instance
