from typing import Dict, Any, Optional
import logging

from .base_provider import LLMProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .groq_provider import GroqProvider

class LLMProviderFactory:
    """Factory for creating LLM provider instances"""
    
    @staticmethod
    def create_provider(provider_name: str, api_key: str, **kwargs) -> LLMProvider:
        """Create a provider instance by name"""
        logger = logging.getLogger("llm.factory")
        
        if provider_name.lower() == "openai":
            logger.info("Creating OpenAI provider")
            return OpenAIProvider(api_key=api_key, **kwargs)
        elif provider_name.lower() == "anthropic":
            logger.info("Creating Anthropic provider")
            return AnthropicProvider(api_key=api_key, **kwargs)
        elif provider_name.lower() == "groq":
            logger.info("Creating Groq provider")
            return GroqProvider(api_key=api_key, **kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
    
    @staticmethod
    def get_available_providers() -> Dict[str, Dict[str, Any]]:
        """Get information about all available providers"""
        return {
            "openai": {
                "name": "OpenAI",
                "models": OpenAIProvider.available_models,
                "description": "OpenAI's GPT models"
            },
            "anthropic": {
                "name": "Anthropic",
                "models": AnthropicProvider.available_models,
                "description": "Anthropic's Claude models"
            },
            "groq": {
                "name": "Groq",
                "models": GroqProvider.available_models,
                "description": "Groq's high-performance inference API"
            }
        }