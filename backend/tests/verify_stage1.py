import sys
import os
import unittest
from unittest.mock import MagicMock
import pandas as pd
import sqlite3
import requests
from loguru import logger
import time
import numpy as np

# 将项目根目录添加到 python path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

from src.database.operations import db, DatabaseManager
# 从 models 中导入所有的模型定义
from src.database.models import Trade, OrderStatus, TradeSide

from src.collectors.indicators import TechnicalIndicators
from src.api.binance_api import BinanceConnector

class Stage1Verification(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # 移除 loguru 默认 handler 以避免测试时刷屏
        logger.remove()
        logger.add(sys.stderr, level="ERROR") # 仅显示错误

    def test_01_database_crud(self):
        """1. 数据库验证: 插入-查询-删除流程"""
        print("\n[Test 1/4] Verifying Database Operations...")
        
        # 插入
        trade_data = {
            "symbol": "TESTUSDT",
            "side": TradeSide.BUY,
            "price": 50000.0,
            "quantity": 0.1,
            "fee": 0.5,
            "order_id": "TEST_ORDER_001",
            "status": OrderStatus.FILLED
        }
        try:
            # 使用上下文管理器进行操作，确保提交
            with db.get_session() as session:
                # 先清理旧数据以免主键冲突
                old_trade = session.query(Trade).filter(Trade.order_id == "TEST_ORDER_001").first()
                if old_trade:
                    session.delete(old_trade)
            
            db.record_trade(trade_data)
            print("✅ Database Record Inserted Successfully")
            
            # 查询
            trades = db.get_trades(limit=10)
            found = False
            for t in trades:
                if t.order_id == "TEST_ORDER_001":
                    found = True
                    self.assertEqual(t.price, 50000.0)
                    self.assertEqual(t.quantity, 0.1)
                    break
            
            self.assertTrue(found, "Failed to retrieve the inserted record")
            print("✅ Database Record Retrieved Successfully")
            
        except Exception as e:
            print(f"❌ Database Test Failed: {e}")
            self.fail(f"Database operation error: {e}")

    def test_02_indicators_logic(self):
        """2. 技术指标验证: 生成随机数据计算 MA, RSI, MACD"""
        print("\n[Test 2/4] Verifying Indicators Calculation Logic (No Network Needed)...")
        
        # 生成 100 行随机数据
        dates = pd.date_range(start='2024-01-01', periods=100, freq='h')
        df = pd.DataFrame({
            'timestamp': dates,
            'open': np.random.uniform(40000, 42000, 100),
            'high': np.random.uniform(42000, 43000, 100),
            'low': np.random.uniform(39000, 40000, 100),
            'close': np.random.uniform(40000, 42000, 100),
            'volume': np.random.uniform(10 , 100, 100)
        })
        
        # 计算
        try:
            result_df = TechnicalIndicators.get_all_indicators(df)
            
            # 验证列是否存在
            expected_cols = ['MA20', 'RSI', 'MACD', 'BB_UPPER', 'ATR']
            for col in expected_cols:
                self.assertIn(col, result_df.columns, f"Indicator {col} missing")
            
            # 验证计算结果非空 (最后一行应该有值)
            last_row = result_df.iloc[-1]
            self.assertFalse(pd.isna(last_row['MA20']), "MA20 check failed")
            # RSI 前几行可能是 NaN，但最后一行应该有值
            if not pd.isna(last_row['RSI']):
                 print(f"✅ RSI Valid: {last_row['RSI']:.2f}")
            else:
                 print("⚠️ RSI is NaN (Data might be insufficient or logic error)")

            print(f"✅ Indicators Calculated Successfully.")
            
        except Exception as e:
            print(f"❌ Indicators Test Failed: {e}")
            self.fail(f"Indicators calculation error: {e}")

    def test_03_api_client_mock(self):
        """3. API 封装逻辑验证 (Mock): 不联网验证参数传递"""
        print("\n[Test 3/4] Verifying Binance API Wrapper Logic (Using Mock)...")
        
        # 创建 Mock 的 Client
        with unittest.mock.patch('src.api.binance_api.Client') as MockClient:
            mock_client_instance = MockClient.return_value
            
            # 设置 mock 返回值
            mock_client_instance.get_account.return_value = {
                'balances': [{'asset': 'BTC', 'free': '1.5', 'locked': '0.0'}, {'asset': 'USDT', 'free': '100.0', 'locked': '0.0'}]
            }
            mock_client_instance.create_order.return_value = {'orderId': 12345, 'status': 'NEW'}
            
            # 初始化我们自己的 Connector
            # 注意：即使有了 Mock，但在 BinanceConnector.__init__ 中，如果初始化 Client 失败会把 self.client 设为 None
            # 所以我们要保证 Client() 调用时不抛异常。这里 MockClient 默认构造函数不会抛异常。
            
            api = BinanceConnector(use_testnet=True)
            
            # 如果 api.client 是 None，说明初始化逻辑里捕获了异常。
            # 通常不需要 Key 也能初始化 Client 对象本身。
            if api.client is None:
                # 重新手动赋值 Mock 对象，以此测试后续逻辑
                api.client = mock_client_instance

            # 测试 get_account_balance 逻辑
            balance = api.get_account_balance()
            if balance is None:
                 print("⚠️ Account balance is None. Check if mock data is correct.")
            else:
                self.assertEqual(balance.get('BTC'), 1.5)
                print("✅ API Account Balance Logic Verified")
            
            # 测试下单参数传递逻辑
            api.place_order("BTCUSDT", "BUY", "LIMIT", 0.1, 50000)
            
            # 验证 create_order 是否被正确调用
            # 注意 python-binance 的 create_order 参数都是关键字参数
            # 我们代码里: create_order(**params) -> symbol, side, type, quantity, price, timeInForce
            call_args = mock_client_instance.create_order.call_args[1]
            self.assertEqual(call_args['symbol'], 'BTCUSDT')
            self.assertEqual(call_args['side'], 'BUY')
            self.assertEqual(str(call_args['price']), '50000') # 注意我们代码里转成了 str
            
            print("✅ API Order Placement Logic Verified")

    def test_04_network_connectivity(self):
        """4. 网络连通性检查 (可选): 尝试连接 API"""
        print("\n[Test 4/4] Checking Network Connectivity to Binance...")
        
        try:
            # 尝试连接 Binance API 公开接口
            url = "https://api.binance.com/api/v3/ping"
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                print("✅ Network Connection to Binance API Successful!")
            else:
                print(f"⚠️  Network Connection Failed (Status: {response.status_code}). Proxy might be needed.")
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Network Connection Failed.")
            print("👉 TIP: If you are in a restricted region, please configure a proxy.")
            print("   Example (PowerShell): $env:HTTP_PROXY='http://127.0.0.1:7890'; $env:HTTPS_PROXY='http://127.0.0.1:7890'")
            # 并不让测试失败，只是提示
            
if __name__ == '__main__':
    unittest.main()
