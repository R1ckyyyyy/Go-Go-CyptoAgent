from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Enum
from sqlalchemy.orm import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class TradeSide(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(str, enum.Enum):
    NEW = "NEW"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"

class DecisionLayer(str, enum.Enum):
    MACRO = "MACRO"           # 宏观规划
    ANALYSIS = "ANALYSIS"     # 分析层
    EXECUTION = "EXECUTION"   # 执行层 (决策层)

class MemoryType(str, enum.Enum):
    SHORT_TERM = "SHORT_TERM"
    LONG_TERM = "LONG_TERM"
    EPISODIC = "EPISODIC"

class Position(Base):
    """当前持仓表"""
    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False, comment="交易对 (如 BTCUSDT)")
    amount = Column(Float, nullable=False, default=0.0, comment="持仓数量")
    avg_price = Column(Float, nullable=False, default=0.0, comment="平均持仓价格")
    current_price = Column(Float, nullable=False, default=0.0, comment="最近一次更新的市场价格")
    pnl = Column(Float, default=0.0, comment="未实现盈亏")
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="最后更新时间")

    def __repr__(self):
        return f"<Position(symbol='{self.symbol}', amount={self.amount}, pnl={self.pnl})>"

class Trade(Base):
    """交易历史表"""
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), index=True, nullable=False, comment="交易对")
    side = Column(Enum(TradeSide), nullable=False, comment="方向 (BUY/SELL)")
    price = Column(Float, nullable=False, comment="成交价格")
    quantity = Column(Float, nullable=False, comment="成交数量")
    fee = Column(Float, default=0.0, comment="交易手续费")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, comment="交易时间")
    order_id = Column(String(50), unique=True, index=True, comment="交易所订单ID")
    status = Column(Enum(OrderStatus), default=OrderStatus.FILLED, comment="订单状态")

    def __repr__(self):
        return f"<Trade(id={self.id}, symbol='{self.symbol}', side='{self.side}', price={self.price})>"

class MarketData(Base):
    """市场数据快照表"""
    __tablename__ = 'market_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), index=True, nullable=False, comment="交易对")
    price = Column(Float, nullable=False, comment="当前价格")
    volume_24h = Column(Float, comment="24小时成交量")
    change_24h = Column(Float, comment="24小时涨跌幅(%)")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, comment="记录时间")

    def __repr__(self):
        return f"<MarketData(symbol='{self.symbol}', price={self.price}, time='{self.timestamp}')>"

class AIDecision(Base):
    """AI决策记录表"""
    __tablename__ = 'ai_decisions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    decision_type = Column(String(50), nullable=False, comment="决策类型 (如 BUY_SIGNAL, SELL_SIGNAL, HOLD)")
    input_data = Column(JSON, comment="输入数据快照 (JSON)")
    output_recommendation = Column(JSON, comment="AI输出建议 (JSON)")
    confidence = Column(Float, comment="置信度 (0.0-1.0)")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, comment="决策生成时间")
    layer = Column(Enum(DecisionLayer), nullable=False, comment="决策层级")

    def __repr__(self):
        return f"<AIDecision(type='{self.decision_type}', layer='{self.layer}', confidence={self.confidence})>"

class AICommunication(Base):
    """AI间通信记录表"""
    __tablename__ = 'ai_communications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_ai = Column(String(50), nullable=False, comment="发送方AI名称")
    to_ai = Column(String(50), nullable=False, comment="接收方AI名称")
    message_type = Column(String(50), nullable=False, comment="消息类型")
    content = Column(JSON, nullable=False, comment="消息内容 (JSON)")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, comment="发送时间")

    def __repr__(self):
        return f"<AICommunication(from='{self.from_ai}', to='{self.to_ai}', type='{self.message_type}')>"

class Memory(Base):
    """系统记忆表"""
    __tablename__ = 'memory'

    id = Column(Integer, primary_key=True, autoincrement=True)
    memory_type = Column(Enum(MemoryType), nullable=False, comment="记忆类型")
    content = Column(JSON, nullable=False, comment="记忆内容")
    importance_score = Column(Float, default=0.0, index=True, comment="重要性评分")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, comment="记忆形成时间")
    expiry_date = Column(DateTime, nullable=True, index=True, comment="过期时间 (仅短期记忆)")

    def __repr__(self):
        return f"<Memory(type='{self.memory_type}', score={self.importance_score})>"

class Config(Base):
    """动态配置表"""
    __tablename__ = 'config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(100), unique=True, nullable=False, comment="配置键名")
    config_value = Column(String(500), nullable=False, comment="配置值")
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    def __repr__(self):
        return f"<Config(key='{self.config_key}', value='{self.config_value}')>"
