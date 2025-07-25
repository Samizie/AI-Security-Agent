from typing import Dict, Any, List, Optional
import logging

from .base_provider import LLMProvider

class OpenAIProvider(LLMProvider):
    """Provider for OpenAI's API"""
    
    provider_name = "openai"
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.default_model = kwargs.get("default_model", "gpt-4o")
        
        # Import here to avoid dependency issues
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            self.logger.error("OpenAI package not installed. Please install it with: pip install openai")
            raise
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt using OpenAI's API"""
        model = kwargs.get("model", self.default_model)
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        
        try:
            response = self.client.completions.create(
                model=model,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].text.strip()
        except Exception as e:
            self.logger.error(f"Error generating text with OpenAI: {str(e)}")
            raise
    
    def generate_chat_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a response from a chat history using OpenAI's API"""
        model = kwargs.get("model", self.default_model)
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        
        # Convert messages to OpenAI format
        openai_messages = []
        for message in messages:
            openai_messages.append({
                "role": message.get("role", "user"),
                "content": message.get("content", "")
            })
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=openai_messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"Error generating chat response with OpenAI: {str(e)}")
            raise
    
    @property
    def available_models(self) -> List[str]:
        """Get the list of available models"""
        return [
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo"
        ]