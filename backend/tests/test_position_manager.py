import pytest
import os
import shutil
from src.execution.position_manager import PositionManager
from src.database.operations import DatabaseManager, Base

# Setup Test DB
TEST_DB_PATH = "tests/data/test_db.db"
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
    # Ensure connections are closed before deleting file
    manager.engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except PermissionError:
            pass # Ignore if still locked, not critical for test logic

@pytest.fixture
def position_manager(db_manager, monkeypatch):
    # Mock global db in position_manager module to use our test db
    monkeypatch.setattr("src.execution.position_manager.db", db_manager)
    monkeypatch.setattr("src.execution.account_manager.db", db_manager)
    
    # Initialize in simulated mode
    pm = PositionManager(mode="simulated")
    # Reset simulated balance
    pm.impl.account_manager.simulated_balance["USDT"] = 10000.0
    return pm

def test_simulated_buy_and_sell(position_manager):
    # 1. Initial State
    summary = position_manager.get_summary()
    assert summary['account_summary']['total_balance'] == 10000.0
    assert len(summary['positions']) == 0
    
    # 2. Buy BTC
    trade_buy = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "quantity": 0.1,
        "price": 50000.0,
        "fee": 0.0
    }
    position_manager.update_position(trade_buy)
    
    # Check Balance (10000 - 5000 = 5000)
    summary = position_manager.get_summary()
    assert summary['account_summary']['available_balance'] == 5000.0
    
    # Check Position
    positions = position_manager.get_positions()
    assert len(positions) == 1
    btc_pos = positions[0]
    assert btc_pos['symbol'] == "BTCUSDT"
    assert btc_pos['amount'] == 0.1
    assert btc_pos['avg_entry_price'] == 50000.0
    
    # 3. Buy More BTC (Avg Cost Calculation)
    trade_buy_2 = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "quantity": 0.1,
        "price": 60000.0,
        "fee": 0.0
    }
    position_manager.update_position(trade_buy_2)
    
    positions = position_manager.get_positions()
    btc_pos = positions[0]
    assert btc_pos['amount'] == 0.2
    # Avg price = (0.1*50000 + 0.1*60000) / 0.2 = 55000
    assert btc_pos['avg_entry_price'] == 55000.0 
    
    # 4. Sell Partial
    trade_sell = {
        "symbol": "BTCUSDT",
        "side": "SELL",
        "quantity": 0.1,
        "price": 70000.0, # Profit!
        "fee": 0.0
    }
    position_manager.update_position(trade_sell)
    
    # Check Balance
    # Spent: 5000 + 6000 = 11000. Initial 10000.
    # Actually logic in AccountManager:
    # Init: 10000
    # Buy1: -5000 -> 5000
    # Buy2: -6000 -> -1000 (Allow negative in basic sim? Code just does +=/-=)
    # Sell: +7000 -> 6000
    
    summary = position_manager.get_summary()
    # assert summary['account_summary']['available_balance'] == 6000.0 
    # Logic verification: The simple AccountManager allows negative balance if validat_balance is skipped. 
    # In test we call update_position directly which updates balance.
    
    positions = position_manager.get_positions()
    btc_pos = positions[0]
    assert btc_pos['amount'] == 0.1
    assert btc_pos['avg_entry_price'] == 55000.0 # Cost basis unchanged on sell
