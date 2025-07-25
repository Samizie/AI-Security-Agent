import unittest
import os
from typing import Dict, Any

from core.mcp_client import MCPClient
from agents.base_agent import BaseAgent
from agents.github_cloner import GitHubClonerAgent
from agents.security_analyst import CodeSecurityAnalystAgent
from tests.base_test import MCPTestCase
from tests.mock_provider import MockLLMProvider

class TestBaseAgent(MCPTestCase):
    """Tests for the BaseAgent class"""
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        # Create MCP client
        mcp_client = MCPClient(
            agent_name="test_agent",
            message_broker=self.context_system["message_broker"],
            shared_context=self.context_system["shared_context"],
            llm_registry=self.llm_registry
        )
        
        # Create a concrete agent class for testing
        class TestAgent(BaseAgent):
            def process_task(self, task_data):
                return {"success": True, "result": "test_result"}
        
        # Create the agent
        agent = TestAgent("TestAgent", mcp_client)
        
        # Check agent properties
        self.assertEqual(agent.name, "TestAgent")
        self.assertEqual(agent.mcp_client, mcp_client)
    
    def test_agent_message_handling(self):
        """Test agent message handling"""
        # Create MCP client
        mcp_client = MCPClient(
            agent_name="test_agent",
            message_broker=self.context_system["message_broker"],
            shared_context=self.context_system["shared_context"],
            llm_registry=self.llm_registry
        )
        
        # Create a concrete agent class for testing
        class TestAgent(BaseAgent):
            def __init__(self, name, mcp_client):
                super().__init__(name, mcp_client)
                self.task_requests = []
                self.context_changes = []
            
            def process_task(self, task_data):
                self.task_requests.append(task_data)
                return {"success": True, "result": "test_result"}
            
            def on_context_change(self, path, changed_by, value):
                self.context_changes.append((path, changed_by, value))
        
        # Create the agent
        agent = TestAgent("TestAgent", mcp_client)
        
        # Send a task request message
        message = self.context_system["message_broker"].publish(
            sender="test_sender",
            recipient="test_agent",
            message_type="task_request",
            content={"task": "test_task"}
        )
        
        # Check that the agent processed the task
        self.assertEqual(len(agent.task_requests), 1)
        self.assertEqual(agent.task_requests[0]["task"], "test_task")
        
        # Send a context change message
        message = self.context_system["message_broker"].publish(
            sender="context_system",
            recipient="test_agent",
            message_type="context_change",
            content={
                "path": "test/path",
                "changed_by": "test_changer",
                "value": "test_value"
            }
        )
        
        # Check that the agent processed the context change
        self.assertEqual(len(agent.context_changes), 1)
        self.assertEqual(agent.context_changes[0][0], "test/path")
        self.assertEqual(agent.context_changes[0][1], "test_changer")
        self.assertEqual(agent.context_changes[0][2], "test_value")

class TestGitHubClonerAgent(MCPTestCase):
    """Tests for the GitHubClonerAgent"""
    
    def setUp(self):
        super().setUp()
        
        # Create MCP client
        self.mcp_client = MCPClient(
            agent_name="cloner_agent",
            message_broker=self.context_system["message_broker"],
            shared_context=self.context_system["shared_context"],
            llm_registry=self.llm_registry
        )
        
        # Create the agent
        self.agent = GitHubClonerAgent(self.mcp_client)
    
    def test_clone_repository(self):
        """Test cloning a repository"""
        # Skip if running in CI environment
        if os.environ.get("CI"):
            self.skipTest("Skipping test that requires git in CI environment")
        
        # Use a small test repository
        repo_url = "https://github.com/pallets/flask"
        
        # Clone the repository
        result = self.agent.clone_repository(repo_url)
        
        # Check the result
        self.assertTrue(result["success"])
        self.assertTrue(os.path.exists(result["repo_path"]))
        
        # Clean up
        self.agent.cleanup()

class TestSecurityAnalystAgent(MCPTestCase):
    """Tests for the CodeSecurityAnalystAgent"""
    
    def setUp(self):
        super().setUp()
        
        # Register mock provider
        self.llm_registry.register_provider(MockLLMProvider)
        self.llm_registry.create_provider_instance("mock")
        self.llm_registry.set_default_provider("mock")
        
        # Create MCP client
        self.mcp_client = MCPClient(
            agent_name="security_agent",
            message_broker=self.context_system["message_broker"],
            shared_context=self.context_system["shared_context"],
            llm_registry=self.llm_registry
        )
        
        # Create the agent
        self.agent = CodeSecurityAnalystAgent(self.mcp_client)
        
        # Set up mock repository data
        self.repo_context = {
            "repo_url": "https://github.com/test/repo",
            "repo_path": "/tmp/test_repo",
            "files": [
                {
                    "path": "app.py",
                    "language": "python",
                    "size": 1000,
                    "is_security_related": True,
                    "is_config": False,
                    "is_test": False
                }
            ],
            "languages": ["python"],
            "api_endpoints": [
                {
                    "path": "/api/users",
                    "method": "GET",
                    "file_path": "app.py",
                    "line_number": None,
                    "description": None,
                    "authentication_required": None
                }
            ]
        }
        
        # Set the repository context
        self.context_system["shared_context"].set("repo", self.repo_context)
    
    def test_security_analysis(self):
        """Test security analysis with mock data"""
        # Create mock security file content
        security_content = """
        --- app.py ---
        @app.route('/login', methods=['POST'])
        def login():
            username = request.form['username']
            password = request.form['password']
            
            # Vulnerable SQL query
            query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            user = db.execute(query).fetchone()
            
            if user:
                session['user_id'] = user['id']
                return redirect('/')
            else:
                return render_template('login.html', error='Invalid credentials')
        """
        
        # Mock the extract_security_file_contents method
        self.agent.extract_security_file_contents = lambda repo_path, security_files: security_content
        
        # Run the security analysis
        try:
            result = self.agent.process_task({})
            
            # Check the result
            self.assertTrue(result["success"])
            self.assertEqual(result["agent"], "CodeSecurityAnalyst")
            self.assertEqual(result["analysis_type"], "security")
        except Exception as e:
            self.fail(f"Security analysis failed with error: {str(e)}")

if __name__ == "__main__":
    unittest.main()