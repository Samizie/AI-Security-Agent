from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import logging

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, **kwargs):
        self.config = kwargs
        self.logger = logging.getLogger(f"llm.{self.provider_name}")
    
    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt"""
        pass
    
    @abstractmethod
    def generate_chat_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a response from a chat history"""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the name of the provider"""
        pass
    
    @property
    @abstractmethod
    def available_models(self) -> List[str]:
        """Get the list of available models"""
        pass
    
    def validate_api_key(self) -> bool:
        """Validate that the API key is valid"""
        try:
            # Make a minimal API call to check if the key works
            self.generate_text("test", max_tokens=1)
            return True
        except Exception as e:
            self.logger.error(f"API key validation failed: {str(e)}")
            return False