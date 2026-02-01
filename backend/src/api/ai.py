from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import json
from src.database.operations import db
from src.database.models import DecisionLayer, TriggerStatus

router = APIRouter()

# --- Models ---
class NodePosition(BaseModel):
    x: float
    y: float

class AINode(BaseModel):
    id: str
    label: str
    type: str  # coordinator, consultant, execution
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
    symbol: Optional[str] = None
    action: Optional[str] = None
    reason: str
    confidence: Optional[float] = None
    timestamp: datetime
    details: Dict[str, Any]

class ActiveTrigger(BaseModel):
    id: int
    description: str
    type: str
    condition: Dict[str, Any]
    created_at: datetime

# --- Routes ---

@router.get("/tree-structure", response_model=TreeStructure)
async def get_tree_structure():
    """
    返回 "星型架构" (Coordinator + Consultants)
    """
    nodes = [
        {
            "id": "coordinator", 
            "label": "中央决策大脑", 
            "type": "coordinator", 
            "position": {"x": 350, "y": 80}, 
            "description": "Coordinator AI: 负责整合各方信息，做出最终交易决策。"
        },
        {
            "id": "technical", 
            "label": "技术分析顾问", 
            "type": "consultant", 
            "position": {"x": 0, "y": 320}, 
            "description": "Trend Analyst: 专注于K线形态、RSI、MACD等技术指标分析。"
        },
        {
            "id": "fundamental", 
            "label": "基本面顾问", 
            "type": "consultant", 
            "position": {"x": 350, "y": 320}, 
            "description": "News Analyst: 监控重大新闻、宏观经济数据和链上异动。"
        },
        {
            "id": "risk", 
            "label": "风控顾问", 
            "type": "consultant", 
            "position": {"x": 700, "y": 320}, 
            "description": "Risk Manager: 评估持仓风险，计算止损位和最大回撤。"
        },
        {
            "id": "execution", 
            "label": "执行终端", 
            "type": "execution", 
            "position": {"x": 350, "y": 550}, 
            "description": "Executor: 负责将决策转化为具体的交易所订单并监控成交。"
        },
    ]
    edges = [
        {"id": "e-c-t", "source": "coordinator", "target": "technical"},
        {"id": "e-c-f", "source": "coordinator", "target": "fundamental"},
        {"id": "e-c-r", "source": "coordinator", "target": "risk"},
        {"id": "e-c-e", "source": "coordinator", "target": "execution"},
    ]
    return TreeStructure(nodes=nodes, edges=edges)

@router.get("/status", response_model=List[NodeStatus])
async def get_node_statuses():
    """
    从实盘 DB 获取 AI 状态
    1. Coordinator: 检查是否有活跃 Trigger (Watching)
    2. Consultants: 默认为 Idle (被动调用)，除非最近 log 显示正在被咨询
    """
    # 获取最近一次决策
    decisions = db.get_decisions(limit=1)
    last_decision = decisions[0] if decisions else None
    
    # 获取活跃 Triggers
    active_triggers = db.get_active_triggers()
    
    # Coordinator Status
    coord_status = "idle"
    coord_task = "Waiting for events"
    
    if active_triggers:
        coord_status = "working"
        coord_task = f"Monitoring {len(active_triggers)} triggers (Watchdog Active)"
        
    if last_decision:
        time_diff = (datetime.utcnow() - last_decision.timestamp).total_seconds()
        if time_diff < 120: # 2分钟内的决策视为 "Active Thinking"
            coord_status = "success"
            coord_task = f"Recent: {last_decision.decision_type}"

    now = datetime.utcnow()
    
    statuses = [
        NodeStatus(id="coordinator", status=coord_status, current_task=coord_task, last_update=now),
        NodeStatus(id="technical", status="idle", current_task="Standby", last_update=now),
        NodeStatus(id="fundamental", status="idle", current_task="Standby", last_update=now),
        NodeStatus(id="risk", status="idle", current_task="Standby", last_update=now),
        NodeStatus(id="execution", status="idle", current_task="Ready", last_update=now),
    ]
    
    return statuses

@router.get("/decisions", response_model=List[DecisionResponse])
async def get_ai_decisions(limit: int = 20):
    """获取真实 AI 决策历史 (From DB)"""
    db_decisions = db.get_decisions(limit=limit)
    response = []
    
    for d in db_decisions:
        # Parse JSON fields safely
        try:
            output = d.output_recommendation
            if isinstance(output, str):
                output = json.loads(output)
            
            action_data = output.get('action', {})
            decision_type = d.decision_type
            action = action_data.get('type', "UNKNOWN")
            reason = output.get('reasoning', "No reasoning provided")
            
            # Extract confidence if available
            confidence = d.confidence
            
            response.append(DecisionResponse(
                id=d.id,
                decision_type=decision_type,
                symbol="BTCUSDT", # TODO: store per row
                action=action,
                reason=reason,
                confidence=confidence,
                timestamp=d.timestamp,
                details=output
            ))
        except Exception as e:
            print(f"Error parsing decision {d.id}: {e}")
            
    return response

@router.post("/analyze")
async def trigger_manual_analysis():
    """
    【人工干预】
    用户点击 "立即分析" 按钮。
    机制：插入一个 status=ACTIVE, type=MANUAL 的高优先级触发器。
    Watchdog 发现后会立即执行。
    """
    trigger_data = {
        "description": "User requested manual analysis",
        "trigger_type": "MANUAL",
        "condition_data": {"operator": "IMMEDIATE", "value": 0}
    }
    trigger_id = db.add_trigger(trigger_data)
    
    if trigger_id == -1:
         # Handle error case (logs usually capture it)
         return {"message": "Failed to queue analysis.", "error": True}

    return {"message": "Analysis queued.", "trigger_id": trigger_id}

@router.get("/triggers", response_model=List[ActiveTrigger])
async def get_active_triggers():
    """获取当前所有活跃的 Watchdog 触发器"""
    triggers = db.get_active_triggers()
    res = []
    for t in triggers:
        try:
            cond = t.condition_data
            if isinstance(cond, str):
                cond = json.loads(cond)
            res.append(ActiveTrigger(
                id=t.id,
                description=t.description,
                type=t.trigger_type,
                condition=cond,
                created_at=t.created_at
            ))
        except Exception:
            pass
    return res
