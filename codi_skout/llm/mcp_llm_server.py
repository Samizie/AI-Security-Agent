from typing import Dict, Any, List, Optional
import logging

from core.mcp_server import MCPServer, MCPTool, MCPResource
from .provider_factory import LLMProviderFactory
from .base_provider import LLMProvider

class MCPLLMServer(MCPServer):
    """MCP server for LLM providers"""
    
    def __init__(self):
        super().__init__("llm_server")
        self.providers: Dict[str, LLMProvider] = {}
        self.default_provider: Optional[str] = None
        
        # Register tools
        self._register_tools()
        
        # Register resources
        self._register_resources()
    
    def _register_tools(self):
        """Register LLM-related tools"""
        
        # Tool for text generation
        self.register_tool(
            name="generate_text",
            description="Generate text from a prompt using an LLM",
            input_schema={
                "prompt": {"type": "string", "description": "The prompt to generate text from"},
                "provider": {"type": "string", "description": "The provider to use", "optional": True},
                "model": {"type": "string", "description": "The model to use", "optional": True},
                "max_tokens": {"type": "integer", "description": "Maximum tokens to generate", "optional": True},
                "temperature": {"type": "number", "description": "Temperature for generation", "optional": True}
            },
            output_schema={
                "text": {"type": "string", "description": "The generated text"}
            },
            handler=self._handle_generate_text
        )
        
        # Tool for chat completion
        self.register_tool(
            name="generate_chat_response",
            description="Generate a response from a chat history",
            input_schema={
                "messages": {"type": "array", "description": "The chat history"},
                "provider": {"type": "string", "description": "The provider to use", "optional": True},
                "model": {"type": "string", "description": "The model to use", "optional": True},
                "max_tokens": {"type": "integer", "description": "Maximum tokens to generate", "optional": True},
                "temperature": {"type": "number", "description": "Temperature for generation", "optional": True}
            },
            output_schema={
                "response": {"type": "string", "description": "The generated response"}
            },
            handler=self._handle_generate_chat_response
        )
        
        # Tool for registering a provider
        self.register_tool(
            name="register_provider",
            description="Register a new LLM provider",
            input_schema={
                "provider_name": {"type": "string", "description": "The name of the provider"},
                "api_key": {"type": "string", "description": "The API key for the provider"},
                "default": {"type": "boolean", "description": "Whether to set as default", "optional": True},
                "config": {"type": "object", "description": "Additional configuration", "optional": True}
            },
            output_schema={
                "success": {"type": "boolean", "description": "Whether the registration was successful"},
                "provider_id": {"type": "string", "description": "The ID of the registered provider"}
            },
            handler=self._handle_register_provider
        )
        
        # Tool for listing providers
        self.register_tool(
            name="list_providers",
            description="List all registered providers",
            input_schema={},
            output_schema={
                "providers": {"type": "object", "description": "The registered providers"}
            },
            handler=self._handle_list_providers
        )
    
    def _register_resources(self):
        """Register LLM-related resources"""
        
        # Resource for available providers
        self.register_resource(
            uri="llm://providers/available",
            data=LLMProviderFactory.get_available_providers(),
            metadata={"description": "Information about available LLM providers"}
        )
    
    def _handle_generate_text(self, prompt: str, provider: Optional[str] = None, 
                             model: Optional[str] = None, max_tokens: Optional[int] = None,
                             temperature: Optional[float] = None) -> Dict[str, str]:
        """Handle the generate_text tool"""
        provider_instance = self._get_provider(provider)
        
        kwargs = {}
        if model:
            kwargs["model"] = model
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        if temperature is not None:
            kwargs["temperature"] = temperature
        
        text = provider_instance.generate_text(prompt, **kwargs)
        return {"text": text}
    
    def _handle_generate_chat_response(self, messages: List[Dict[str, str]], 
                                     provider: Optional[str] = None,
                                     model: Optional[str] = None, 
                                     max_tokens: Optional[int] = None,
                                     temperature: Optional[float] = None) -> Dict[str, str]:
        """Handle the generate_chat_response tool"""
        provider_instance = self._get_provider(provider)
        
        kwargs = {}
        if model:
            kwargs["model"] = model
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        if temperature is not None:
            kwargs["temperature"] = temperature
        
        response = provider_instance.generate_chat_response(messages, **kwargs)
        return {"response": response}
    
    def _handle_register_provider(self, provider_name: str, api_key: str,
                                default: bool = False, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle the register_provider tool"""
        try:
            provider = LLMProviderFactory.create_provider(
                provider_name=provider_name,
                api_key=api_key,
                **(config or {})
            )
            
            provider_id = f"{provider_name}_{len([p for p in self.providers if p.startswith(provider_name)])}"
            self.providers[provider_id] = provider
            
            if default or not self.default_provider:
                self.default_provider = provider_id
            
            return {
                "success": True,
                "provider_id": provider_id
            }
        except Exception as e:
            self.logger.error(f"Failed to register provider: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _handle_list_providers(self) -> Dict[str, Dict[str, Any]]:
        """Handle the list_providers tool"""
        result = {}
        for provider_id, provider in self.providers.items():
            result[provider_id] = {
                "name": provider.provider_name,
                "default": provider_id == self.default_provider,
                "models": provider.available_models
            }
        return {"providers": result}
    
    def _get_provider(self, provider_id: Optional[str] = None) -> LLMProvider:
        """Get a provider instance by ID or the default"""
        if not provider_id:
            if not self.default_provider:
                raise ValueError("No default provider set")
            return self.providers[self.default_provider]
        
        if provider_id not in self.providers:
            raise ValueError(f"Provider not found: {provider_id}")
        
        return self.providers[provider_id]