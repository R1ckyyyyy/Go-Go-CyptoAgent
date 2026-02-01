import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys
import os
from dotenv import load_dotenv

# Load .env from current directory (backend/)
load_dotenv()

# 确保 src 目录在 python path 中
sys.path.append(os.path.join(os.path.dirname(__file__)))

import logging

# Filter out /status logs (Health checks)
class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.args and len(record.args) >= 3 and "/status" not in str(record.args[2])

logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

from src.api.system import router as system_router
from src.api.account import router as account_router
from src.api.trading import router as trading_router
from src.api.ai import router as ai_router

import asyncio
from src.service_coordinator import start_coordinator_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("System Starting Up...")
    
    # Initialize DB (Optional check)
    
    # 🚀 Start Coordinator Background Service
    # This runs the Watchdog loop in parallel with the API
    coordinator_task = asyncio.create_task(start_coordinator_service())
    
    yield
    
    logger.info("System Shutting Down...")
    coordinator_task.cancel()
    try:
        await coordinator_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="Crypto Trading AI System",
    description="Backend API for the Agentic Crypto Trading System",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(system_router, prefix="/api/system", tags=["System"])
app.include_router(account_router, prefix="/api/account", tags=["Account"])
app.include_router(trading_router, prefix="/api/trading", tags=["Trading"])
app.include_router(ai_router, prefix="/api/ai", tags=["AI"])

@app.get("/")
async def root():
    return {"message": "Crypto Trading AI Agent API is Running"}

# --- WebSocket Manager ---
from fastapi import WebSocket, WebSocketDisconnect
from src.utils.websocket import ws_manager

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo for now (or handle commands from frontend)
            # await ws_manager.broadcast(f"Server received: {data}")
            pass 
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
