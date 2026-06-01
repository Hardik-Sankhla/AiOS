"""Hermes Agent Framework - Lightweight autonomous agent orchestration."""

import asyncio
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskResult:
    """Task execution result."""
    task_id: str
    status: TaskStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class HermesAgent:
    """Lightweight autonomous agent."""
    
    def __init__(self, name: str):
        """Initialize agent.
        
        Args:
            name: Agent name
        """
        self.name = name
        self.tasks: Dict[str, TaskResult] = {}
        self.handlers: Dict[str, Callable] = {}
    
    def register_handler(self, task_type: str, handler: Callable):
        """Register a task handler.
        
        Args:
            task_type: Task type identifier
            handler: Async callable handler
        """
        self.handlers[task_type] = handler
    
    async def run_task(self, task_id: str, task_type: str, **kwargs) -> TaskResult:
        """Run a task.
        
        Args:
            task_id: Unique task identifier
            task_type: Task type
            **kwargs: Task parameters
            
        Returns:
            TaskResult with execution details
        """
        if task_type not in self.handlers:
            return TaskResult(
                task_id=task_id,
                status=TaskStatus.FAILED,
                error=f"Unknown task type: {task_type}"
            )
        
        result = TaskResult(
            task_id=task_id,
            status=TaskStatus.RUNNING,
            started_at=datetime.now()
        )
        self.tasks[task_id] = result
        
        try:
            handler = self.handlers[task_type]
            output = await handler(**kwargs)
            result.status = TaskStatus.COMPLETED
            result.result = output
        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error = str(e)
        finally:
            result.completed_at = datetime.now()
        
        return result


class HermesOrchestrator:
    """Orchestrates multiple agents."""
    
    def __init__(self):
        """Initialize orchestrator."""
        self.agents: Dict[str, HermesAgent] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
    
    def register_agent(self, agent: HermesAgent):
        """Register an agent.
        
        Args:
            agent: HermesAgent instance
        """
        self.agents[agent.name] = agent
    
    async def dispatch_task(
        self,
        agent_name: str,
        task_id: str,
        task_type: str,
        **kwargs
    ) -> TaskResult:
        """Dispatch a task to an agent.
        
        Args:
            agent_name: Target agent name
            task_id: Task identifier
            task_type: Task type
            **kwargs: Task parameters
            
        Returns:
            TaskResult
        """
        if agent_name not in self.agents:
            return TaskResult(
                task_id=task_id,
                status=TaskStatus.FAILED,
                error=f"Agent not found: {agent_name}"
            )
        
        agent = self.agents[agent_name]
        return await agent.run_task(task_id, task_type, **kwargs)


# Factory for common agents
def create_executor_agent() -> HermesAgent:
    """Create an executor agent."""
    agent = HermesAgent("executor")
    
    async def execute_command(command: str) -> str:
        """Execute a shell command."""
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(stderr.decode())
        return stdout.decode()
    
    agent.register_handler("execute", execute_command)
    return agent
