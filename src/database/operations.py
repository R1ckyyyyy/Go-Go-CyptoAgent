from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from typing import List, Optional, Any
import os

from src.database.models import Base, Position, Trade, MarketData, AIDecision, AICommunication, Memory, Config
from src.utils.logger import logger

# 数据库路径配置
DB_PATH = os.path.join(os.getcwd(), "data", "database.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

class DatabaseManager:
    """数据库管理类，处理所有数据库交互"""
    
    def __init__(self, db_url: str = DATABASE_URL):
        self.engine = create_engine(db_url, echo=False, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        logger.info(f"Database engine initialized at {db_url}")

    def create_tables(self):
        """创建所有数据表"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("All database tables created successfully.")

    @contextmanager
    def get_session(self):
        """获取数据库会话的上下文管理器"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    # --- Position Operations ---
    def update_position(self, symbol: str, amount: float, avg_price: float, current_price: float):
        """更新或创建持仓记录"""
        with self.get_session() as session:
            try:
                position = session.query(Position).filter(Position.symbol == symbol).first()
                if position:
                    position.amount = amount
                    position.avg_price = avg_price
                    position.current_price = current_price
                    # 简单计算未实现盈亏: (当前价格 - 平均价格) * 数量
                    position.pnl = (current_price - avg_price) * amount
                    logger.debug(f"Updated position for {symbol}")
                else:
                    position = Position(
                        symbol=symbol,
                        amount=amount,
                        avg_price=avg_price,
                        current_price=current_price,
                        pnl=(current_price - avg_price) * amount
                    )
                    session.add(position)
                    logger.info(f"Created new position for {symbol}")
            except Exception as e:
                logger.error(f"Failed to update position for {symbol}: {e}")
                raise

    def get_all_positions(self) -> List[Position]:
        """获取所有持仓"""
        with self.get_session() as session:
            positions = session.query(Position).all()
            # 将对象从 session 中 detach，以便在 session 关闭后使用
            session.expunge_all() 
            return positions

    # --- Trade Operations ---
    def record_trade(self, trade_data: dict):
        """记录新的交易"""
        with self.get_session() as session:
            try:
                trade = Trade(**trade_data)
                session.add(trade)
                logger.info(f"Recorded trade: {trade_data.get('symbol')} {trade_data.get('side')}")
            except Exception as e:
                logger.error(f"Failed to record trade: {e}")
                raise

    def get_trades(self, limit: int = 50) -> List[Trade]:
        """获取最近交易记录"""
        with self.get_session() as session:
            trades = session.query(Trade).order_by(Trade.timestamp.desc()).limit(limit).all()
            session.expunge_all()
            return trades

    # --- Market Data Operations ---
    def save_market_data(self, data: dict):
        """保存市场快照"""
        with self.get_session() as session:
            try:
                market_data = MarketData(**data)
                session.add(market_data)
            except Exception as e:
                logger.error(f"Failed to save market data: {e}")

    # --- AI Decision Operations ---
    def log_decision(self, decision_data: dict):
        """记录AI决策"""
        with self.get_session() as session:
            try:
                decision = AIDecision(**decision_data)
                session.add(decision)
                logger.info(f"Logged AI decision: {decision_data.get('decision_type')}")
            except Exception as e:
                logger.error(f"Failed to log AI decision: {e}")

    # --- Config Operations ---
    def get_config(self, key: str, default: Any = None) -> str:
        """获取配置值"""
        with self.get_session() as session:
            config = session.query(Config).filter(Config.config_key == key).first()
            return config.config_value if config else default

    def set_config(self, key: str, value: str):
        """设置配置值"""
        with self.get_session() as session:
            try:
                config = session.query(Config).filter(Config.config_key == key).first()
                if config:
                    config.config_value = value
                else:
                    config = Config(config_key=key, config_value=value)
                    session.add(config)
                logger.info(f"Config updated: {key} = {value}")
            except Exception as e:
                logger.error(f"Failed to set config {key}: {e}")

# 全局数据库实例
db = DatabaseManager()
