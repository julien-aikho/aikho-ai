"""Registry for chat agents."""

import yaml
import importlib
import logfire
from pathlib import Path
from typing import Dict, Type
from .chat import ChatAgent

class AgentRegistry:
    """Registry for chat agents."""
    
    _agents: Dict[str, ChatAgent] = {}
    _metadata: Dict[str, dict] = {}
    
    @classmethod
    def register(cls, agent_id: str, agent: ChatAgent) -> None:
        """Register a new agent instance."""
        cls._agents[agent_id] = agent
    
    @classmethod
    def get(cls, agent_id: str) -> ChatAgent:
        """Get an agent by ID."""
        if agent_id not in cls._agents:
            raise ValueError(f"Unknown agent: {agent_id}")
        return cls._agents[agent_id]
    
    @classmethod
    def list(cls) -> list[dict]:
        """List all registered agents."""
        return [
            {
                "id": agent_id,
                "name": agent_id.title(),  # Simple name from ID for now
                "description": "A chat agent"  # Simple description for now
            }
            for agent_id in cls._agents
        ]
    
    @classmethod
    def load_from_config(cls) -> None:
        """Load agents from config file."""
        config_path = Path("config/agents.yaml")
        try:
            with config_path.open() as f:
                config = yaml.safe_load(f)
            
            for entry in config["agents"]:
                try:
                    module_path, class_name = entry["package"].rsplit(".", 1)
                    logfire.info(f"Loading module {module_path}")
                    module = importlib.import_module(module_path)
                    logfire.info(f"Getting class {class_name} from module")
                    agent_class = getattr(module, class_name)
                    logfire.info(f"Got agent_class: {agent_class} of type {type(agent_class)}")
                    logfire.info(f"Module dict: {module.__dict__.keys()}")
                    
                    # Make sure we got a class and it's a ChatAgent
                    if not isinstance(agent_class, type):
                        raise TypeError(f"Expected a class, got {type(agent_class)}")
                    if not issubclass(agent_class, ChatAgent):
                        raise TypeError(f"Expected a ChatAgent subclass, got {agent_class}")
                        
                    agent = agent_class()
                    cls.register(entry["id"], agent)
                except Exception as e:
                    logfire.error(f"Failed to load agent {entry['id']}: {e}")
        except Exception as e:
            logfire.error(f"Failed to load config {config_path}: {e}") 