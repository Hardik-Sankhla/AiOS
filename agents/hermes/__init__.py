"""Hermes agent framework - Pure Python agent orchestration."""

from .agent import Agent, AgentConfig
from .task import Task, TaskResult, TaskStatus, TaskPriority
from .registry import AgentRegistry, get_registry
from .orchestrator import Orchestrator, WorkflowDefinition, WorkflowStep

__all__ = [
    # Agent classes
    "Agent",
    "AgentConfig",
    # Task classes
    "Task",
    "TaskResult",
    "TaskStatus",
    "TaskPriority",
    # Registry
    "AgentRegistry",
    "get_registry",
    # Orchestration
    "Orchestrator",
    "WorkflowDefinition",
    "WorkflowStep",
]

__version__ = "0.1.0"
__author__ = "AIOS"
__description__ = "Pure Python agent orchestration framework"
