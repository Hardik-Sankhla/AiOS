"""Base agent class and interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
import asyncio
from datetime import datetime

from .task import Task, TaskResult, TaskStatus


@dataclass
class AgentConfig:
    """Agent configuration."""
    name: str
    description: str
    capabilities: List[str] = field(default_factory=list)
    memory_enabled: bool = True
    max_concurrent_tasks: int = 3
    timeout: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class Agent(ABC):
    """Base agent class."""
    
    def __init__(self, config: AgentConfig):
        """Initialize agent."""
        self.config = config
        self.tasks: Dict[str, Task] = {}
        self.results: Dict[str, TaskResult] = {}
        self.memory: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self._running_tasks = set()
    
    @property
    def name(self) -> str:
        """Agent name."""
        return self.config.name
    
    @property
    def description(self) -> str:
        """Agent description."""
        return self.config.description
    
    @property
    def capabilities(self) -> List[str]:
        """List of agent capabilities."""
        return self.config.capabilities
    
    def register_task(self, task: Task) -> None:
        """Register a task with the agent."""
        if task.id in self.tasks:
            raise ValueError(f"Task {task.id} already registered")
        self.tasks[task.id] = task
    
    def unregister_task(self, task_id: str) -> None:
        """Unregister a task from the agent."""
        if task_id in self.tasks:
            del self.tasks[task_id]
    
    async def execute_task(self, task_id: str, *args, **kwargs) -> TaskResult:
        """Execute a registered task."""
        if task_id not in self.tasks:
            return TaskResult(
                task_id=task_id,
                status=TaskStatus.FAILED,
                error=f"Task {task_id} not found"
            )
        
        # Wait for slot if at capacity
        while len(self._running_tasks) >= self.config.max_concurrent_tasks:
            await asyncio.sleep(0.1)
        
        task = self.tasks[task_id]
        self._running_tasks.add(task_id)
        
        try:
            result = await task.execute(*args, **kwargs)
            self.results[task_id] = result
            return result
        finally:
            self._running_tasks.discard(task_id)
    
    async def execute_workflow(self, task_ids: List[str], *args, **kwargs) -> Dict[str, TaskResult]:
        """Execute multiple tasks with dependency handling."""
        results = {}
        completed = set()
        
        while len(completed) < len(task_ids):
            ready_tasks = []
            
            for task_id in task_ids:
                if task_id not in completed:
                    task = self.tasks.get(task_id)
                    if task and all(dep in completed for dep in task.dependencies):
                        ready_tasks.append(task_id)
            
            if not ready_tasks:
                break
            
            # Execute ready tasks concurrently
            task_coros = [
                self.execute_task(task_id, *args, **kwargs)
                for task_id in ready_tasks
            ]
            
            results.update(dict(zip(ready_tasks, await asyncio.gather(*task_coros))))
            completed.update(ready_tasks)
        
        return results
    
    def store_memory(self, key: str, value: Any) -> None:
        """Store data in agent memory."""
        if self.config.memory_enabled:
            self.memory[key] = value
    
    def retrieve_memory(self, key: str, default: Any = None) -> Any:
        """Retrieve data from agent memory."""
        return self.memory.get(key, default)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        completed = sum(1 for r in self.results.values() if r.status == TaskStatus.COMPLETED)
        failed = sum(1 for r in self.results.values() if r.status == TaskStatus.FAILED)
        
        return {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "tasks_registered": len(self.tasks),
            "tasks_completed": completed,
            "tasks_failed": failed,
            "memory_items": len(self.memory),
            "capabilities": self.capabilities
        }
    
    @abstractmethod
    async def think(self, context: str) -> str:
        """Agent thinking/planning step - must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def act(self, action: str, context: str) -> Any:
        """Agent action/execution step - must be implemented by subclasses."""
        pass
