import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from .base_agent import BaseAgent
from core.data_structures import SecurityAnalysisResult, CodeReviewResult



# Reporter Agent
class ReporterAgent(BaseAgent):
    """Agent responsible for collating and formatting reports"""
    
    def __init__(self, api_key: str):
        super().__init__("Reporter", api_key)
    
    def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive report from all agent analyses"""
        try:
            repo_data = task_data.get('repo_data')
            security_analysis = task_data.get('security_analysis')
            code_review = task_data.get('code_review')
            
            # Generate comprehensive report
            report = self.generate_comprehensive_report(
                repo_data, security_analysis, code_review
            )
            
            return {
                'success': True,
                'agent': self.name,
                'report': report,
                'message': "Comprehensive report generated successfully"
            }
            
        except Exception as e:
            return {
                'success': False,
                'agent': self.name,
                'error': str(e),
                'message': f"Report generation failed: {str(e)}"
            }
    
    def generate_comprehensive_report(self, repo_data: Dict[str, Any], 
                                    security_analysis: Dict[str, Any], 
                                    code_review: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final comprehensive report"""
        #print(repo_data)
        # Extract results
        security_result = security_analysis.get('result') if security_analysis.get('success') else None
        review_result = code_review.get('result') if code_review.get('success') else None
        
        # Calculate overall scores
        overall_risk = self.calculate_overall_risk(security_result, review_result)
        overall_quality = self.calculate_overall_quality(security_result, review_result)
        
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'repository': repo_data.get('repo_url'),
                'analysis_agents': ['GitHubCloner', 'CodeSecurityAnalyst', 'CodeReviewer', 'Reporter']
            },
            'executive_summary': {
                'overall_risk_level': overall_risk,
                'code_quality_score': overall_quality,
                'total_files_analyzed': len(repo_data.get('structure', {}).get('files', [])),
                'languages_detected': repo_data.get('languages', []),
                'critical_findings': self.extract_critical_findings(security_result, review_result)
            },
            'repository_overview': {
                'structure': repo_data.get('structure', {}),
                'endpoints': repo_data.get('endpoints', []),
                'security_files': repo_data.get('security_files', []),
                'languages': repo_data.get('languages', [])
            },
            'security_analysis': {
                'status': security_analysis.get('success', False),
                'risk_level': security_result.risk_level if security_result else 'UNKNOWN',
                'confidence_score': security_result.confidence_score if security_result else 0.0,
                'vulnerabilities': security_result.vulnerabilities if security_result else [],
                'security_issues': security_result.security_issues if security_result else [],
                'recommendations': security_result.recommendations if security_result else []
            },
            'code_review': {
                'status': code_review.get('success', False),
                'maintainability_score': review_result.maintainability_score if review_result else 0.0,
                'best_practices_violations': review_result.best_practices_violations if review_result else [],
                'code_quality_issues': review_result.code_quality_issues if review_result else [],
                'architecture_recommendations': review_result.architecture_recommendations if review_result else [],
                'documentation_gaps': review_result.documentation_gaps if review_result else []
            },
            'actionable_recommendations': self.generate_actionable_recommendations(security_result, review_result),
            'priority_matrix': self.create_priority_matrix(security_result, review_result)
        }
        
        return report
    
    def calculate_overall_risk(self, security_result, review_result) -> str:
        """Calculate overall risk level"""
        if not security_result:
            return "UNKNOWN"
        
        risk_levels = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        security_risk = risk_levels.get(security_result.risk_level, 2)
        
        # Factor in code quality
        if review_result and review_result.maintainability_score < 3:
            security_risk = min(security_risk + 1, 4)
        
        risk_names = {4: 'CRITICAL', 3: 'HIGH', 2: 'MEDIUM', 1: 'LOW'}
        return risk_names.get(security_risk, 'MEDIUM')
    
    def calculate_overall_quality(self, security_result, review_result) -> float:
        """Calculate overall code quality score"""
        if not review_result:
            return 5.0
        
        quality_score = review_result.maintainability_score
        
        # Adjust based on security findings
        if security_result:
            if security_result.risk_level == 'CRITICAL':
                quality_score = max(quality_score - 2, 0)
            elif security_result.risk_level == 'HIGH':
                quality_score = max(quality_score - 1, 0)
        
        return round(quality_score, 1)
    
    def extract_critical_findings(self, security_result, review_result) -> List[str]:
        """Extract the most critical findings"""
        critical_findings = []
        
        if security_result:
            # Add critical vulnerabilities
            critical_findings.extend(security_result.vulnerabilities[:3])
        
        if review_result:
            # Add critical code quality issues
            critical_findings.extend(review_result.best_practices_violations[:3])
        
        return critical_findings[:5]  # Limit to top 5
    
    def generate_actionable_recommendations(self, security_result, review_result) -> List[Dict[str, str]]:
        """Generate prioritized, actionable recommendations"""
        recommendations = []
        
        if security_result:
            for rec in security_result.recommendations[:3]:
                recommendations.append({
                    'category': 'Security',
                    'priority': 'HIGH',
                    'action': rec
                })
        
        if review_result:
            for rec in review_result.architecture_recommendations[:3]:
                recommendations.append({
                    'category': 'Code Quality',
                    'priority': 'MEDIUM',
                    'action': rec
                })
        
        return recommendations
    
    def create_priority_matrix(self, security_result, review_result) -> Dict[str, List[str]]:
        """Create a priority matrix for fixes"""
        matrix = {
            'immediate_action': [],
            'short_term': [],
            'long_term': []
        }
        
        if security_result and security_result.risk_level in ['CRITICAL', 'HIGH']:
            matrix['immediate_action'].extend(security_result.vulnerabilities[:2])
        
        if review_result and review_result.maintainability_score < 4:
            matrix['short_term'].extend(review_result.best_practices_violations[:2])
        
        if review_result:
            matrix['long_term'].extend(review_result.architecture_recommendations[:2])
        
        return matrix
