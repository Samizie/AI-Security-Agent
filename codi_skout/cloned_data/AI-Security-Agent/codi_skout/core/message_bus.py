from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime

@dataclass
class AgentMessage:
    """Standard message format for agent communication"""
    sender: str
    recipient: str
    message_type: str
    content: Dict[str, Any]
    timestamp: str