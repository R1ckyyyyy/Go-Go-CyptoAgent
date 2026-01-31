from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

router = APIRouter()

# --- Models ---
class SystemStatus(BaseModel):
    status: str
    uptime: str
    active_agents: int
    last_update: datetime

class ConfigUpdate(BaseModel):
    config: Dict[str, Any]

# --- Mock State (后续连接真实状态) ---
SYSTEM_STATE = {
    "status": "idle",
    "start_time": datetime.now()
}

@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    """获取系统当前运行状态"""
    now = datetime.now()
    uptime = str(now - SYSTEM_STATE["start_time"]).split('.')[0]
    
    return SystemStatus(
        status=SYSTEM_STATE["status"],
        uptime=uptime,
        active_agents=0, # TODO: connect to agent manager
        last_update=now
    )

@router.post("/start")
async def start_system():
    """启动自动交易系统"""
    SYSTEM_STATE["status"] = "running"
    return {"message": "System started", "status": "running"}

@router.post("/stop")
async def stop_system():
    """停止自动交易系统"""
    SYSTEM_STATE["status"] = "stopped"
    return {"message": "System stopped", "status": "stopped"}

@router.get("/config")
async def get_config():
    """获取当前系统配置"""
    # TODO: 从数据库或配置管理器读取
    return {"mode": "live", "risk_level": "medium"}
