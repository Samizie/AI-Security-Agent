from abc import ABC, abstractmethod
from typing import List, Dict, Any
from langchain_groq import ChatGroq
from datetime import datetime

from core.message_bus import AgentMessage
from core.data_structures import SecurityAnalysisResult, CodeReviewResult, RepoAnalysisData




# Base Agent Class
class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, name: str, api_key: str):
        self.name = name
        self.api_key = api_key
        self.llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1, api_key=api_key)
        self.message_history: List[AgentMessage] = []
    
    def send_message(self, recipient: str, message_type: str, content: Dict[str, Any]) -> AgentMessage:
        """Send a message to another agent"""
        message = AgentMessage(
            sender=self.name,
            recipient=recipient,
            message_type=message_type,
            content=content,
            timestamp=datetime.now().isoformat()
        )
        self.message_history.append(message)
        return message
    
    def receive_message(self, message: AgentMessage):
        """Receive a message from another agent"""
        self.message_history.append(message)
    
    @abstractmethod
    def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the main task for this agent"""
        pass