import yaml
import os
from typing import Dict, Any, Optional
from src.utils.logger import logger
from src.config.config_validator import ConfigValidator

class StrategyConfig:
    """
    策略配置管理类
    负责加载、验证和提供策略配置。支持根据市场环境建议调整。
    """
    
    DEFAULT_STRATEGY = "moderate_strategy.yaml"
    STRATEGY_DIR = os.path.join(os.path.dirname(__file__), "strategies")
    
    def __init__(self, strategy_file: str = None):
        self.current_strategy_name = strategy_file or self.DEFAULT_STRATEGY
        self.config = {}
        self.load_config(self.current_strategy_name)

    def load_config(self, filename: str) -> bool:
        """加载指定策略文件"""
        path = os.path.join(self.STRATEGY_DIR, filename)
        if not os.path.exists(path):
            logger.error(f"Strategy file not found: {path}")
            return False
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                new_config = yaml.safe_load(f)
                
            if ConfigValidator.validate_strategy_config(new_config):
                self.config = new_config
                self.current_strategy_name = filename
                logger.info(f"Loaded strategy configuration: {filename}")
                return True
            else:
                logger.error(f"Validation failed for strategy: {filename}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load strategy {filename}: {e}")
            return False

    def get_config(self) -> Dict[str, Any]:
        return self.config

    def suggest_adjustment(self, market_condition: str) -> Optional[str]:
        """
        根据市场环境建议策略调整
        market_condition: "Bull", "Bear", "Sideways"
        Returns: Suggested strategy filename or None
        """
        # Simple rule-based suggestion
        condition = market_condition.lower()
        current = self.current_strategy_name
        
        if "bear" in condition:
            if current != "conservative_strategy.yaml":
                return "conservative_strategy.yaml"
        elif "bull" in condition:
            if current != "aggressive_strategy.yaml" and current != "moderate_strategy.yaml":
                 # In Bull market, moderate or aggressive is fine. 
                 # If conservative, suggest moderate first.
                 return "moderate_strategy.yaml"
        elif "sideways" in condition or "volatile" in condition:
            if current == "aggressive_strategy.yaml":
                return "conservative_strategy.yaml" # Safety first in volatility
                
        return None

    def update_runtime_param(self, section: str, key: str, value: Any) -> bool:
        """运行动态修改参数 (不持久化到文件)"""
        if section in self.config and key in self.config[section]:
            # Backup
            old_val = self.config[section][key]
            self.config[section][key] = value
            
            # Validate
            if ConfigValidator.validate_strategy_config(self.config):
                logger.info(f"Runtime config updated: {section}.{key} = {value}")
                return True
            else:
                # Rollback
                self.config[section][key] = old_val
                logger.warning(f"Runtime update rejected by validation: {section}.{key} = {value}")
                return False
        return False
