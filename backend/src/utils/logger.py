import sys
from loguru import logger
import os

# 确保日志目录存在
# 获取项目根目录: backend
current_dir = os.path.dirname(os.path.abspath(__file__))
# logger.py is in backend/src/utils, so root is up 2 levels
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
LOG_DIR = os.path.join(PROJECT_ROOT, "data", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(log_level="INFO", log_file=None):
    """
    配置全局 Logger
    :param log_level: 日志级别
    :param log_file: 日志文件路径，默认为 data/logs/app.log
    """
    logger.remove()  # 移除默认的 handler
    
    if log_file is None:
        log_file = os.path.join(LOG_DIR, "app.log")

    # 控制台输出
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level
    )

    # 文件输出 (每天轮转，保留 10 天，压缩)
    logger.add(
        log_file,
        rotation="00:00",
        retention="10 days",
        compression="zip",
        level=log_level,
        encoding="utf-8"
    )
    
    # 错误日志单独文件
    error_log = os.path.join(LOG_DIR, "error.log")
    logger.add(
        error_log,
        rotation="10 MB",
        retention="30 days",
        level="ERROR",
        encoding="utf-8"
    )
    
    return logger

# 默认初始化
setup_logger()
