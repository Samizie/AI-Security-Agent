from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class SecurityAnalysisResult:
    """Security analysis result structure"""
    vulnerabilities: List[str]
    security_issues: List[str]
    recommendations: List[str]
    risk_level: str
    confidence_score: float

@dataclass
class CodeReviewResult:
    """Code review result structure"""
    best_practices_violations: List[str]
    code_quality_issues: List[str]
    architecture_recommendations: List[str]
    maintainability_score: float
    documentation_gaps: List[str]

@dataclass
class RepoAnalysisData:
    """Repository analysis data"""
    repo_url: str
    repo_path: str
    structure: Dict[str, Any]
    endpoints: List[Dict[str, str]]
    security_files: List[str]
    languages: List[str]