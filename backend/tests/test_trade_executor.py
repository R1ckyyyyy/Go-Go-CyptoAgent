import pytest
import os
import shutil
from src.execution.trade_executor import TradeExecutor
from src.database.operations import DatabaseManager

# Setup Test DB
TEST_DB_PATH = "tests/data/test_db_exec.db"
TEST_DB_URL = f"sqlite:///{TEST_DB_PATH}"

@pytest.fixture
def db_manager():
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass
            
    os.makedirs(os.path.dirname(TEST_DB_PATH), exist_ok=True)
    manager = DatabaseManager(db_url=TEST_DB_URL)
    manager.create_tables()
    yield manager
    
    manager.engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass

@pytest.fixture
def trade_executor(db_manager, monkeypatch):
    # Mock databases
    monkeypatch.setattr("src.execution.position_manager.db", db_manager)
    monkeypatch.setattr("src.execution.account_manager.db", db_manager)
    monkeypatch.setattr("src.execution.safety_checks.db", db_manager)
    
    # Init simulated
    executor = TradeExecutor(mode="simulated")
    # Reset balance
    executor.account_manager.simulated_balance["USDT"] = 10000.0
    
    return executor

def test_execute_buy_success(trade_executor, monkeypatch):
    class MockBinance:
        def get_ticker(self, symbol):
            return {"symbol": symbol, "price": 50000.0}
    
    monkeypatch.setattr("src.execution.trade_executor.BinanceConnector", MockBinance)

    decision = {
        "decision": "BUY",
        "symbol": "BTCUSDT",
        "quantity": 0.01, # Cost 500
        "action_type": "MARKET"
    }
    
    result = trade_executor.execute_decision(decision)
    assert result['status'] == 'executed'
    assert 'order_id' in result
    
    # Check balance
    summary = trade_executor.position_manager.get_summary()
    assert summary['account_summary']['available_balance'] == 9500.0

def test_execute_insufficient_funds(trade_executor, monkeypatch):
    class MockBinance:
        def get_ticker(self, symbol):
            return {"symbol": symbol, "price": 50000.0}
            
    monkeypatch.setattr("src.execution.trade_executor.BinanceConnector", MockBinance)

    decision = {
        "decision": "BUY",
        "symbol": "BTCUSDT",
        "quantity": 1.0, 
        "action_type": "MARKET"
    }
    
    result = trade_executor.execute_decision(decision)
    assert result['status'] == 'rejected'
    assert 'Insufficient funds' in result['reason']

def test_safety_hold(trade_executor):
    decision = {
        "decision": "HOLD",
        "symbol": "BTCUSDT"
    }
    result = trade_executor.execute_decision(decision)
    assert result['status'] == 'skipped'
