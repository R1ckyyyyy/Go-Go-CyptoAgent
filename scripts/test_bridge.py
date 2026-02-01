import asyncio
import os
import sys

# Mocking things to run in isolation
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from src.ai_agents.communication import CommunicationChannel, AgentMessage, MessageType

async def mock_ws_broadcast(payload):
    print(f"✅ [WS MOCK] Broadcasting: {payload}")

async def bridge_to_ws(msg: AgentMessage):
    print(f"🌉 [BRIDGE] bridging {msg.message_type}...")
    await mock_ws_broadcast({
        "type": "THOUGHT_STREAM",
        "content": msg.content
    })

async def main():
    print("Testing Communication Channel...")
    channel = CommunicationChannel()
    
    # 1. Subscribe
    channel.subscribe("all", bridge_to_ws)
    print("Subscribed to 'all'")
    
    # 2. Publish Async
    msg = AgentMessage(
        sender="coordinator",
        receiver="all",
        message_type=MessageType.STATUS_UPDATE,
        content={"status": "TESTING"}
    )
    
    print(f"Publishing message: {msg.message_type}")
    await channel.publish(msg)
    
    # Allow loop to cycle
    await asyncio.sleep(0.1)
    print("Test Complete.")

if __name__ == "__main__":
    asyncio.run(main())
