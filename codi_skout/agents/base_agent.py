from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

from core.mcp_client import MCPClient
from core.message_broker import MessageBroker
from core.shared_context import SharedContext
from core.llm_provider_registry import LLMProviderRegistry

class BaseAgent(ABC):
    """Abstract base class for all agents using MCP architecture"""
    
    def __init__(self, name: str, mcp_client: MCPClient):
        self.name = name
        self.mcp_client = mcp_client
        self.logger = logging.getLogger(f"agent.{name}")
        
        # Register message handlers
        self._register_message_handlers()
    
    def _register_message_handlers(self):
        """Register handlers for different message types"""
        self.mcp_client.register_message_handler("task_request", self._handle_task_request)
        self.mcp_client.register_message_handler("context_change", self._handle_context_change)
        self.mcp_client.register_message_handler("ping", self._handle_ping)
    
    def _handle_task_request(self, message):
        """Handle a task request message"""
        self.logger.info(f"Received task request from {message.sender}")
        
        try:
            # Process the task
            result = self.process_task(message.content)
            
            # Send the result back
            self.mcp_client.send_message(
                recipient=message.sender,
                message_type="task_result",
                content=result,
                reply_to=message.id
            )
            
        except Exception as e:
            self.logger.error(f"Error processing task: {str(e)}")
            
            # Send error message back
            self.mcp_client.send_message(
                recipient=message.sender,
                message_type="task_error",
                content={
                    "error": str(e),
                    "task_data": message.content
                },
                reply_to=message.id
            )
    
    def _handle_context_change(self, message):
        """Handle a context change notification"""
        self.logger.debug(f"Received context change notification for {message.content.get('path')}")
        
        # Call the on_context_change method if implemented
        if hasattr(self, 'on_context_change') and callable(getattr(self, 'on_context_change')):
            self.on_context_change(
                message.content.get('path'),
                message.content.get('changed_by'),
                message.content.get('value')
            )
    
    def _handle_ping(self, message):
        """Handle a ping message from the monitor"""
        self.logger.debug(f"Received ping from {message.sender}")
        
        # Send a heartbeat back
        self.mcp_client.send_message(
            recipient=f"monitor.heartbeat.{self.name}",
            message_type="heartbeat",
            content={
                "timestamp": message.content.get("timestamp"),
                "status": "active"
            }
        )
    
    def send_message(self, recipient: str, message_type: str, content: Dict[str, Any]) -> None:
        """Send a message to another agent"""
        self.mcp_client.send_message(recipient, message_type, content)
    
    def broadcast_message(self, message_type: str, content: Dict[str, Any]) -> None:
        """Broadcast a message to all agents"""
        self.mcp_client.broadcast_message(message_type, content)
    
    def set_context(self, path: str, value: Any) -> None:
        """Set a value in the shared context"""
        self.mcp_client.set_context(path, value)
    
    def get_context(self, path: str, default: Any = None) -> Any:
        """Get a value from the shared context"""
        return self.mcp_client.get_context(path, default)
    
    def watch_context(self, path: str) -> None:
        """Watch a path in the shared context for changes"""
        self.mcp_client.watch_context(path)
    
    def get_llm(self, provider_name: Optional[str] = None) -> Any:
        """Get an LLM provider instance"""
        return self.mcp_client.get_llm(provider_name)
    
    @abstractmethod
    def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the main task for this agent"""
        pass
    
    def cleanup(self):
        """Clean up resources used by this agent"""
        self.mcp_client.cleanup()