from langchain.prompts import PromptTemplate

CODE_REVIEW_PROMPT = PromptTemplate(
    input_variables=["languages", "file_structure", "code_samples", "endpoints"],
    template="""
    You are a senior software engineer and code review specialist with expertise in multiple programming languages.
    
    Codebase Analysis:
    - Programming Languages: {languages}
    - File Structure: {file_structure}
    - Code Samples: {code_samples}
    - API Endpoints: {endpoints}
    
    Perform a comprehensive code quality review focusing on:
    
    BEST_PRACTICES_VIOLATIONS:
    - Naming conventions violations
    - Code organization issues
    - Design pattern misuse
    - SOLID principle violations
    - Language-specific best practices
    
    CODE_QUALITY_ISSUES:
    - Code duplication
    - Complex functions/methods
    - Poor error handling
    - Inefficient algorithms
    - Memory/performance issues
    
    ARCHITECTURE_CONCERNS:
    - Tight coupling
    - Poor separation of concerns
    - Missing abstractions
    - Scalability issues
    - Maintainability problems
    
    DOCUMENTATION_GAPS:
    - Missing docstrings/comments
    - Inadequate README
    - Missing API documentation
    - Unclear code comments
    
    IMPROVEMENT_RECOMMENDATIONS:
    - Refactoring suggestions
    - Design improvements
    - Performance optimizations
    - Testing recommendations
    
    MAINTAINABILITY_SCORE: [0-10]
    Provide specific, actionable feedback with file references where possible.
    """
)

SECURITY_ANALYSIS_PROMPT = PromptTemplate(
    input_variables=["code_structure", "security_files", "languages", "endpoints", "file_contents"],
    template="""
    You are a senior cybersecurity analyst with expertise in code security analysis.
    
    Repository Analysis:
    - Programming Languages: {languages}
    - Security-related files: {security_files}
    - Code structure: {code_structure}
    - Exposed endpoints: {endpoints}
    - Sample file contents: {file_contents}
    
    Perform a comprehensive security analysis and provide:
    
    CRITICAL_VULNERABILITIES:
    - SQL Injection risks
    - Cross-Site Scripting (XSS) vulnerabilities
    - Authentication bypass possibilities
    - Authorization flaws
    - Remote Code Execution risks
    
    HIGH_RISK_ISSUES:
    - Hardcoded credentials
    - Insecure cryptography
    - Weak session management
    - Input validation failures
    - Insecure file handling
    
    MEDIUM_RISK_ISSUES:
    - Configuration weaknesses
    - Missing security headers
    - Improper error handling
    - Logging sensitive data
    - Dependency vulnerabilities
    
    SECURITY_RECOMMENDATIONS:
    - Immediate actions required
    - Security controls to implement
    - Code changes needed
    - Security testing approaches
    
    RISK_ASSESSMENT:
    - Overall risk level: [CRITICAL/HIGH/MEDIUM/LOW]
    - Confidence score: [0-1]
    - Priority vulnerabilities to fix first
    
    Provide specific, actionable findings with file references where possible.
    """
)