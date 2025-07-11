from typing import List, Dict, Any
from .message_bus import AgentMessage

from agents import (
    GitHubClonerAgent,
    CodeSecurityAnalystAgent,
    CodeReviewerAgent,
    ReporterAgent
)



# Orchestrator - Coordinates all agents
class SecurityOrchestrator:
    """Main orchestrator that coordinates all agents"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.agents = {
            'cloner': GitHubClonerAgent(api_key),
            'security_analyst': CodeSecurityAnalystAgent(api_key),
            'code_reviewer': CodeReviewerAgent(api_key),
            'reporter': ReporterAgent(api_key)
        }
        self.message_bus: List[AgentMessage] = []
    
    def orchestrate_analysis(self, repo_url: str) -> Dict[str, Any]:
        """Orchestrate the complete analysis workflow"""
        
        try:
            # Step 1: Clone repository
            clone_result = self.agents['cloner'].process_task({'repo_url': repo_url})
            
            if not clone_result['success']:
                return {
                    'success': False,
                    'error': clone_result.get('error'),
                    'message': 'Failed to clone repository'
                }
            
            # Step 2: Security Analysis
            security_result = self.agents['security_analyst'].process_task(clone_result)
            
            # Step 3: Code Review
            code_review_result = self.agents['code_reviewer'].process_task(clone_result)
            
            # Step 4: Generate Report
            report_result = self.agents['reporter'].process_task({
                'repo_data': clone_result,
                'security_analysis': security_result,
                'code_review': code_review_result
            })
            
            # Cleanup
            self.agents['cloner'].cleanup()
            
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
            # Cleanup on error
            self.agents['cloner'].cleanup()
            return {
                'success': False,
                'error': str(e),
                'message': f'Orchestration failed: {str(e)}'
            }