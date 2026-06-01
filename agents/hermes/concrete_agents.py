"""Concrete agent implementations for research and coding tasks."""

import asyncio
from typing import Any, Dict, Optional
import sys
sys.path.insert(0, '/data/data/com.termux/files/home/storage/shared/projects/AIOS')

from .agent import Agent, AgentConfig
from services.llm import LLMClient


class ResearchAgent(Agent):
    """Agent specialized in research tasks."""
    
    def __init__(self, config: AgentConfig, llm_client: Optional[LLMClient] = None):
        """Initialize research agent."""
        super().__init__(config)
        self.llm_client = llm_client
    
    async def think(self, context: str) -> str:
        """Research thinking step - analyze and plan research approach."""
        if not self.llm_client:
            return "No LLM client configured"
        
        messages = [
            {
                "role": "system",
                "content": "You are a research expert. Analyze the research query and provide a structured research plan."
            },
            {
                "role": "user",
                "content": f"Research query: {context}\n\nProvide a research approach with key areas to investigate."
            }
        ]
        
        response = await self.llm_client.chat_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response["choices"][0]["message"]["content"]
    
    async def act(self, action: str, context: str) -> Any:
        """Research action step - execute research task."""
        if not self.llm_client:
            return {"error": "No LLM client configured"}
        
        messages = [
            {
                "role": "system",
                "content": "You are a research expert conducting research."
            },
            {
                "role": "user",
                "content": f"Action: {action}\nContext: {context}\n\nExecute this research action and provide findings."
            }
        ]
        
        response = await self.llm_client.chat_completion(
            messages=messages,
            temperature=0.5,
            max_tokens=800
        )
        
        findings = response["choices"][0]["message"]["content"]
        self.store_memory(f"research_{action}", findings)
        
        return {
            "action": action,
            "findings": findings,
            "provider": response.get("x-routed-via", "unknown")
        }


class CodingAgent(Agent):
    """Agent specialized in coding tasks."""
    
    def __init__(self, config: AgentConfig, llm_client: Optional[LLMClient] = None):
        """Initialize coding agent."""
        super().__init__(config)
        self.llm_client = llm_client
    
    async def think(self, context: str) -> str:
        """Coding thinking step - analyze and plan implementation."""
        if not self.llm_client:
            return "No LLM client configured"
        
        messages = [
            {
                "role": "system",
                "content": "You are a senior software engineer. Analyze the coding task and provide a detailed implementation plan."
            },
            {
                "role": "user",
                "content": f"Coding task: {context}\n\nProvide an implementation plan with architecture, key components, and best practices."
            }
        ]
        
        response = await self.llm_client.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=600
        )
        
        return response["choices"][0]["message"]["content"]
    
    async def act(self, action: str, context: str) -> Any:
        """Coding action step - execute coding task."""
        if not self.llm_client:
            return {"error": "No LLM client configured"}
        
        messages = [
            {
                "role": "system",
                "content": "You are a senior software engineer writing production code."
            },
            {
                "role": "user",
                "content": f"Action: {action}\nContext: {context}\n\nWrite clean, well-documented code for this task."
            }
        ]
        
        response = await self.llm_client.chat_completion(
            messages=messages,
            temperature=0.2,
            max_tokens=1000
        )
        
        code = response["choices"][0]["message"]["content"]
        self.store_memory(f"code_{action}", code)
        
        return {
            "action": action,
            "code": code,
            "provider": response.get("x-routed-via", "unknown")
        }
