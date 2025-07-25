from typing import Dict, Any, List
import logging

from core.mcp_client import MCPClient
from core.message_broker import MessageBroker
from core.shared_context import SharedContext
from core.llm_provider_registry import LLMProviderRegistry

from .base_agent import BaseAgent
from .github_cloner import GitHubClonerAgent
from .security_analyst import CodeSecurityAnalystAgent
from .code_reviewer import CodeReviewerAgent
from .reporter import ReporterAgent

class AgentFactory:
    """Factory for creating agent instances"""
    
    def __init__(self, message_broker: MessageBroker, shared_context: SharedContext, 
                llm_registry: LLMProviderRegistry):
        self.message_broker = message_broker
        self.shared_context = shared_context
        self.llm_registry = llm_registry
        self.logger = logging.getLogger("agent.factory")
        self.agents: Dict[str, BaseAgent] = {}
    
    def create_agent(self, agent_type: str) -> BaseAgent:
        """Create an agent instance by type"""
        # Create MCP client for the agent
        agent_name = f"{agent_type}_{len([a for a in self.agents if a.startswith(agent_type)])}"
        mcp_client = MCPClient(
            agent_name=agent_name,
            message_broker=self.message_broker,
            shared_context=self.shared_context,
            llm_registry=self.llm_registry
        )
        
        # Create the agent
        if agent_type.lower() == "github_cloner":
            self.logger.info(f"Creating GitHub Cloner agent: {agent_name}")
            agent = GitHubClonerAgent(mcp_client)
        elif agent_type.lower() == "security_analyst":
            self.logger.info(f"Creating Security Analyst agent: {agent_name}")
            agent = CodeSecurityAnalystAgent(mcp_client)
        elif agent_type.lower() == "code_reviewer":
            self.logger.info(f"Creating Code Reviewer agent: {agent_name}")
            agent = CodeReviewerAgent(mcp_client)
        elif agent_type.lower() == "reporter":
            self.logger.info(f"Creating Reporter agent: {agent_name}")
            agent = ReporterAgent(mcp_client)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        # Store the agent
        self.agents[agent_name] = agent
        
        return agent
    
    def get_agent(self, agent_name: str) -> BaseAgent:
        """Get an agent by name"""
        if agent_name not in self.agents:
            raise ValueError(f"Agent not found: {agent_name}")
        
        return self.agents[agent_name]
    
    def get_agents_by_type(self, agent_type: str) -> List[BaseAgent]:
        """Get all agents of a specific type"""
        return [agent for name, agent in self.agents.items() if name.startswith(agent_type)]
    
    def cleanup(self):
        """Clean up all agents"""
        for agent in self.agents.values():
            agent.cleanup()
        
        self.agents.clear()