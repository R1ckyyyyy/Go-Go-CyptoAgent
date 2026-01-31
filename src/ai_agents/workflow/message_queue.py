from typing import Dict, Any, Optional, List
import json
from datetime import datetime
from src.ai_agents.communication import CommunicationChannel, AgentMessage
from src.database.operations import db
from src.utils.logger import logger

class MessageQueue:
    """
    增强版消息队列
    支持持久化、路由和追踪
    """
    
    def __init__(self):
        self.channel = CommunicationChannel()

    async def publish(self, message: AgentMessage):
        """发布消息并持久化"""
        # 1. 持久化到数据库
        try:
            db_record = {
                "from_ai": message.sender,
                "to_ai": message.receiver,
                "message_type": message.message_type,
                "content": message.content,
                "timestamp": datetime.now()
            }
            # 注意: db operations 暂不支持直接插入 Message Object，需适配
            # 这里为了演示，假设有对应的insert方法或直接使用ORM
            # db.save_message(db_record) 
            pass 
        except Exception as e:
            logger.error(f"Failed to persist message: {e}")

        # 2. 通过内存通道分发
        self.channel.publish(message)

    def subscribe(self, agent_id: str, callback):
        self.channel.subscribe(agent_id, callback)

    def get_trace(self, message_id: str):
        """获取消息追踪链 (TODO)"""
        pass

# 全局MQ实例
message_queue = MessageQueue()
