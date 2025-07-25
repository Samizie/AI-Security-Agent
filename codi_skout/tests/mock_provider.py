from typing import Dict, Any, List, Optional
import json
import os
import re

from llm.base_provider import LLMProvider
from .config import get_test_config

class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing"""
    
    provider_name = "mock"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.responses = {}
        self.load_mock_responses()
    
    def load_mock_responses(self):
        """Load mock responses from files"""
        config = get_test_config()
        mock_data_dir = config["mock_data_dir"]
        
        # Load mock responses
        responses_file = os.path.join(mock_data_dir, "mock_responses.json")
        if os.path.exists(responses_file):
            with open(responses_file, 'r', encoding='utf-8') as f:
                self.responses = json.load(f)
        else:
            # Create default mock responses
            self.responses = {
                "default": "This is a mock response from the mock LLM provider.",
                "security_analysis": {
                    "vulnerabilities": [
                        "SQL Injection vulnerability in login form",
                        "Cross-site scripting (XSS) in user profile page",
                        "Insecure direct object references in API endpoints"
                    ],
                    "security_issues": [
                        "Weak password hashing algorithm (MD5)",
                        "Missing CSRF protection",
                        "Sensitive data exposure in error messages"
                    ],
                    "recommendations": [
                        "Use parameterized queries for database operations",
                        "Implement proper input validation and output encoding",
                        "Add CSRF tokens to all forms"
                    ],
                    "risk_level": "HIGH",
                    "confidence_score": 0.8
                },
                "code_review": {
                    "best_practices_violations": [
                        "Inconsistent code formatting",
                        "Lack of comments in complex functions",
                        "Duplicate code in multiple modules"
                    ],
                    "code_quality_issues": [
                        "High cyclomatic complexity in main controller",
                        "Excessive use of global variables",
                        "Long methods with multiple responsibilities"
                    ],
                    "architecture_recommendations": [
                        "Implement dependency injection",
                        "Separate business logic from presentation layer",
                        "Use design patterns for common problems"
                    ],
                    "maintainability_score": 6.5,
                    "documentation_gaps": [
                        "Missing API documentation",
                        "Outdated README file",
                        "No contributing guidelines"
                    ]
                }
            }
            
            # Save default responses
            os.makedirs(mock_data_dir, exist_ok=True)
            with open(responses_file, 'w', encoding='utf-8') as f:
                json.dump(self.responses, f, indent=2)
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt using mock responses"""
        self.logger.info(f"Mock provider generating text for prompt: {prompt[:50]}...")
        
        # Check for specific response patterns
        if "security analysis" in prompt.lower():
            return json.dumps(self.responses.get("security_analysis", self.responses["default"]))
        elif "code review" in prompt.lower():
            return json.dumps(self.responses.get("code_review", self.responses["default"]))
        
        # Default response
        return self.responses.get("default", "Mock response")
    
    def generate_chat_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a response from a chat history using mock responses"""
        self.logger.info(f"Mock provider generating chat response for {len(messages)} messages")
        
        # Get the last message
        last_message = messages[-1]["content"] if messages else ""
        
        # Use the same logic as generate_text
        return self.generate_text(last_message, **kwargs)
    
    @property
    def available_models(self) -> List[str]:
        """Get the list of available models"""
        return ["mock-model"]