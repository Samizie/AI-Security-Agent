import unittest
import os
import time
from typing import Dict, Any

from core.context_init import initialize_context_system
from core.llm_provider_registry import LLMProviderRegistry
from llm.provider_factory import LLMProviderFactory
from core.orchestrator import SecurityOrchestrator
from tests.base_test import MCPTestCase
from tests.mock_provider import MockLLMProvider

class TestEndToEnd(MCPTestCase):
    """End-to-end tests for the complete system"""
    
    def setUp(self):
        super().setUp()
        
        # Register mock provider
        self.llm_registry.register_provider(MockLLMProvider)
        self.llm_registry.create_provider_instance("mock")
        self.llm_registry.set_default_provider("mock")
        
        # Create orchestrator
        self.orchestrator = SecurityOrchestrator(
            message_broker=self.context_system["message_broker"],
            shared_context=self.context_system["shared_context"],
            llm_registry=self.llm_registry
        )
    
    def test_full_analysis_workflow(self):
        """Test the complete analysis workflow with mock data"""
        # Skip if running in CI environment
        if os.environ.get("CI"):
            self.skipTest("Skipping test that requires git in CI environment")
        
        # Use a small test repository
        repo_url = "https://github.com/pallets/flask"
        
        # Run the analysis
        result = self.orchestrator.orchestrate_analysis(repo_url)
        
        # Check the result
        self.assertTrue(result["success"])
        self.assertIn("clone", result["results"])
        self.assertIn("security", result["results"])
        self.assertIn("code_review", result["results"])
        self.assertIn("report", result["results"])
        
        # Check that the clone was successful
        self.assertTrue(result["results"]["clone"]["success"])
        
        # Check that the security analysis was successful
        self.assertTrue(result["results"]["security"]["success"])
        
        # Check that the code review was successful
        self.assertTrue(result["results"]["code_review"]["success"])
        
        # Check that the report was successful
        self.assertTrue(result["results"]["report"]["success"])
        
        # Clean up
        self.orchestrator.cleanup()
    
    def test_error_handling(self):
        """Test error handling in the workflow"""
        # Use a non-existent repository to trigger an error
        repo_url = "https://github.com/non-existent/repo"
        
        # Run the analysis
        result = self.orchestrator.orchestrate_analysis(repo_url)
        
        # Check the result
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertIn("message", result)
        
        # Clean up
        self.orchestrator.cleanup()

if __name__ == "__main__":
    unittest.main()