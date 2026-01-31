from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from src.database.operations import db

router = APIRouter()

# --- Models ---
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

@router.get("/decisions", response_model=List[DecisionResponse])
async def get_ai_decisions(limit: int = 20):
    """获取 AI 决策历史"""
    try:
        decisions = db.get_decisions(limit=limit)
        return [
            DecisionResponse(
                id=d.id,
                decision_type=d.decision_type,
                symbol=d.symbol,
                action=d.action,
                reason=d.reason,
                confidence=d.confidence,
                timestamp=d.timestamp,
                details=d.decision_data if isinstance(d.decision_data, dict) else {}
            ) for d in decisions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/communications", response_model=List[CommunicationResponse])
async def get_ai_communications(limit: int = 50):
    """获取 AI 间的通信记录"""
    try:
        comms = db.get_communications(limit=limit)
        return [
            CommunicationResponse(
                sender=c.sender,
                receiver=c.receiver,
                message_content=c.content,
                timestamp=c.timestamp,
                message_type=c.message_type
            ) for c in comms
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
