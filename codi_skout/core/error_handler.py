from typing import Dict, Any, List, Optional, Callable, Type
import logging
import traceback
import time
from functools import wraps

from .errors import (
    MCPError, ProviderError, ProviderRateLimitError, 
    ProviderTimeoutError, ProviderQuotaExceededError,
    AgentError, AgentTimeoutError, AgentExecutionError
)

class ErrorHandler:
    """Handler for MCP errors with retry and fallback logic"""
    
    def __init__(self):
        self.logger = logging.getLogger("mcp.error_handler")
        self.error_handlers: Dict[Type[Exception], List[Callable]] = {}
        self.register_default_handlers()
    
    def register_handler(self, error_type: Type[Exception], handler: Callable):
        """Register a handler for a specific error type"""
        if error_type not in self.error_handlers:
            self.error_handlers[error_type] = []
        
        self.error_handlers[error_type].append(handler)
        self.logger.debug(f"Registered handler for {error_type.__name__}")
    
    def register_default_handlers(self):
        """Register default handlers for common errors"""
        # Provider rate limit handler
        self.register_handler(
            ProviderRateLimitError,
            lambda error, context: {"action": "retry", "delay": 5}
        )
        
        # Provider timeout handler
        self.register_handler(
            ProviderTimeoutError,
            lambda error, context: {"action": "retry", "delay": 2}
        )
        
        # Provider quota exceeded handler
        self.register_handler(
            ProviderQuotaExceededError,
            lambda error, context: {"action": "fallback_provider"}
        )
        
        # Agent timeout handler
        self.register_handler(
            AgentTimeoutError,
            lambda error, context: {"action": "retry", "delay": 3}
        )
        
        # Agent execution error handler
        self.register_handler(
            AgentExecutionError,
            lambda error, context: {"action": "log_and_continue"}
        )
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle an error and determine the appropriate action"""
        context = context or {}
        self.logger.error(f"Handling error: {str(error)}")
        
        # Find the most specific handler
        handler_result = None
        for error_type, handlers in self.error_handlers.items():
            if isinstance(error, error_type):
                for handler in handlers:
                    try:
                        result = handler(error, context)
                        if result:
                            handler_result = result
                            break
                    except Exception as e:
                        self.logger.error(f"Error in error handler: {str(e)}")
                
                if handler_result:
                    break
        
        # Default action if no handler found
        if not handler_result:
            handler_result = {"action": "raise"}
        
        self.logger.info(f"Error handler result: {handler_result}")
        return handler_result
    
    def with_error_handling(self, max_retries: int = 3, retry_delay: float = 1.0):
        """Decorator for functions that need error handling"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                retries = 0
                last_error = None
                
                while retries <= max_retries:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_error = e
                        self.logger.error(f"Error in {func.__name__}: {str(e)}")
                        self.logger.debug(traceback.format_exc())
                        
                        # Get context for error handling
                        context = {
                            "function": func.__name__,
                            "args": args,
                            "kwargs": kwargs,
                            "retries": retries,
                            "max_retries": max_retries
                        }
                        
                        # Handle the error
                        result = self.handle_error(e, context)
                        action = result.get("action", "raise")
                        
                        if action == "retry" and retries < max_retries:
                            retries += 1
                            delay = result.get("delay", retry_delay)
                            self.logger.info(f"Retrying {func.__name__} in {delay} seconds (attempt {retries}/{max_retries})")
                            time.sleep(delay)
                        elif action == "fallback_provider" and "fallback_provider" in kwargs:
                            self.logger.info(f"Falling back to alternative provider")
                            kwargs["provider"] = kwargs["fallback_provider"]
                            retries += 1
                        elif action == "log_and_continue":
                            self.logger.warning(f"Continuing despite error: {str(e)}")
                            return None
                        else:
                            # Raise the error
                            raise
                
                # If we've exhausted retries, raise the last error
                raise last_error
            
            return wrapper
        
        return decorator