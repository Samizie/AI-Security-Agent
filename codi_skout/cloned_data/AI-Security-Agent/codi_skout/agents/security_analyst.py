import os
from pathlib import Path
from typing import Dict, List, Any
import traceback

# LangChain imports
from config import SECURITY_ANALYSIS_PROMPT
from langchain.chains import LLMChain
from langchain_core.runnables import RunnableSequence

from .base_agent import BaseAgent
from core.data_structures import RepoAnalysisData, SecurityAnalysisResult




# Code Security Analyst Agent
class CodeSecurityAnalystAgent(BaseAgent):
    """Agent specialized in security vulnerability analysis"""
    
    def __init__(self, api_key: str):
        super().__init__("CodeSecurityAnalyst", api_key)
        self.security_prompt = SECURITY_ANALYSIS_PROMPT
    
    def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code for security vulnerabilities"""
        try:
            repo_data = RepoAnalysisData(
                repo_url=task_data['repo_url'],
                repo_path=task_data['repo_path'],
                structure=task_data['structure'],
                endpoints=task_data['endpoints'],
                security_files=task_data['structure'].get('security_files', []),
                languages=task_data['structure'].get('languages', [])
            )
            
            # Extract security file contents
            security_content = self.extract_security_file_contents(
                repo_data.repo_path,
                repo_data.security_files
            )
            
            # Run security analysis
            analysis_result = self.analyze_security_vulnerabilities(
                repo_data, security_content
            )
            
            return {
                'success': True,
                'agent': self.name,
                'analysis_type': 'security',
                'result': analysis_result,
                'message': f"Security analysis completed. Risk level: {analysis_result.risk_level}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'agent': self.name,
                'error': str(e),
                'trace': traceback.format_exc(),
                'message': f"Security analysis failed: {str(e)}"
            }
    
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
    
    def analyze_security_vulnerabilities(self, repo_data: RepoAnalysisData, 
                                       security_content: str) -> SecurityAnalysisResult:
        """Perform detailed security analysis using LLM"""
        
        chain = self.security_prompt | self.llm
        
        try:
            result = chain.invoke({
                'code_structure': f"{len(repo_data.structure['files'])} files analyzed",
                'security_files': repo_data.security_files,
                'languages': ', '.join(repo_data.languages),
                'endpoints': [ep['endpoint'] for ep in repo_data.endpoints],
                'file_contents': security_content
            })
            
            # Parse the result
            parsed_result = self.parse_security_analysis(result.content)
            return parsed_result
            
        except Exception as e:
            return SecurityAnalysisResult(
                vulnerabilities=[f"Analysis error: {str(e)}"],
                security_issues=[],
                recommendations=["Re-run analysis after fixing configuration"],
                risk_level="UNKNOWN",
                confidence_score=0.0
            )
    
    def parse_security_analysis(self, analysis_text: str) -> SecurityAnalysisResult:
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
        
        return SecurityAnalysisResult(
            vulnerabilities=vulnerabilities,
            security_issues=security_issues,
            recommendations=recommendations,
            risk_level=risk_level,
            confidence_score=confidence_score
        )