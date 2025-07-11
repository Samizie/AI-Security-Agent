import os
import re
from pathlib import Path
from typing import Dict, List, Any

# LangChain imports
from langchain.chains import LLMChain

from .base_agent import BaseAgent
from core.data_structures import RepoAnalysisData, CodeReviewResult
from config import CODE_REVIEW_PROMPT
from config.constants import CODE_EXTENSIONS


class CodeReviewerAgent(BaseAgent):
    """Agent specialized in code quality and best practices review"""
    
    def __init__(self, api_key: str):
        super().__init__("CodeReviewer", api_key)
        self.review_prompt = CODE_REVIEW_PROMPT
    
    def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Review code for quality and best practices"""
        try:
            repo_data = RepoAnalysisData(
                repo_url=task_data['repo_url'],
                repo_path=task_data['repo_path'],
                structure=task_data['structure'],
                endpoints=task_data['endpoints'],
                security_files=task_data['structure'].get('security_files', []),
                languages=task_data['structure'].get('languages', [])
            )
            
            # Extract code samples
            code_samples = self.extract_code_samples(
                repo_data.repo_path, 
                repo_data.structure['files']
            )
            
            # Run code review
            review_result = self.perform_code_review(repo_data, code_samples)
            
            return {
                'success': True,
                'agent': self.name,
                'analysis_type': 'code_review',
                'result': review_result,
                'message': f"Code review completed. Maintainability score: {review_result.maintainability_score}/10"
            }
            
        except Exception as e:
            return {
                'success': False,
                'agent': self.name,
                'error': str(e),
                'message': f"Code review failed: {str(e)}"
            }
    
    def extract_code_samples(self, repo_path: str, files: List[str]) -> str:
        """Extract code samples from various files"""
        code_samples = ""
        


        # Focus on main code files
        code_files = [f for f in files if any(f.endswith(ext) for ext in CODE_EXTENSIONS)]
        
        for file_path in code_files[:15]:  # Limit to first 15 files
            full_path = os.path.join(repo_path, file_path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()[:1500]  # First 1500 chars
                        code_samples += f"\n--- {file_path} ---\n{content}\n"
                except:
                    continue
        
        return code_samples
    
    def perform_code_review(self, repo_data: RepoAnalysisData, code_samples: str) -> CodeReviewResult:
        """Perform comprehensive code review"""
        
        chain = self.review_prompt | self.llm
        
        try:
            result = chain.invoke({
                'languages': ', '.join(repo_data.languages),
                'file_structure': f"{len(repo_data.structure['files'])} files in {len(repo_data.structure.get('directories', []))} directories",
                'code_samples': code_samples,
                'endpoints': [ep['endpoint'] for ep in repo_data.endpoints]
            })
            
            # Parse the result
            parsed_result = self.parse_code_review(result.content)
            return parsed_result
            
        except Exception as e:
            return CodeReviewResult(
                best_practices_violations=[f"Review error: {str(e)}"],
                code_quality_issues=[],
                architecture_recommendations=["Re-run review after fixing configuration"],
                maintainability_score=0.0,
                documentation_gaps=[]
            )
    
    def parse_code_review(self, review_text: str) -> CodeReviewResult:
        """Parse LLM output into structured code review"""
        
        violations = []
        quality_issues = []
        architecture_recs = []
        documentation_gaps = []
        maintainability_score = 5.0
        
        lines = review_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if 'BEST_PRACTICES_VIOLATIONS' in line.upper():
                current_section = 'violations'
            elif 'CODE_QUALITY_ISSUES' in line.upper():
                current_section = 'quality_issues'
            elif 'ARCHITECTURE_CONCERNS' in line.upper():
                current_section = 'architecture'
            elif 'DOCUMENTATION_GAPS' in line.upper():
                current_section = 'documentation'
            elif 'MAINTAINABILITY_SCORE' in line.upper():
                try:
                    score_match = re.search(r'(\d+(?:\.\d+)?)', line)
                    if score_match:
                        maintainability_score = float(score_match.group(1))
                except:
                    pass
            elif line and current_section:
                if current_section == 'violations':
                    violations.append(line)
                elif current_section == 'quality_issues':
                    quality_issues.append(line)
                elif current_section == 'architecture':
                    architecture_recs.append(line)
                elif current_section == 'documentation':
                    documentation_gaps.append(line)
        
        return CodeReviewResult(
            best_practices_violations=violations,
            code_quality_issues=quality_issues,
            architecture_recommendations=architecture_recs,
            maintainability_score=maintainability_score,
            documentation_gaps=documentation_gaps
        )