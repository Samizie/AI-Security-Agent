from typing import Dict, Any, Optional

class MCPError(Exception):
    """Base class for all MCP errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)

class ProviderError(MCPError):
    """Error related to LLM providers"""
    pass

class ProviderNotFoundError(ProviderError):
    """Error when a provider is not found"""
    pass

class ProviderAuthenticationError(ProviderError):
    """Error when authentication with a provider fails"""
    pass

class ProviderQuotaExceededError(ProviderError):
    """Error when a provider's quota is exceeded"""
    pass

class ProviderRateLimitError(ProviderError):
    """Error when a provider's rate limit is exceeded"""
    pass

class ProviderTimeoutError(ProviderError):
    """Error when a provider times out"""
    pass

class AgentError(MCPError):
    """Error related to agents"""
    pass

class AgentNotFoundError(AgentError):
    """Error when an agent is not found"""
    pass

class AgentTimeoutError(AgentError):
    """Error when an agent times out"""
    pass

class AgentExecutionError(AgentError):
    """Error when an agent fails to execute a task"""
    pass

class ContextError(MCPError):
    """Error related to the shared context"""
    pass

class ContextPathNotFoundError(ContextError):
    """Error when a context path is not found"""
    pass

class ContextAccessDeniedError(ContextError):
    """Error when access to a context path is denied"""
    pass

class MessageError(MCPError):
    """Error related to message passing"""
    pass

class MessageDeliveryError(MessageError):
    """Error when a message cannot be delivered"""
    pass

class MessageTimeoutError(MessageError):
    """Error when a message times out"""
    pass

class ToolError(MCPError):
    """Error related to MCP tools"""
    pass

class ToolNotFoundError(ToolError):
    """Error when a tool is not found"""
    pass

class ToolExecutionError(ToolError):
    """Error when a tool fails to execute"""
    pass

class ResourceError(MCPError):
    """Error related to MCP resources"""
    pass

class ResourceNotFoundError(ResourceError):
    """Error when a resource is not found"""
    pass

class ResourceAccessDeniedError(ResourceError):
    """Error when access to a resource is denied"""
    pass