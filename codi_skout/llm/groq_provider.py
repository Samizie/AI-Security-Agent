from typing import Dict, Any, List, Optional
import logging

from .base_provider import LLMProvider

class GroqProvider(LLMProvider):
    """Provider for Groq's API"""
    
    provider_name = "groq"
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.default_model = kwargs.get("default_model", "llama-3.1-8b-instant")
        self.default_temperature = kwargs.get("temperature", 0.1)
        
        # Import here to avoid dependency issues
        try:
            from langchain_groq import ChatGroq
            self.ChatGroq = ChatGroq
        except ImportError:
            self.logger.error("langchain_groq package not installed. Please install it with: pip install langchain_groq")
            raise
    
    def _get_llm(self, model=None, temperature=None):
        """Get a LangChain LLM instance"""
        return self.ChatGroq(
            model=model or self.default_model,
            temperature=temperature or self.default_temperature,
            api_key=self.api_key
        )
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt using Groq's API"""
        model = kwargs.get("model", self.default_model)
        temperature = kwargs.get("temperature", self.default_temperature)
        
        try:
            llm = self._get_llm(model, temperature)
            response = llm.invoke(prompt)
            
            return response.content
        except Exception as e:
            self.logger.error(f"Error generating text with Groq: {str(e)}")
            raise
    
    def generate_chat_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a response from a chat history using Groq's API"""
        model = kwargs.get("model", self.default_model)
        temperature = kwargs.get("temperature", self.default_temperature)
        
        try:
            # Convert messages to LangChain format
            langchain_messages = []
            for message in messages:
                role = message.get("role", "user")
                content = message.get("content", "")
                
                if role == "user":
                    from langchain_core.messages import HumanMessage
                    langchain_messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    from langchain_core.messages import AIMessage
                    langchain_messages.append(AIMessage(content=content))
                else:
                    from langchain_core.messages import SystemMessage
                    langchain_messages.append(SystemMessage(content=content))
            
            llm = self._get_llm(model, temperature)
            response = llm.invoke(langchain_messages)
            
            return response.content
        except Exception as e:
            self.logger.error(f"Error generating chat response with Groq: {str(e)}")
            raise
    
    @property
    def available_models(self) -> List[str]:
        """Get the list of available models"""
        return [
            "llama-3.1-8b-instant",
            "llama-3.1-70b-instant",
            "llama-3.1-405b-instant",
            "mixtral-8x7b-32768",
            "gemma-7b-it"
        ]