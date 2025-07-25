import os
from typing import Dict, Any

# Test configuration
TEST_CONFIG = {
    # LLM Provider API keys (use environment variables for security)
    "openai_api_key": os.environ.get("OPENAI_API_KEY", ""),
    "anthropic_api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
    "groq_api_key": os.environ.get("GROQ_API_KEY", ""),
    
    # Test repositories
    "test_repos": [
        "https://github.com/pallets/flask",
        "https://github.com/django/django",
        "https://github.com/expressjs/express"
    ],
    
    # Test timeouts
    "short_timeout": 5,  # seconds
    "medium_timeout": 30,  # seconds
    "long_timeout": 120,  # seconds
    
    # Mock data directory
    "mock_data_dir": os.path.join(os.path.dirname(__file__), "mock_data"),
    
    # Test output directory
    "output_dir": os.path.join(os.path.dirname(__file__), "output")
}

# Create directories if they don't exist
os.makedirs(TEST_CONFIG["mock_data_dir"], exist_ok=True)
os.makedirs(TEST_CONFIG["output_dir"], exist_ok=True)

def get_test_config() -> Dict[str, Any]:
    """Get the test configuration"""
    return TEST_CONFIG