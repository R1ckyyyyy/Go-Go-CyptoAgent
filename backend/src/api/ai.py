from fastapi import APIRouter
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import random

router = APIRouter()

# --- Models ---
class NodePosition(BaseModel):
    x: float
    y: float

class AINode(BaseModel):
    id: str
    label: str
    type: str  # macro, analyst, decision, execution
    position: NodePosition
    description: str

class AIEdge(BaseModel):
    id: str
    source: str
    target: str
    animated: bool = True

class TreeStructure(BaseModel):
    nodes: List[AINode]
    edges: List[AIEdge]

class NodeStatus(BaseModel):
    id: str
    status: str  # idle, working, success, error
    current_task: str
    last_update: datetime

class DecisionResponse(BaseModel):
    id: int
    decision_type: str
    symbol: str
    action: str
    reason: str
    confidence: float
    timestamp: datetime
    details: Dict[str, Any]

class CommunicationResponse(BaseModel):
    sender: str
    receiver: str
    message_content: str
    timestamp: datetime
    message_type: str

# --- Routes ---

@router.get("/tree-structure", response_model=TreeStructure)
async def get_tree_structure():
    """返回 AI 决策树的静态结构"""
    nodes = [
        {"id": "macro", "label": "宏观策略 (Macro)", "type": "macro", "position": {"x": 250, "y": 0}, "description": "全球市场趋势分析"},
        {"id": "tech", "label": "技术分析 (Tech)", "type": "analyst", "position": {"x": 50, "y": 150}, "description": "技术指标与图表模式"},
        {"id": "fund", "label": "基本面 (Fund)", "type": "analyst", "position": {"x": 250, "y": 150}, "description": "链上数据与新闻情绪"},
        {"id": "risk", "label": "风控管理 (Risk)", "type": "analyst", "position": {"x": 450, "y": 150}, "description": "风险评估与仓位管理"},
        {"id": "decision", "label": "决策中枢 (Decision)", "type": "decision", "position": {"x": 250, "y": 300}, "description": "最终交易执行判定"},
    ]
    edges = [
        {"id": "e-m-t", "source": "macro", "target": "tech"},
        {"id": "e-m-f", "source": "macro", "target": "fund"},
        {"id": "e-m-r", "source": "macro", "target": "risk"},
        {"id": "e-t-d", "source": "tech", "target": "decision"},
        {"id": "e-f-d", "source": "fund", "target": "decision"},
        {"id": "e-r-d", "source": "risk", "target": "decision"},
    ]
    return TreeStructure(nodes=nodes, edges=edges)

@router.get("/status", response_model=List[NodeStatus])
async def get_node_statuses():
    """返回 AI 节点的实时状态 (Mock)"""
    # 模拟随机状态变化
    statuses = ["idle", "working", "success"]
    tasks = ["正在扫描市场...", "分析 BTC 走势...", "计算风险敞口...", "等待信号...", "处理链上数据...", "情绪指标更新..."]
    
    return [
        NodeStatus(id="macro", status=random.choice(statuses), current_task=random.choice(tasks), last_update=datetime.now()),
        NodeStatus(id="tech", status=random.choice(statuses), current_task="RSI 背离检测中", last_update=datetime.now()),
        NodeStatus(id="fund", status="working", current_task="抓取链上鲸鱼数据", last_update=datetime.now()),
        NodeStatus(id="risk", status="idle", current_task="待机", last_update=datetime.now()),
        NodeStatus(id="decision", status=random.choice(statuses), current_task="聚合多方信号", last_update=datetime.now()),
    ]

@router.get("/decisions", response_model=List[DecisionResponse])
async def get_ai_decisions(limit: int = 20):
    """获取 AI 决策历史 (Mock)"""
    return [
        DecisionResponse(
            id=1,
            decision_type="BUY_SIGNAL",
            symbol="BTCUSDT",
            action="BUY",
            reason="Strong technical breakout + positive sentiment",
            confidence=0.85,
            timestamp=datetime.now(),
            details={"indicators": {"RSI": 65, "MACD": "Bullish"}, "sentiment": "Greed"}
        ),
        DecisionResponse(
            id=2,
            decision_type="HOLD",
            symbol="ETHUSDT",
            action="HOLD",
            reason="Conflicting signals",
            confidence=0.45,
            timestamp=datetime.now(),
            details={}
        )
    ]

@router.get("/communications", response_model=List[CommunicationResponse])
async def get_ai_communications(limit: int = 50):
    """获取 AI 间的通信记录 (Mock)"""
    return [
        CommunicationResponse(
            sender="Macro Strategy",
            receiver="Tech Analyst",
            message_content="Analyze BTC 4H chart for breakout pattern",
            timestamp=datetime.now(),
            message_type="TASK"
        ),
        CommunicationResponse(
            sender="Tech Analyst",
            receiver="Decision Maker",
            message_content="BTC showing Golden Cross on 1D",
            timestamp=datetime.now(),
            message_type="REPORT"
        )
    ]
