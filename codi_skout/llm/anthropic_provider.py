from typing import Dict, Any, List, Optional
import logging

from .base_provider import LLMProvider

class AnthropicProvider(LLMProvider):
    """Provider for Anthropic's Claude API"""
    
    provider_name = "anthropic"
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.default_model = kwargs.get("default_model", "claude-3-opus-20240229")
        
        # Import here to avoid dependency issues
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            self.logger.error("Anthropic package not installed. Please install it with: pip install anthropic")
            raise
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt using Anthropic's API"""
        model = kwargs.get("model", self.default_model)
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        
        try:
            response = self.client.completions.create(
                model=model,
                prompt=f"\n\nHuman: {prompt}\n\nAssistant:",
                max_tokens_to_sample=max_tokens,
                temperature=temperature
            )
            
            return response.completion.strip()
        except Exception as e:
            self.logger.error(f"Error generating text with Anthropic: {str(e)}")
            raise
    
    def generate_chat_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a response from a chat history using Anthropic's API"""
        model = kwargs.get("model", self.default_model)
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        
        # Convert messages to Anthropic format
        anthropic_messages = []
        for message in messages:
            role = message.get("role", "user")
            if role == "user":
                anthropic_role = "human"
            elif role == "assistant":
                anthropic_role = "assistant"
            else:
                anthropic_role = "human"
            
            anthropic_messages.append({
                "role": anthropic_role,
                "content": message.get("content", "")
            })
        
        try:
            response = self.client.messages.create(
                model=model,
                messages=anthropic_messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.content[0].text
        except Exception as e:
            self.logger.error(f"Error generating chat response with Anthropic: {str(e)}")
            raise
    
    @property
    def available_models(self) -> List[str]:
        """Get the list of available models"""
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]