from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
import uuid
import time
import logging

@dataclass
class MCPMessage:
    """Message format for MCP communication"""
    id: str
    sender: str
    recipient: str
    message_type: str
    content: Dict[str, Any]
    timestamp: float
    reply_to: Optional[str] = None

class MessageBroker:
    """Broker for handling message passing between agents"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_history: List[MCPMessage] = []
        self.logger = logging.getLogger("mcp.message_broker")
    
    def publish(self, sender: str, recipient: str, message_type: str, 
               content: Dict[str, Any], reply_to: Optional[str] = None) -> MCPMessage:
        """Publish a message to the broker"""
        message = MCPMessage(
            id=str(uuid.uuid4()),
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            content=content,
            timestamp=time.time(),
            reply_to=reply_to
        )
        
        self.message_history.append(message)
        self.logger.debug(f"Published message: {message.id} from {sender} to {recipient}")
        
        # Notify subscribers
        if recipient in self.subscribers:
            for callback in self.subscribers[recipient]:
                try:
                    callback(message)
                except Exception as e:
                    self.logger.error(f"Error in subscriber callback: {str(e)}")
        
        # Broadcast messages
        if recipient == "*" and "*" in self.subscribers:
            for callback in self.subscribers["*"]:
                try:
                    callback(message)
                except Exception as e:
                    self.logger.error(f"Error in broadcast subscriber callback: {str(e)}")
        
        return message
    
    def subscribe(self, recipient: str, callback: Callable[[MCPMessage], None]) -> None:
        """Subscribe to messages for a specific recipient"""
        if recipient not in self.subscribers:
            self.subscribers[recipient] = []
        
        self.subscribers[recipient].append(callback)
        self.logger.debug(f"Added subscriber for recipient: {recipient}")
    
    def unsubscribe(self, recipient: str, callback: Callable[[MCPMessage], None]) -> None:
        """Unsubscribe from messages for a specific recipient"""
        if recipient in self.subscribers and callback in self.subscribers[recipient]:
            self.subscribers[recipient].remove(callback)
            self.logger.debug(f"Removed subscriber for recipient: {recipient}")
    
    def get_messages(self, recipient: Optional[str] = None, 
                    sender: Optional[str] = None,
                    message_type: Optional[str] = None,
                    start_time: Optional[float] = None,
                    end_time: Optional[float] = None) -> List[MCPMessage]:
        """Get messages matching the specified filters"""
        filtered_messages = self.message_history
        
        if recipient:
            filtered_messages = [m for m in filtered_messages if m.recipient == recipient]
        
        if sender:
            filtered_messages = [m for m in filtered_messages if m.sender == sender]
        
        if message_type:
            filtered_messages = [m for m in filtered_messages if m.message_type == message_type]
        
        if start_time:
            filtered_messages = [m for m in filtered_messages if m.timestamp >= start_time]
        
        if end_time:
            filtered_messages = [m for m in filtered_messages if m.timestamp <= end_time]
        
        return filtered_messages