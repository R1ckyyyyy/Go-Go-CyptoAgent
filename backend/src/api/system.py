from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

router = APIRouter()

from src.database.operations import db

# --- Models ---
class SystemStatus(BaseModel):
    status: str # RUNNING | STOPPED
    uptime: str
    active_agents: int
    last_update: datetime
    message: str = ""

# --- Routes ---

@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    """获取系统当前运行状态 (From DB)"""
    status = db.get_config("system_status", "STOPPED")
    last_heartbeat = db.get_config("system_heartbeat", "")
    
    # Calculate crude uptime or liveliness
    msg = "System is offline"
    if status == "RUNNING":
        msg = "System is actively monitoring markets."
        
    return SystemStatus(
        status=status,
        uptime="N/A", # TODO: Store start time in DB
        active_agents=1, # Coordinator
        last_update=datetime.now(),
        message=f"{msg} (Last Pulse: {last_heartbeat})"
    )

@router.post("/start")
async def start_system():
    """启动自动交易系统"""
    db.set_config("system_status", "RUNNING")
    return {"message": "System start command sent.", "status": "RUNNING"}

@router.post("/stop")
async def stop_system():
    """停止自动交易系统"""
    db.set_config("system_status", "STOPPED")
    return {"message": "System stop command sent.", "status": "STOPPED"}

@router.get("/config")
async def get_config():
    """获取当前系统配置"""
    mode = db.get_config("trading_mode", "PAPER")
    return {"mode": mode}
