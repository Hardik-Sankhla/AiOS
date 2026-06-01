"""Agent registry for registration and discovery."""

from typing import Dict, List, Optional, Type
from .agent import Agent


class AgentRegistry:
    """Central registry for agent registration and discovery."""
    
    _instance: Optional['AgentRegistry'] = None
    _agents: Dict[str, Agent] = {}
    _agent_classes: Dict[str, Type[Agent]] = {}
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register_agent(self, agent_id: str, agent: Agent) -> None:
        """Register an agent instance."""
        if agent_id in self._agents:
            raise ValueError(f"Agent {agent_id} already registered")
        self._agents[agent_id] = agent
    
    def register_agent_class(self, agent_id: str, agent_class: Type[Agent]) -> None:
        """Register an agent class for factory creation."""
        if agent_id in self._agent_classes:
            raise ValueError(f"Agent class {agent_id} already registered")
        self._agent_classes[agent_id] = agent_class
    
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent instance."""
        if agent_id in self._agents:
            del self._agents[agent_id]
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get registered agent by ID."""
        return self._agents.get(agent_id)
    
    def get_agent_class(self, agent_id: str) -> Optional[Type[Agent]]:
        """Get registered agent class by ID."""
        return self._agent_classes.get(agent_id)
    
    def list_agents(self) -> List[str]:
        """List all registered agent IDs."""
        return list(self._agents.keys())
    
    def list_agent_classes(self) -> List[str]:
        """List all registered agent class IDs."""
        return list(self._agent_classes.keys())
    
    def create_agent(self, agent_class_id: str, agent_id: str, config) -> Agent:
        """Factory method to create and register an agent."""
        agent_class = self.get_agent_class(agent_class_id)
        if not agent_class:
            raise ValueError(f"Agent class {agent_class_id} not found")
        
        agent = agent_class(config)
        self.register_agent(agent_id, agent)
        return agent
    
    def get_agent_by_capability(self, capability: str) -> Optional[Agent]:
        """Find agent with specific capability."""
        for agent in self._agents.values():
            if capability in agent.capabilities:
                return agent
        return None
    
    def get_agents_by_capability(self, capability: str) -> List[Agent]:
        """Find all agents with specific capability."""
        return [
            agent for agent in self._agents.values()
            if capability in agent.capabilities
        ]
    
    def clear(self) -> None:
        """Clear all registered agents (for testing)."""
        self._agents.clear()
        self._agent_classes.clear()
    
    def get_stats(self) -> Dict:
        """Get registry statistics."""
        return {
            "registered_agents": len(self._agents),
            "registered_classes": len(self._agent_classes),
            "agent_ids": self.list_agents(),
            "class_ids": self.list_agent_classes()
        }


# Singleton instance
_registry = AgentRegistry()


def get_registry() -> AgentRegistry:
    """Get the global agent registry."""
    return _registry
