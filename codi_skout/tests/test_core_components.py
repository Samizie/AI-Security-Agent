import unittest
import time
from typing import Dict, Any

from core.shared_context import SharedContext
from core.message_broker import MessageBroker, MCPMessage
from core.llm_provider_registry import LLMProviderRegistry
from llm.provider_factory import LLMProviderFactory
from tests.base_test import MCPTestCase
from tests.mock_provider import MockLLMProvider

class TestSharedContext(MCPTestCase):
    """Tests for the SharedContext component"""
    
    def test_set_get_context(self):
        """Test setting and getting context values"""
        context = SharedContext()
        
        # Set a value
        context.set("test/path", "test_value")
        
        # Get the value
        value = context.get("test/path")
        
        self.assertEqual(value, "test_value")
    
    def test_nested_context(self):
        """Test nested context paths"""
        context = SharedContext()
        
        # Set nested values
        context.set("user/profile/name", "John Doe")
        context.set("user/profile/email", "john@example.com")
        context.set("user/settings/theme", "dark")
        
        # Get nested values
        name = context.get("user/profile/name")
        email = context.get("user/profile/email")
        theme = context.get("user/settings/theme")
        
        self.assertEqual(name, "John Doe")
        self.assertEqual(email, "john@example.com")
        self.assertEqual(theme, "dark")
        
        # Get parent path
        profile = context.get("user/profile")
        self.assertEqual(profile, {"name": "John Doe", "email": "john@example.com"})
    
    def test_default_value(self):
        """Test getting a value with a default"""
        context = SharedContext()
        
        # Get a non-existent value with a default
        value = context.get("non_existent_path", "default_value")
        
        self.assertEqual(value, "default_value")
    
    def test_watch_unwatch(self):
        """Test watching and unwatching paths"""
        context = SharedContext()
        
        # Watch a path
        context.watch("test/path", "test_agent")
        
        # Check if the agent is watching
        self.assertIn("test_agent", context.watchers.get("test/path", set()))
        
        # Unwatch the path
        context.unwatch("test/path", "test_agent")
        
        # Check if the agent is no longer watching
        self.assertNotIn("test_agent", context.watchers.get("test/path", set()))

class TestMessageBroker(MCPTestCase):
    """Tests for the MessageBroker component"""
    
    def test_publish_message(self):
        """Test publishing a message"""
        broker = MessageBroker()
        
        # Publish a message
        message = broker.publish(
            sender="test_sender",
            recipient="test_recipient",
            message_type="test_type",
            content={"key": "value"}
        )
        
        # Check message properties
        self.assertEqual(message.sender, "test_sender")
        self.assertEqual(message.recipient, "test_recipient")
        self.assertEqual(message.message_type, "test_type")
        self.assertEqual(message.content, {"key": "value"})
        
        # Check that the message is in the history
        self.assertIn(message, broker.message_history)
    
    def test_subscribe_unsubscribe(self):
        """Test subscribing and unsubscribing to messages"""
        broker = MessageBroker()
        received_messages = []
        
        # Define a callback
        def callback(message):
            received_messages.append(message)
        
        # Subscribe to messages
        broker.subscribe("test_recipient", callback)
        
        # Publish a message
        broker.publish(
            sender="test_sender",
            recipient="test_recipient",
            message_type="test_type",
            content={"key": "value"}
        )
        
        # Check that the callback was called
        self.assertEqual(len(received_messages), 1)
        self.assertEqual(received_messages[0].sender, "test_sender")
        
        # Unsubscribe from messages
        broker.unsubscribe("test_recipient", callback)
        
        # Publish another message
        broker.publish(
            sender="test_sender",
            recipient="test_recipient",
            message_type="test_type",
            content={"key": "value"}
        )
        
        # Check that the callback was not called again
        self.assertEqual(len(received_messages), 1)
    
    def test_broadcast_message(self):
        """Test broadcasting a message to all recipients"""
        broker = MessageBroker()
        received_messages = []
        
        # Define a callback
        def callback(message):
            received_messages.append(message)
        
        # Subscribe to broadcast messages
        broker.subscribe("*", callback)
        
        # Publish a broadcast message
        broker.publish(
            sender="test_sender",
            recipient="*",
            message_type="test_type",
            content={"key": "value"}
        )
        
        # Check that the callback was called
        self.assertEqual(len(received_messages), 1)
        self.assertEqual(received_messages[0].sender, "test_sender")
        self.assertEqual(received_messages[0].recipient, "*")

class TestLLMProviderRegistry(MCPTestCase):
    """Tests for the LLMProviderRegistry component"""
    
    def test_register_provider(self):
        """Test registering a provider"""
        registry = LLMProviderRegistry()
        
        # Register the mock provider
        registry.register_provider(MockLLMProvider)
        
        # Check that the provider is registered
        self.assertIn("mock", registry.providers)
    
    def test_create_provider_instance(self):
        """Test creating a provider instance"""
        registry = LLMProviderRegistry()
        
        # Register the mock provider
        registry.register_provider(MockLLMProvider)
        
        # Create an instance
        instance = registry.create_provider_instance("mock")
        
        # Check that the instance is created
        self.assertIsInstance(instance, MockLLMProvider)
        self.assertIn("mock_0", registry.instances)
    
    def test_get_provider(self):
        """Test getting a provider instance"""
        registry = LLMProviderRegistry()
        
        # Register the mock provider
        registry.register_provider(MockLLMProvider)
        
        # Create an instance
        registry.create_provider_instance("mock")
        
        # Get the instance
        instance = registry.get_provider("mock_0")
        
        # Check that the instance is returned
        self.assertIsInstance(instance, MockLLMProvider)
    
    def test_set_default_provider(self):
        """Test setting the default provider"""
        registry = LLMProviderRegistry()
        
        # Register the mock provider
        registry.register_provider(MockLLMProvider)
        
        # Set as default
        registry.set_default_provider("mock")
        
        # Check that it's the default
        self.assertEqual(registry.default_provider, "mock")
        
        # Create an instance
        registry.create_provider_instance("mock")
        
        # Get the default instance
        instance = registry.get_provider()
        
        # Check that the default instance is returned
        self.assertIsInstance(instance, MockLLMProvider)

if __name__ == "__main__":
    unittest.main()