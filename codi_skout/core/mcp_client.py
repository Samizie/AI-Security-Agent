from typing import Dict, Any, List, Optional, Callable
import logging

from .message_broker import MessageBroker, MCPMessage
from .shared_context import SharedContext
from .llm_provider_registry import LLMProviderRegistry

class MCPClient:
    """Client for agents to interact with the MCP system"""
    
    def __init__(self, agent_name: str, message_broker: MessageBroker, 
                shared_context: SharedContext, llm_registry: LLMProviderRegistry):
        self.agent_name = agent_name
        self.message_broker = message_broker
        self.shared_context = shared_context
        self.llm_registry = llm_registry
        self.logger = logging.getLogger(f"mcp.client.{agent_name}")
        
        # Subscribe to messages for this agent
        self.message_broker.subscribe(agent_name, self._handle_message)
        self.message_handlers: Dict[str, Callable[[MCPMessage], None]] = {}
    
    def send_message(self, recipient: str, message_type: str, 
                    content: Dict[str, Any], reply_to: Optional[str] = None) -> MCPMessage:
        """Send a message to another agent"""
        return self.message_broker.publish(
            sender=self.agent_name,
            recipient=recipient,
            message_type=message_type,
            content=content,
            reply_to=reply_to
        )
    
    def broadcast_message(self, message_type: str, content: Dict[str, Any]) -> MCPMessage:
        """Broadcast a message to all agents"""
        return self.message_broker.publish(
            sender=self.agent_name,
            recipient="*",
            message_type=message_type,
            content=content
        )
    
    def register_message_handler(self, message_type: str, 
                               handler: Callable[[MCPMessage], None]) -> None:
        """Register a handler for a specific message type"""
        self.message_handlers[message_type] = handler
        self.logger.debug(f"Registered handler for message type: {message_type}")
    
    def _handle_message(self, message: MCPMessage) -> None:
        """Handle an incoming message"""
        self.logger.debug(f"Received message: {message.id} from {message.sender}")
        
        if message.message_type in self.message_handlers:
            try:
                self.message_handlers[message.message_type](message)
            except Exception as e:
                self.logger.error(f"Error in message handler: {str(e)}")
    
    def set_context(self, path: str, value: Any) -> None:
        """Set a value in the shared context"""
        self.shared_context.set(path, value, self.agent_name)
    
    def get_context(self, path: str, default: Any = None) -> Any:
        """Get a value from the shared context"""
        return self.shared_context.get(path, default)
    
    def watch_context(self, path: str) -> None:
        """Watch a path in the shared context for changes"""
        self.shared_context.watch(path, self.agent_name)
    
    def get_llm(self, provider_name: Optional[str] = None) -> Any:
        """Get an LLM provider instance"""
        return self.llm_registry.get_provider(provider_name)
    
    def cleanup(self) -> None:
        """Clean up resources used by this client"""
        # Unsubscribe from messages
        self.message_broker.unsubscribe(self.agent_name, self._handle_message)
        self.logger.info(f"Cleaned up MCP client for agent: {self.agent_name}")