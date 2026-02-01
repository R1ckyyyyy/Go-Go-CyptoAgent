from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import asyncio
import json
import os
from datetime import datetime
from anthropic import AsyncAnthropic
# Google GenAI Import
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

from src.ai_agents.communication import CommunicationChannel, AgentMessage, MessageType
from src.database.operations import db
from src.utils.logger import logger
from src.database.models import DecisionLayer

class BaseAgent(ABC):
    """
    AI代理基类
    支持 Claude (Anthropic) 和 Gemini (Google) 双后端
    """

    def __init__(
        self, 
        agent_id: str, 
        agent_type: str, 
        role_description: str,
        layer: DecisionLayer
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.role_description = role_description
        self.layer = layer
        
        # 消息通道
        self.channel = CommunicationChannel()
        self.channel.subscribe(self.agent_id, self.handle_message)
        
        # 记忆
        self.memory: List[Dict] = []
        self.max_memory_size = 20

        # LLM Provider Config
        # 优先通过环境变量选择: "anthropic" or "gemini"
        self.provider = os.getenv("LLM_PROVIDER", "anthropic").lower() 
        
        # --- Anthropic Client ---
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY") 
        self.claude_client = None
        if self.anthropic_key:
             self.claude_client = AsyncAnthropic(api_key=self.anthropic_key)
        
        self.claude_model = "claude-3-5-sonnet-20240620"

        # --- Gemini Client ---
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.gemini_client = None
        # 模型选择策略 (分级配置)
        if self.provider == "gemini":
            # 默认回退 (Base)
            self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
            
            # 根据层级覆盖 (Smart vs Fast)
            if self.layer in [DecisionLayer.MACRO, DecisionLayer.EXECUTION]:
                # 复杂推理/决策 -> Smart Model (e.g. Pro)
                self.gemini_model = os.getenv("GEMINI_MODEL_SMART", self.gemini_model)
            elif self.layer == DecisionLayer.ANALYSIS:
                # 快速分析 -> Fast Model (e.g. Flash)
                self.gemini_model = os.getenv("GEMINI_MODEL_FAST", self.gemini_model)
                
            logger.info(f"Agent {self.agent_id} ({self.layer}) initialized with Gemini Model: {self.gemini_model}")

        if self.gemini_key and HAS_GENAI:
            self.gemini_client = genai.Client(api_key=self.gemini_key)
        elif self.provider == "gemini" and not self.gemini_key:
            logger.warning("Provider set to Gemini but GEMINI_API_KEY not found.")
    
    @abstractmethod
    async def process(self, input_data: Any) -> Dict[str, Any]:
        """核心处理逻辑，子类需实现"""
        pass
    
    async def handle_message(self, message: AgentMessage):
        """处理收到的消息"""
        logger.info(f"Agent {self.agent_id} received message: {message.message_type} from {message.sender}")
        
    async def communicate(self, to_agent: str, message_type: MessageType, content: Dict[str, Any]):
        """发送消息给其他Agent"""
        msg = AgentMessage(
            sender=self.agent_id,
            receiver=to_agent,
            message_type=message_type,
            content=content
        )
        await self.channel.publish(msg)

    async def call_llm(
        self,
        system_prompt: str,
        user_content: str,
        temperature: float = 0.7,
        tools: Optional[List[Dict]] = None
    ) -> str:
        """通用 LLM 调用接口，根据 self.provider 路由"""
        if self.provider == "gemini":
            return await self.call_gemini(system_prompt, user_content, temperature, tools)
        else:
            return await self.call_claude(system_prompt, user_content, temperature, tools)

    async def call_gemini(
        self,
        system_prompt: str,
        user_content: str,
        temperature: float = 0.7,
        tools: Optional[List[Dict]] = None
    ) -> str:
        """调用 Google Gemini API using google-genai library"""
        if not self.gemini_client:
            raise ValueError("Gemini Client not initialized. Check GEMINI_API_KEY.")
            
        try:
            # 构建配置
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                max_output_tokens=4096 
                # tools=tools # TODO: 适配 Tools 格式
            )
            
            response = await self.gemini_client.aio.models.generate_content(
                model=self.gemini_model,
                contents=user_content,
                config=config
            )
            
            return response.text

        except Exception as e:
            logger.error(f"Error calling Gemini API for agent {self.agent_id}: {e}")
            raise e

    async def call_claude(
        self, 
        system_prompt: str, 
        user_content: str, 
        temperature: float = 0.7,
        tools: Optional[List[Dict]] = None
    ) -> str:
        """调用 Claude API (如果 Provider 是 Gemini，自动重定向到 call_llm 以防止死循环推荐用 call_llm)"""
        if self.provider == "gemini":
             # 如果子类显式调用 call_claude 但全局配置是 Gemini，我们尝试在此处重定向
             # 注意：这可能会因为参数格式微小差异导致问题，但对于纯文本 IO 是安全的
             return await self.call_gemini(system_prompt, user_content, temperature, tools)
             
        if not self.claude_client:
             raise ValueError("Claude client not initialized. Check ANTHROPIC_API_KEY.")

        messages = [{"role": "user", "content": user_content}]
        
        # 添加短期上下文 (简化)
        if self.memory:
            pass

        try:
            kw_args = {
                "model": self.claude_model,
                "max_tokens": 4096,
                "temperature": temperature,
                "system": system_prompt,
                "messages": messages,
            }
            if tools:
                kw_args["tools"] = tools

            response = await self.claude_client.messages.create(**kw_args)
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Error calling Claude API for agent {self.agent_id}: {e}")
            raise e

    def add_memory(self, content: Dict):
        """添加记忆"""
        self.memory.append({
            "timestamp": datetime.now().isoformat(),
            "content": content
        })
        if len(self.memory) > self.max_memory_size:
            self.memory.pop(0)

    async def log_decision(self, decision_data: Dict[str, Any], confidence: float):
        """记录决策到数据库"""
        record = {
            "decision_type": decision_data.get("decision", "UNKNOWN"),
            "input_data": decision_data.get("input_summary", {}), 
            "output_recommendation": decision_data,
            "confidence": confidence,
            "layer": self.layer,
            "timestamp": datetime.utcnow()
        }
        try:
            db.log_decision(record)
        except Exception as e:
            logger.error(f"Failed to log decision: {e}")

    async def use_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """
        执行工具
        目前为基础框架，后续对接 ToolRegistry
        """
        logger.info(f"Agent {self.agent_id} calling tool: {tool_name} with {params}")
        
        # 临时 Mock 实现，后续替换为真实的 tool_registry.execute(tool_name, params)
        if tool_name == "get_market_data":
            return {"symbol": params.get("symbol"), "price": 42000.0, "source": "mock"}
        elif tool_name == "calculator":
            # 简单的示例工具
            expr = params.get("expression")
            try:
                return eval(expr)
            except:
                return "Error"
                
        return f"Tool {tool_name} executed successfully (Mock)"
