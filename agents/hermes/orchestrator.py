"""Agent orchestration and workflow management."""

import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime

from .agent import Agent
from .task import Task, TaskResult, TaskStatus
from .registry import get_registry


@dataclass
class WorkflowStep:
    """Single step in a workflow."""
    agent_id: str
    task_id: str
    input_key: Optional[str] = None
    output_key: str = "output"
    dependencies: List[str] = field(default_factory=list)


@dataclass
class WorkflowDefinition:
    """Workflow definition with multiple steps."""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep] = field(default_factory=list)
    timeout: Optional[float] = None


class Orchestrator:
    """Agent orchestrator for managing multi-agent workflows."""
    
    def __init__(self):
        """Initialize orchestrator."""
        self.registry = get_registry()
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.workflow_results: Dict[str, Dict[str, Any]] = {}
        self.created_at = datetime.now()
    
    def register_workflow(self, workflow: WorkflowDefinition) -> None:
        """Register a workflow definition."""
        if workflow.id in self.workflows:
            raise ValueError(f"Workflow {workflow.id} already registered")
        self.workflows[workflow.id] = workflow
    
    async def execute_workflow(self, workflow_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a complete workflow."""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        context = context or {}
        results = {}
        
        # Sort steps by dependencies
        executed = set()
        remaining_steps = list(workflow.steps)
        
        while remaining_steps:
            ready_steps = [
                step for step in remaining_steps
                if all(dep in executed for dep in step.dependencies)
            ]
            
            if not ready_steps:
                raise RuntimeError(f"Workflow {workflow_id} has circular dependencies")
            
            # Execute ready steps concurrently
            step_tasks = []
            for step in ready_steps:
                task = self._execute_step(step, context, results)
                step_tasks.append(task)
            
            step_results = await asyncio.gather(*step_tasks, return_exceptions=True)
            
            for step, result in zip(ready_steps, step_results):
                if isinstance(result, Exception):
                    results[step.task_id] = {"error": str(result), "status": "failed"}
                else:
                    results[step.task_id] = result
                executed.add(step.task_id)
                remaining_steps.remove(step)
        
        self.workflow_results[workflow_id] = results
        return results
    
    async def _execute_step(self, step: WorkflowStep, context: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step."""
        agent = self.registry.get_agent(step.agent_id)
        if not agent:
            return {"error": f"Agent {step.agent_id} not found", "status": "failed"}
        
        # Prepare input
        step_input = context.copy()
        if step.input_key and step.input_key in results:
            step_input.update(results[step.input_key])
        
        # Execute task
        try:
            result = await agent.execute_task(step.task_id, **step_input)
            return {
                "status": result.status.value,
                "output": result.output,
                "duration": result.duration_seconds,
                "error": result.error
            }
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    async def parallel_execute(self, agent_ids: List[str], task_id: str) -> Dict[str, TaskResult]:
        """Execute same task across multiple agents in parallel."""
        tasks = []
        for agent_id in agent_ids:
            agent = self.registry.get_agent(agent_id)
            if agent:
                tasks.append(agent.execute_task(task_id))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return dict(zip(agent_ids, results))
    
    async def route_to_capable_agent(self, capability: str, task_id: str, *args, **kwargs) -> Optional[TaskResult]:
        """Route task to an agent with specific capability."""
        agent = self.registry.get_agent_by_capability(capability)
        if not agent:
            return None
        
        return await agent.execute_task(task_id, *args, **kwargs)
    
    async def broadcast_to_capable_agents(self, capability: str, task_id: str, *args, **kwargs) -> Dict[str, TaskResult]:
        """Broadcast task to all agents with specific capability."""
        agents = self.registry.get_agents_by_capability(capability)
        results = {}
        
        for agent in agents:
            result = await agent.execute_task(task_id, *args, **kwargs)
            results[agent.name] = result
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        return {
            "created_at": self.created_at.isoformat(),
            "registered_workflows": len(self.workflows),
            "executed_workflows": len(self.workflow_results),
            "registered_agents": len(self.registry.list_agents()),
            "workflow_ids": list(self.workflows.keys())
        }
