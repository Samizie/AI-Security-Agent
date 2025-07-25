import unittest
import logging
import os
import json
from typing import Dict, Any, Optional

from core.context_init import initialize_context_system
from core.llm_provider_registry import LLMProviderRegistry
from llm.provider_factory import LLMProviderFactory
from .config import get_test_config

class MCPTestCase(unittest.TestCase):
    """Base test case for MCP components"""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment"""
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Get test configuration
        cls.config = get_test_config()
        
        # Initialize context system
        cls.context_system = initialize_context_system()
        
        # Initialize LLM registry
        cls.llm_registry = LLMProviderRegistry()
        
        # Register providers if API keys are available
        cls._register_test_providers()
    
    @classmethod
    def _register_test_providers(cls):
        """Register test providers if API keys are available"""
        # Register OpenAI provider
        if cls.config["openai_api_key"]:
            try:
                provider = LLMProviderFactory.create_provider(
                    provider_name="openai",
                    api_key=cls.config["openai_api_key"]
                )
                cls.llm_registry.register_provider(provider.__class__)
                cls.llm_registry.create_provider_instance(
                    "openai",
                    api_key=cls.config["openai_api_key"]
                )
                logging.info("Registered OpenAI provider for testing")
            except Exception as e:
                logging.error(f"Failed to register OpenAI provider: {str(e)}")
        
        # Register Anthropic provider
        if cls.config["anthropic_api_key"]:
            try:
                provider = LLMProviderFactory.create_provider(
                    provider_name="anthropic",
                    api_key=cls.config["anthropic_api_key"]
                )
                cls.llm_registry.register_provider(provider.__class__)
                cls.llm_registry.create_provider_instance(
                    "anthropic",
                    api_key=cls.config["anthropic_api_key"]
                )
                logging.info("Registered Anthropic provider for testing")
            except Exception as e:
                logging.error(f"Failed to register Anthropic provider: {str(e)}")
        
        # Register Groq provider
        if cls.config["groq_api_key"]:
            try:
                provider = LLMProviderFactory.create_provider(
                    provider_name="groq",
                    api_key=cls.config["groq_api_key"]
                )
                cls.llm_registry.register_provider(provider.__class__)
                cls.llm_registry.create_provider_instance(
                    "groq",
                    api_key=cls.config["groq_api_key"]
                )
                cls.llm_registry.set_default_provider("groq")
                logging.info("Registered Groq provider for testing")
            except Exception as e:
                logging.error(f"Failed to register Groq provider: {str(e)}")
    
    def setUp(self):
        """Set up before each test"""
        # Clear shared context
        self.context_system["shared_context"].context = {}
    
    def tearDown(self):
        """Clean up after each test"""
        pass
    
    def load_mock_data(self, filename: str) -> Any:
        """Load mock data from a file"""
        file_path = os.path.join(self.config["mock_data_dir"], filename)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            if filename.endswith('.json'):
                return json.load(f)
            else:
                return f.read()
    
    def save_output(self, filename: str, data: Any) -> str:
        """Save output data to a file"""
        file_path = os.path.join(self.config["output_dir"], filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if isinstance(data, (dict, list)):
                json.dump(data, f, indent=2)
            else:
                f.write(str(data))
        
        return file_path