from typing import Dict, Any, List, Type, Optional
from abc import ABC, abstractmethod
import logging

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
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

class LLMProviderRegistry:
    """Registry for LLM providers"""
    
    def __init__(self):
        self.providers: Dict[str, Type[LLMProvider]] = {}
        self.instances: Dict[str, LLMProvider] = {}
        self.default_provider: Optional[str] = None
        self.logger = logging.getLogger("mcp.llm_registry")
    
    def register_provider(self, provider_class: Type[LLMProvider]) -> None:
        """Register a new provider class"""
        provider_name = provider_class.provider_name
        self.providers[provider_name] = provider_class
        self.logger.info(f"Registered LLM provider: {provider_name}")
        
        # Set as default if it's the first one
        if not self.default_provider:
            self.default_provider = provider_name
    
    def create_provider_instance(self, provider_name: str, **kwargs) -> LLMProvider:
        """Create an instance of a provider"""
        if provider_name not in self.providers:
            raise ValueError(f"Provider not registered: {provider_name}")
        
        provider_class = self.providers[provider_name]
        instance = provider_class(**kwargs)
        instance_name = f"{provider_name}_{len([k for k in self.instances if k.startswith(provider_name)])}"
        self.instances[instance_name] = instance
        self.logger.info(f"Created provider instance: {instance_name}")
        return instance
    
    def get_provider(self, instance_name: Optional[str] = None) -> LLMProvider:
        """Get a provider instance by name, or the default if none specified"""
        if not instance_name:
            if not self.default_provider or not self.instances:
                raise ValueError("No default provider available")
            # Get the first instance of the default provider
            for name, instance in self.instances.items():
                if name.startswith(self.default_provider):
                    return instance
            # If no instances of default provider, create one
            return self.create_provider_instance(self.default_provider)
        
        if instance_name not in self.instances:
            raise ValueError(f"Provider instance not found: {instance_name}")
        
        return self.instances[instance_name]
    
    def set_default_provider(self, provider_name: str) -> None:
        """Set the default provider"""
        if provider_name not in self.providers:
            raise ValueError(f"Provider not registered: {provider_name}")
        
        self.default_provider = provider_name
        self.logger.info(f"Set default provider to: {provider_name}")