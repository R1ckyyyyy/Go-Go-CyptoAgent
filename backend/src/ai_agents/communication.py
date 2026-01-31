from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class MessageType(str, Enum):
    """通信消息类型"""
    TASK_ASSIGNMENT = "TASK_ASSIGNMENT"   # 任务分配
    ANALYSIS_REPORT = "ANALYSIS_REPORT"   # 分析报告
    STRATEGY_PLAN = "STRATEGY_PLAN"       # 宏观策略
    DECISION_OUTPUT = "DECISION_OUTPUT"   # 最终决策
    DATA_REQUEST = "DATA_REQUEST"         # 数据请求
    DATA_RESPONSE = "DATA_RESPONSE"       # 数据响应
    ERROR_REPORT = "ERROR_REPORT"         # 错误报告
    STATUS_UPDATE = "STATUS_UPDATE"       # 状态更新

class AgentMessage(BaseModel):
    """
    代理间通信消息标准格式
    """
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = Field(..., description="发送方Agent ID")
    receiver: str = Field(..., description="接收方Agent ID (或 'all')")
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    message_type: MessageType = Field(..., description="消息类型")
    content: Dict[str, Any] = Field(..., description="消息具体内容")
    
    class Config:
        use_enum_values = True

    def to_json(self) -> str:
        return self.model_dump_json()
    
    @classmethod
    def from_json(cls, json_str: str) -> "AgentMessage":
        return cls.model_validate_json(json_str)

class CommunicationChannel:
    """
    简单的内存消息通道，用于代理间直接传递消息
    (在实际分布式系统中可以使用Redis/RabbitMQ)
    """
    _instance = None
    _message_queue: List[AgentMessage] = []
    _listeners: Dict[str, List] = {} # target: [callback]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CommunicationChannel, cls).__new__(cls)
            cls._instance._message_queue = []
            cls._instance._listeners = {}
        return cls._instance

    def publish(self, message: AgentMessage):
        """发布消息"""
        print(f"[Channel] Message from {message.sender} to {message.receiver}: {message.message_type}")
        self._message_queue.append(message)
        
        # 触发监听器 (简化版Observer模式)
        if message.receiver in self._listeners:
            for callback in self._listeners[message.receiver]:
                try:
                    callback(message)
                except Exception as e:
                    print(f"Error acting on message: {e}")
        
        # 同时触发广播监听器
        if "all" in self._listeners:
            for callback in self._listeners["all"]:
                try:
                    callback(message)
                except Exception as e:
                    print(f"Error acting on broadcast: {e}")

    def subscribe(self, agent_id: str, callback):
        """订阅发给特定Agent的消息"""
        if agent_id not in self._listeners:
            self._listeners[agent_id] = []
        self._listeners[agent_id].append(callback)

    def get_history(self, limit: int = 100) -> List[AgentMessage]:
        return self._message_queue[-limit:]

