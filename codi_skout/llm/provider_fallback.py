from typing import Dict, Any, List, Optional, Tuple
import logging
import time

from core.llm_provider_registry import LLMProviderRegistry
from core.errors import (
    ProviderError, ProviderNotFoundError, ProviderAuthenticationError,
    ProviderQuotaExceededError, ProviderRateLimitError, ProviderTimeoutError
)

class ProviderFallbackManager:
    """Manager for LLM provider fallback strategies"""
    
    def __init__(self, llm_registry: LLMProviderRegistry):
        self.llm_registry = llm_registry
        self.logger = logging.getLogger("llm.fallback")
        self.provider_status: Dict[str, Dict[str, Any]] = {}
        self.fallback_chains: Dict[str, List[str]] = {}
    
    def register_fallback_chain(self, primary_provider: str, fallbacks: List[str]):
        """Register a fallback chain for a provider"""
        self.fallback_chains[primary_provider] = fallbacks
        self.logger.info(f"Registered fallback chain for {primary_provider}: {fallbacks}")
    
    def update_provider_status(self, provider_id: str, status: str, error: Optional[Exception] = None):
        """Update the status of a provider"""
        if provider_id not in self.provider_status:
            self.provider_status[provider_id] = {
                "status": "unknown",
                "last_error": None,
                "error_count": 0,
                "last_success": None,
                "last_failure": None
            }
        
        self.provider_status[provider_id]["status"] = status
        
        if status == "error" and error:
            self.provider_status[provider_id]["last_error"] = str(error)
            self.provider_status[provider_id]["error_count"] += 1
            self.provider_status[provider_id]["last_failure"] = time.time()
        elif status == "success":
            self.provider_status[provider_id]["last_success"] = time.time()
        
        self.logger.debug(f"Updated provider status: {provider_id} -> {status}")
    
    def get_provider_with_fallback(self, provider_id: Optional[str] = None) -> Tuple[Any, str]:
        """Get a provider instance with fallback if needed"""
        # If no provider specified, use the default
        if not provider_id:
            provider_id = self.llm_registry.default_provider
        
        # Check if the provider exists
        if provider_id not in self.llm_registry.instances:
            # Try to find a fallback
            fallbacks = self.fallback_chains.get(provider_id, [])
            
            for fallback in fallbacks:
                if fallback in self.llm_registry.instances:
                    self.logger.warning(f"Provider {provider_id} not found, falling back to {fallback}")
                    return self.llm_registry.get_provider(fallback), fallback
            
            # No fallbacks available
            raise ProviderNotFoundError(f"Provider not found: {provider_id}")
        
        # Check if the provider is in error state
        if provider_id in self.provider_status and self.provider_status[provider_id]["status"] == "error":
            # Check if we should retry the provider
            last_failure = self.provider_status[provider_id].get("last_failure", 0)
            error_count = self.provider_status[provider_id].get("error_count", 0)
            
            # Exponential backoff for retries
            retry_delay = min(60, 2 ** error_count)
            
            if time.time() - last_failure < retry_delay:
                # Try to find a fallback
                fallbacks = self.fallback_chains.get(provider_id, [])
                
                for fallback in fallbacks:
                    if fallback in self.llm_registry.instances:
                        fallback_status = self.provider_status.get(fallback, {}).get("status")
                        if fallback_status != "error":
                            self.logger.warning(f"Provider {provider_id} in error state, falling back to {fallback}")
                            return self.llm_registry.get_provider(fallback), fallback
                
                # No fallbacks available, retry the original provider
                self.logger.warning(f"Provider {provider_id} in error state, but no fallbacks available. Retrying.")
        
        # Get the provider
        return self.llm_registry.get_provider(provider_id), provider_id
    
    def with_fallback(self, func):
        """Decorator for functions that need provider fallback"""
        def wrapper(*args, **kwargs):
            provider_id = kwargs.get("provider")
            
            try:
                # Get the provider with fallback
                provider, actual_provider_id = self.get_provider_with_fallback(provider_id)
                
                # Update the provider in kwargs
                kwargs["provider"] = actual_provider_id
                
                # Call the function
                result = func(*args, **kwargs)
                
                # Update provider status
                self.update_provider_status(actual_provider_id, "success")
                
                return result
                
            except ProviderError as e:
                # Update provider status
                if provider_id:
                    self.update_provider_status(provider_id, "error", e)
                
                # Handle specific provider errors
                if isinstance(e, ProviderQuotaExceededError):
                    # Try to find a fallback
                    fallbacks = self.fallback_chains.get(provider_id, [])
                    
                    for fallback in fallbacks:
                        try:
                            # Update the provider in kwargs
                            kwargs["provider"] = fallback
                            
                            # Call the function
                            result = func(*args, **kwargs)
                            
                            # Update provider status
                            self.update_provider_status(fallback, "success")
                            
                            return result
                        except Exception as fallback_error:
                            self.update_provider_status(fallback, "error", fallback_error)
                
                # No fallbacks worked, re-raise the error
                raise
        
        return wrapper