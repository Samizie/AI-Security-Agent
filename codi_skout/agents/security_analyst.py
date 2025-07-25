import os
from pathlib import Path
from typing import Dict, List, Any
import traceback
import logging
import uuid

from .base_agent import BaseAgent
from core.mcp_client import MCPClient
from core.errors import ProviderError, AgentExecutionError

class CodeSecurityAnalystAgent(BaseAgent):
    """Agent specialized in security vulnerability analysis"""
    
    def __init__(self, mcp_client: MCPClient):
        super().__init__("CodeSecurityAnalyst", mcp_client)
        
        # Watch for repository context changes
        self.watch_context("repo")
    
    def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code for security vulnerabilities"""
        try:
            # Update status in shared context
            self.set_context("repo/analysis_status/security_analysis", "in_progress")
            
            # Get repository data from context
            repo_context = self.get_context("repo")
            #print(repo_context)
            if not repo_context:
                raise ValueError("Repository context not found")
            
            # Extract security file contents
            security_files = [f["path"] for f in repo_context.get("files", []) 
                             if f.get("is_security_related", False)]
            
            security_content = self.extract_security_file_contents(
                repo_context["repo_path"],
                security_files
            )
            
            # Run security analysis
            analysis_result = self.analyze_security_vulnerabilities(repo_context, security_content)
            
            # Add security findings to context
            repo_context_manager = self.get_context("repo_context_manager")
            if repo_context_manager:
                for vulnerability in analysis_result.get("vulnerabilities", []):
                    finding = {
                        "id": str(uuid.uuid4()),
                        "title": vulnerability,
                        "description": vulnerability,
                        "severity": "MEDIUM",  # Default to medium
                        "file_path": "",  # We don't have this information yet
                        "line_number": None,
                        "code_snippet": None,
                        "recommendation": "",
                        "confidence": 0.7
                    }
                    
                    repo_context_manager.add_security_finding(finding)
            
            # Update status in shared context
            self.set_context("repo/analysis_status/security_analysis", "completed")
            
            return {
                'success': True,
                'agent': self.name,
                'analysis_type': 'security',
                'result': analysis_result,
                'message': f"Security analysis completed. Risk level: {analysis_result.get('risk_level', 'UNKNOWN')}"
            }
            
        except Exception as e:
            # Update status in shared context
            self.set_context("repo/analysis_status/security_analysis", "failed")
            
            self.logger.error(f"Error in security analysis: {str(e)}")
            self.logger.error(traceback.format_exc())
            
            raise AgentExecutionError(f"Security analysis failed: {str(e)}", {
                "agent": self.name,
                "error": str(e),
                "trace": traceback.format_exc()
            })
    
    def extract_security_file_contents(self, repo_path: str, security_files: List[str]) -> str:
        """Extract contents from security-related files"""
        content = ""
        
        for file_path in security_files[:10]:  # Limit to first 10 files
            full_path = os.path.join(repo_path, file_path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        file_content = f.read()[:2000]  # First 2000 chars
                        content += f"\n--- {file_path} ---\n{file_content}\n"
                except:
                    continue
        
        return content
    
    def analyze_security_vulnerabilities(self, repo_context: Dict[str, Any], 
                                       security_content: str) -> Dict[str, Any]:
        """Perform detailed security analysis using LLM"""
        
        # Get the LLM provider
        try:
            llm = self.get_llm()
        except ProviderError as e:
            self.logger.error(f"Error getting LLM provider: {str(e)}")
            # Try fallback to any available provider
            llm = self.get_llm("groq")  # Fallback to Groq if available
        
        # Prepare the prompt
        prompt = f"""
        You are a security expert analyzing a codebase for vulnerabilities.
        
        Repository Information:
        - URL: {repo_context.get('repo_url', 'Unknown')}
        - Files: {len(repo_context.get('files', []))} files analyzed
        - Languages: {', '.join(repo_context.get('languages', []))}
        - API Endpoints: {len(repo_context.get('api_endpoints', []))} endpoints found
        
        Security-related file contents:
        {security_content}
        
        Based on this information, identify:
        
        CRITICAL_VULNERABILITIES:
        
        HIGH_RISK_ISSUES:
        
        MEDIUM_RISK_ISSUES:
        
        SECURITY_RECOMMENDATIONS:
        
        RISK_ASSESSMENT:
        Overall risk level (CRITICAL, HIGH, MEDIUM, LOW) and confidence score (0-1)
        """
        
        try:
            # Generate the analysis
            response = llm.generate_text(prompt)
            
            # Parse the result
            parsed_result = self.parse_security_analysis(response)
            return parsed_result
            
        except Exception as e:
            self.logger.error(f"Error in LLM analysis: {str(e)}")
            
            # Create a default result
            return {
                "vulnerabilities": [f"Analysis error: {str(e)}"],
                "security_issues": [],
                "recommendations": ["Re-run analysis after fixing configuration"],
                "risk_level": "UNKNOWN",
                "confidence_score": 0.0
            }
    
    def parse_security_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse LLM output into structured security analysis"""
        
        vulnerabilities = []
        security_issues = []
        recommendations = []
        risk_level = "MEDIUM"
        confidence_score = 0.7
        
        lines = analysis_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if 'CRITICAL_VULNERABILITIES' in line.upper():
                current_section = 'critical_vulnerabilities'
            elif 'HIGH_RISK_ISSUES' in line.upper():
                current_section = 'high_risk_issues'
            elif 'MEDIUM_RISK_ISSUES' in line.upper():
                current_section = 'medium_risk_issues'
            elif 'SECURITY_RECOMMENDATIONS' in line.upper():
                current_section = 'recommendations'
            elif 'RISK_ASSESSMENT' in line.upper():
                current_section = 'risk_assessment'
            elif line and current_section:
                if current_section in ['critical_vulnerabilities', 'high_risk_issues', 'medium_risk_issues']:
                    vulnerabilities.append(line)
                elif current_section == 'recommendations':
                    recommendations.append(line)
                elif current_section == 'risk_assessment':
                    if 'CRITICAL' in line.upper():
                        risk_level = 'CRITICAL'
                    elif 'HIGH' in line.upper():
                        risk_level = 'HIGH'
                    elif 'LOW' in line.upper():
                        risk_level = 'LOW'
                    # Extract confidence score if present
                    if 'confidence' in line.lower():
                        try:
                            import re
                            score_match = re.search(r'(\d+(?:\.\d+)?)', line)
                            if score_match:
                                confidence_score = float(score_match.group(1))
                                if confidence_score > 1:
                                    confidence_score = confidence_score / 100
                        except:
                            pass
        
        # Create the result object
        return {
            "vulnerabilities": vulnerabilities,
            "security_issues": security_issues,
            "recommendations": recommendations,
            "risk_level": risk_level,
            "confidence_score": confidence_score
        }
    
    def on_context_change(self, path: str, changed_by: str, value: Any) -> None:
        """Handle context change notifications"""
        # React to changes in the repository context
        if path.startswith("repo/files") and changed_by != self.name:
            self.logger.info(f"Repository files changed by {changed_by}, may need to re-analyze")