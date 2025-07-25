from typing import Dict, Any, List, Optional
import logging
import time
import traceback

from .message_broker import MessageBroker
from .shared_context import SharedContext
from .llm_provider_registry import LLMProviderRegistry
from .error_handler import ErrorHandler
from .timeout import TimeoutManager
from .errors import AgentError, AgentTimeoutError
from agents.agent_factory import AgentFactory

class SecurityOrchestrator:
    """Main orchestrator that coordinates all agents using MCP"""
    
    def __init__(self, message_broker: MessageBroker, shared_context: SharedContext,
                llm_registry: LLMProviderRegistry):
        self.message_broker = message_broker
        self.shared_context = shared_context
        self.llm_registry = llm_registry
        self.agent_factory = AgentFactory(message_broker, shared_context, llm_registry)
        self.error_handler = ErrorHandler()
        self.timeout_manager = TimeoutManager()
        self.logger = logging.getLogger("orchestrator")
    
    @ErrorHandler().with_error_handling(max_retries=2)
    @TimeoutManager().with_timeout(timeout=600, task_name="orchestrate_analysis")
    def orchestrate_analysis(self, repo_url: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Orchestrate the complete analysis workflow"""
        
        config = config or {}
        self.logger.info(f"Starting analysis for {repo_url}")
        
        try:
            # Create agents
            cloner = self.agent_factory.create_agent("github_cloner")
            security_analyst = self.agent_factory.create_agent("security_analyst")
            code_reviewer = self.agent_factory.create_agent("code_reviewer")
            reporter = self.agent_factory.create_agent("reporter")
            
            # Step 1: Clone repository
            self.logger.info("Step 1: Cloning repository")
            clone_result = cloner.process_task({'repo_url': repo_url})
            print(f"Clone result: {clone_result}")
            
            # Set the repo context for other agents to use
            self.set_context("repo", clone_result)

            if not clone_result['success']:
                self.logger.error(f"Failed to clone repository: {clone_result.get('error')}")
                return {
                    'success': False,
                    'error': clone_result.get('error'),
                    'message': 'Failed to clone repository'
                }
            
            # Determine if we should run in parallel
            parallel_execution = config.get("parallel_execution", False)
            
            if parallel_execution:
                # Step 2 & 3: Run security analysis and code review in parallel
                self.logger.info("Steps 2 & 3: Running security analysis and code review in parallel")
                
                # Use the timeout manager to run tasks with timeouts
                security_task = self.timeout_manager.with_timeout(300, "security_analysis")(
                    security_analyst.process_task
                )
                code_review_task = self.timeout_manager.with_timeout(300, "code_review")(
                    code_reviewer.process_task
                )
                
                # Start the tasks in separate threads
                import threading
                
                security_result_container = {"result": None, "exception": None}
                code_review_result_container = {"result": None, "exception": None}
                
                def run_security_analysis():
                    try:
                        security_result_container["result"] = security_task(clone_result)
                    except Exception as e:
                        security_result_container["exception"] = e
                
                def run_code_review():
                    try:
                        code_review_result_container["result"] = code_review_task(clone_result)
                    except Exception as e:
                        code_review_result_container["exception"] = e
                
                security_thread = threading.Thread(target=run_security_analysis)
                code_review_thread = threading.Thread(target=run_code_review)
                
                security_thread.start()
                code_review_thread.start()
                
                # Wait for both threads to complete
                security_thread.join()
                code_review_thread.join()
                
                # Check for exceptions
                if security_result_container["exception"]:
                    self.logger.error(f"Security analysis failed: {security_result_container['exception']}")
                    security_result = {
                        'success': False,
                        'error': str(security_result_container["exception"]),
                        'message': 'Security analysis failed'
                    }
                else:
                    security_result = security_result_container["result"]
                
                if code_review_result_container["exception"]:
                    self.logger.error(f"Code review failed: {code_review_result_container['exception']}")
                    code_review_result = {
                        'success': False,
                        'error': str(code_review_result_container["exception"]),
                        'message': 'Code review failed'
                    }
                else:
                    code_review_result = code_review_result_container["result"]
            else:
                # Run sequentially
                # Step 2: Security Analysis
                self.logger.info("Step 2: Running security analysis")
                try:
                    security_result = security_analyst.process_task(clone_result)
                except AgentError as e:
                    self.logger.error(f"Security analysis failed: {str(e)}")
                    security_result = {
                        'success': False,
                        'error': str(e),
                        'message': 'Security analysis failed'
                    }
                
                # Step 3: Code Review
                self.logger.info("Step 3: Running code review")
                try:
                    code_review_result = code_reviewer.process_task(clone_result)
                except AgentError as e:
                    self.logger.error(f"Code review failed: {str(e)}")
                    code_review_result = {
                        'success': False,
                        'error': str(e),
                        'message': 'Code review failed'
                    }
            
            # Step 4: Generate Report
            self.logger.info("Step 4: Generating report")
            try:
                report_result = reporter.process_task({
                    'repo_data': clone_result,
                    'security_analysis': security_result,
                    'code_review': code_review_result
                })
            except AgentError as e:
                self.logger.error(f"Report generation failed: {str(e)}")
                report_result = {
                    'success': False,
                    'error': str(e),
                    'message': 'Report generation failed'
                }
            
            # Cleanup
            cloner.cleanup()
            
            return {
                'success': True,
                'results': {
                    'clone': clone_result,
                    'security': security_result,
                    'code_review': code_review_result,
                    'report': report_result
                }
            }
            
        except Exception as e:
            self.logger.error(f"Orchestration failed: {str(e)}")
            self.logger.error(traceback.format_exc())
            
            # Cleanup on error
            self.agent_factory.cleanup()
            
            return {
                'success': False,
                'error': str(e),
                'message': f'Orchestration failed: {str(e)}'
            }
    
    def cleanup(self):
        """Clean up all resources"""
        self.agent_factory.cleanup()