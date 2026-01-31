from typing import Dict, Any, List
from src.utils.logger import logger

class ConfigValidator:
    """策略配置验证器"""
    
    @staticmethod
    def validate_strategy_config(config: Dict[str, Any]) -> bool:
        """
        验证策略配置的合法性
        Return True if valid, False otherwise.
        """
        try:
            # 1. Check structure
            if "trading_preference" not in config:
                logger.error("Missing 'trading_preference' section")
                return False
            if "risk_control" not in config:
                logger.error("Missing 'risk_control' section")
                return False
                
            # 2. Check ranges
            tp = config["trading_preference"]
            rc = config["risk_control"]
            
            # Position ratios (0-1)
            if not (0 < tp.get("max_position_per_symbol", 0) <= 1):
                logger.error("max_position_per_symbol must be between 0 and 1")
                return False
            if not (0 < tp.get("max_total_position", 0) <= 1):
                logger.error("max_total_position must be between 0 and 1")
                return False
                
            # Loss percentages (0-1)
            if not (0 < rc.get("max_daily_loss", 0) < 1):
                logger.error("max_daily_loss must be between 0 and 1")
                return False
                
            # 3. logic conflicts
            # Stop loss should be reasonably small
            sl = rc.get("stop_loss_percentage", 0)
            if sl <= 0 or sl > 0.2:
                logger.warning(f"Abnormal stop_loss_percentage: {sl}")
                
            # max_single_loss should be < max_daily_loss
            if rc.get("max_single_loss", 0) > rc.get("max_daily_loss", 0):
                logger.error("max_single_loss cannot exceed max_daily_loss")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False
