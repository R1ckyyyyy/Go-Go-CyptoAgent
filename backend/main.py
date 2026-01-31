import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys
import os

# 确保 src 目录在 python path 中
sys.path.append(os.path.join(os.path.dirname(__file__)))

from src.api.system import router as system_router
from src.api.account import router as account_router
from src.api.trading import router as trading_router
from src.api.ai import router as ai_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("System Starting Up...")
    # TODO: 初始化数据库连接、加载模型等
    yield
    logger.info("System Shutting Down...")

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
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo for now, or handle commands
            await manager.broadcast(f"Server received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
