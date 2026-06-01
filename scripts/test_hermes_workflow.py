"""Test Hermes agent workflow demonstration."""

import asyncio
import sys
from pathlib import Path

# Add AIOS to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.hermes import (
    Agent, AgentConfig,
    Task, TaskStatus, TaskPriority,
    get_registry, Orchestrator,
    WorkflowDefinition, WorkflowStep
)
from agents.hermes.concrete_agents import ResearchAgent, CodingAgent


async def test_hermes_workflow():
    """Test a complete Hermes workflow."""
    
    print("=" * 70)
    print("PHASE 4 STEP 4: HERMES AGENT WORKFLOW DEMONSTRATION")
    print("=" * 70)
    
    # Get registry
    registry = get_registry()
    registry.clear()  # Clean slate
    
    print("\n[1] Creating ResearchAgent and CodingAgent")
    print("-" * 70)
    
    # Create research agent
    research_config = AgentConfig(
        name="ResearchAgent",
        description="Specialized in research and analysis",
        capabilities=["research", "analysis", "planning"]
    )
    research_agent = ResearchAgent(research_config, llm_client=None)
    registry.register_agent("research_agent", research_agent)
    print(f"✓ ResearchAgent registered: {research_agent.name}")
    print(f"  - Capabilities: {research_agent.capabilities}")
    
    # Create coding agent
    coding_config = AgentConfig(
        name="CodingAgent",
        description="Specialized in software development",
        capabilities=["coding", "architecture", "implementation"]
    )
    coding_agent = CodingAgent(coding_config, llm_client=None)
    registry.register_agent("coding_agent", coding_agent)
    print(f"✓ CodingAgent registered: {coding_agent.name}")
    print(f"  - Capabilities: {coding_agent.capabilities}")
    
    print("\n[2] Creating workflow tasks")
    print("-" * 70)
    
    # Create research task
    async def research_handler(query: str) -> str:
        result = await research_agent.think(query)
        return f"Research plan: {result}"
    
    research_task = Task(
        id="task_research",
        name="Research Planning",
        description="Plan research approach",
        handler=research_handler,
        priority=TaskPriority.HIGH
    )
    research_agent.register_task(research_task)
    print(f"✓ Task registered: {research_task.name}")
    print(f"  - ID: {research_task.id}")
    print(f"  - Priority: {research_task.priority.name}")
    
    # Create coding task
    async def coding_handler(spec: str) -> str:
        result = await coding_agent.think(spec)
        return f"Implementation plan: {result}"
    
    coding_task = Task(
        id="task_coding",
        name="Implementation",
        description="Code implementation based on research",
        handler=coding_handler,
        priority=TaskPriority.HIGH,
        dependencies=["task_research"]
    )
    coding_agent.register_task(coding_task)
    print(f"✓ Task registered: {coding_task.name}")
    print(f"  - ID: {coding_task.id}")
    print(f"  - Dependencies: {coding_task.dependencies}")
    
    print("\n[3] Executing independent tasks")
    print("-" * 70)
    
    # Execute research task
    query = "What are best practices for Python async programming?"
    print(f"\nExecuting: {research_task.name}")
    print(f"Input: {query}")
    
    research_result = await research_agent.execute_task(
        "task_research",
        query=query
    )
    print(f"\n✓ Result status: {research_result.status.value}")
    print(f"  - Duration: {research_result.duration_seconds:.2f}s")
    if research_result.output:
        output_preview = research_result.output[:100] + "..." if len(research_result.output) > 100 else research_result.output
        print(f"  - Output: {output_preview}")
    
    print("\n[4] Agent statistics")
    print("-" * 70)
    
    stats = research_agent.get_stats()
    print(f"\nResearchAgent Stats:")
    for key, value in stats.items():
        if key != "capabilities":
            print(f"  - {key}: {value}")
    
    stats = coding_agent.get_stats()
    print(f"\nCodingAgent Stats:")
    for key, value in stats.items():
        if key != "capabilities":
            print(f"  - {key}: {value}")
    
    print("\n[5] Registry and Orchestrator status")
    print("-" * 70)
    
    registry_stats = registry.get_stats()
    print(f"\nRegistry Stats:")
    print(f"  - Registered agents: {registry_stats['registered_agents']}")
    print(f"  - Agent IDs: {registry_stats['agent_ids']}")
    
    orchestrator = Orchestrator()
    orch_stats = orchestrator.get_stats()
    print(f"\nOrchestrator Stats:")
    print(f"  - Registered workflows: {orch_stats['registered_workflows']}")
    print(f"  - Registered agents: {orch_stats['registered_agents']}")
    
    print("\n" + "=" * 70)
    print("✅ HERMES WORKFLOW DEMONSTRATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_hermes_workflow())
