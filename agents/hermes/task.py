"""Task definition and execution interface for Hermes agents."""

from dataclasses import dataclass, field
from typing import Any, Optional, Callable, Dict, List
from enum import Enum
import asyncio
from datetime import datetime


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task execution priority."""
    LOW = 3
    NORMAL = 2
    HIGH = 1
    CRITICAL = 0


@dataclass
class TaskResult:
    """Result of task execution."""
    task_id: str
    status: TaskStatus
    output: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0


@dataclass
class Task:
    """Executable task definition."""
    
    id: str
    name: str
    description: str
    handler: Optional[Callable] = None
    priority: TaskPriority = TaskPriority.NORMAL
    timeout: Optional[float] = None
    retries: int = 0
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate task definition."""
        if not self.id:
            raise ValueError("Task ID cannot be empty")
        if not self.name:
            raise ValueError("Task name cannot be empty")
    
    async def execute(self, *args, **kwargs) -> TaskResult:
        """Execute task with timeout and retry logic."""
        start_time = datetime.now()
        attempt = 0
        last_error = None
        
        while attempt <= self.retries:
            try:
                if self.handler is None:
                    raise RuntimeError(f"No handler defined for task {self.id}")
                
                # Handle both sync and async handlers
                if asyncio.iscoroutinefunction(self.handler):
                    output = await asyncio.wait_for(
                        self.handler(*args, **kwargs),
                        timeout=self.timeout
                    )
                else:
                    output = await asyncio.wait_for(
                        asyncio.to_thread(self.handler, *args, **kwargs),
                        timeout=self.timeout
                    )
                
                completed_at = datetime.now()
                duration = (completed_at - start_time).total_seconds()
                
                return TaskResult(
                    task_id=self.id,
                    status=TaskStatus.COMPLETED,
                    output=output,
                    completed_at=completed_at,
                    duration_seconds=duration,
                    metadata={"attempts": attempt + 1}
                )
            
            except asyncio.TimeoutError:
                last_error = f"Task timeout after {self.timeout}s"
                attempt += 1
                if attempt <= self.retries:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
            except Exception as e:
                last_error = str(e)
                attempt += 1
                if attempt <= self.retries:
                    await asyncio.sleep(2 ** attempt)
        
        completed_at = datetime.now()
        duration = (completed_at - start_time).total_seconds()
        
        return TaskResult(
            task_id=self.id,
            status=TaskStatus.FAILED,
            error=last_error,
            completed_at=completed_at,
            duration_seconds=duration,
            metadata={"attempts": self.retries + 1, "failed": True}
        )
