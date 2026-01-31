import os
from src.config.strategy_config import StrategyConfig
from src.utils.logger import logger

def run_demo():
    print("=== Strategy Configuration Demo ===")
    
    # 1. Load Default
    print("\n[Loading Default Strategy]")
    strategy_mgr = StrategyConfig() # load moderate
    print(f"Current Strategy: {strategy_mgr.current_strategy_name}")
    print(f"Risk Level: {strategy_mgr.get_config()['trading_preference']['risk_level']}")
    
    # 2. Switch Strategy
    print("\n[Switching to Aggressive]")
    success = strategy_mgr.load_config("aggressive_strategy.yaml")
    if success:
        print(f"Switched to: {strategy_mgr.current_strategy_name}")
        print(f"Daily Trade Limit: {strategy_mgr.get_config()['risk_control']['daily_trade_limit']}")
    
    # 3. Auto Suggestion
    print("\n[Market Change: Bear Market Detected]")
    suggestion = strategy_mgr.suggest_adjustment("Bear Market")
    if suggestion:
        print(f"AI Suggests switching to: {suggestion}")
        strategy_mgr.load_config(suggestion)
        print(f"New Risk Level: {strategy_mgr.get_config()['trading_preference']['risk_level']}")
        
    # 4. Runtime Update & Validation
    print("\n[Attempting Runtime Update]")
    # Try invalid value
    print("Trying setting max_total_position to 1.5 (Invalid)...")
    res = strategy_mgr.update_runtime_param("trading_preference", "max_total_position", 1.5)
    print(f"Update Success: {res}")
    
    # Try valid value
    print("Trying setting max_total_position to 0.6...")
    res = strategy_mgr.update_runtime_param("trading_preference", "max_total_position", 0.6)
    print(f"Update Success: {res}")
    print(f"Current Max Position: {strategy_mgr.get_config()['trading_preference']['max_total_position']}")

if __name__ == "__main__":
    os.makedirs("data/logs", exist_ok=True)
    run_demo()
