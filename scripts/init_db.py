import sys
import os

# 将项目根目录添加到 python path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(os.path.join(root_dir, "backend"))

from src.database.operations import db
from src.utils.logger import logger

def init_db():
    logger.info("Starting database initialization...")
    try:
        db.create_all_tables() # 注意: operations.py 中定义的方法名是 create_tables
        logger.info("Database initialized successfully!")
    except AttributeError:
         # 修正: 如果 operations.py 中是 create_tables
        db.create_tables()
        logger.info("Database initialized successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db()
