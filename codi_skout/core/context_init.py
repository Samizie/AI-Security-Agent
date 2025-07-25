from typing import Dict, Any
import logging

from .shared_context import SharedContext
from .message_broker import MessageBroker
from .llm_provider_registry import LLMProviderRegistry

def initialize_context_system() -> Dict[str, Any]:
    """Initialize the context system"""
    logger = logging.getLogger("mcp.context_init")
    
    # Create the shared context
    shared_context = SharedContext()
    logger.info("Created shared context")
    
    # Create the message broker
    message_broker = MessageBroker()
    logger.info("Created message broker")
    
    # Create the LLM provider registry
    llm_registry = LLMProviderRegistry()
    logger.info("Created LLM provider registry")
    
    return {
        "shared_context": shared_context,
        "message_broker": message_broker,
        "llm_registry": llm_registry
    }