import os
import stat
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any
import re
import logging

from .base_agent import BaseAgent
from core.mcp_client import MCPClient
from config.constants import SECURITY_PATTERNS, URL_PATTERNS, CODE_EXTENSIONS, ENDPOINT_PATTERNS

class GitHubClonerAgent(BaseAgent):
    """Agent responsible for cloning GitHub repositories"""
    
    def __init__(self, mcp_client: MCPClient):
        super().__init__("GitHubCloner", mcp_client)
        self.temp_dir = None
        
        # Watch for repository context changes
        self.watch_context("repo")
    
    def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clone repository and analyze basic structure"""
        repo_url = task_data.get('repo_url')
        
        try:
            # Update status in shared context
            self.set_context("repo/analysis_status/cloning", "in_progress")
            
            # Clone repository
            clone_result = self.clone_repository(repo_url)
            
            # Initialize repository context
            repo_context_manager = self.get_context("repo_context_manager")
            if repo_context_manager:
                repo_context_manager.initialize_repo_context(
                    repo_url=repo_url,
                    repo_path=clone_result['repo_path']
                )
            
            # Analyze basic structure
            structure = self.analyze_code_structure(clone_result['repo_path'])
            
            # Extract endpoints
            endpoints = self.extract_urls_and_endpoints(
                clone_result['repo_path'], 
                structure['exposed_urls']
            )
            
            # Update repository context with files
            if repo_context_manager:
                repo_files = []
                for file_path in structure['files']:
                    ext = Path(file_path).suffix.lower()
                    repo_files.append({
                        "path": file_path,
                        "language": ext[1:] if ext in CODE_EXTENSIONS else None,
                        "size": os.path.getsize(os.path.join(clone_result['repo_path'], file_path)),
                        "is_security_related": file_path in structure['security_files'],
                        "is_config": file_path in structure['config_files'],
                        "is_test": "test" in file_path.lower() or "spec" in file_path.lower()
                    })
                
                repo_context_manager.update_repo_files(repo_files)
                
                # Add API endpoints
                for endpoint in endpoints:
                    repo_context_manager.add_api_endpoint({
                        "path": endpoint.get("endpoint", ""),
                        "method": endpoint.get("type", "GET"),
                        "file_path": endpoint.get("file", ""),
                        "line_number": None,
                        "description": None,
                        "authentication_required": None
                    })
            
            # Update status in shared context
            self.set_context("repo/analysis_status/cloning", "completed")
            
            result = {
                'success': True,
                'repo_url': repo_url,
                'repo_path': clone_result['repo_path'],
                'structure': structure,
                'endpoints': endpoints,
                'message': f"Successfully cloned and analyzed {repo_url}"
            }
            
            return result
            
        except Exception as e:
            # Update status in shared context
            self.set_context("repo/analysis_status/cloning", "failed")
            
            self.logger.error(f"Error cloning repository: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to clone repository: {str(e)}"
            }
    
    def clone_repository(self, repo_url: str) -> Dict[str, Any]:
        """Clone GitHub repository to temporary directory"""
        try:
            repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
            base_dir = Path(__file__).resolve().parent.parent / "cloning_data"
            base_dir.mkdir(parents=True, exist_ok=True)

            self.temp_dir = str(base_dir / repo_name)

            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, onerror=self.handle_remove_readonly)
            
            result = subprocess.run(
                ['git', 'clone', repo_url, self.temp_dir],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                self.logger.error(f"Git clone failed: {result.stderr}")
                raise Exception(f"Git clone failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
            
            return {
                'success': True,
                'repo_path': self.temp_dir,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except Exception as e:
            raise Exception(f"Failed to clone repository: {str(e)}")
    
    def analyze_code_structure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze repository structure and extract key information"""
        structure = {
            'files': [],
            'directories': [],
            'languages': set(),
            'config_files': [],
            'security_files': [],
            'exposed_urls': [],
            'database_configs': []
        }
        
        try:
            for root, dirs, files in os.walk(repo_path):
                # Skip hidden directories and common ignore patterns
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]
                
                for file in files:
                    if file.startswith('.'):
                        continue
                        
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_path)
                    
                    structure['files'].append(relative_path)
                    
                    # Detect language by extension
                    ext = Path(file).suffix.lower()
                    if ext in CODE_EXTENSIONS:
                        structure['languages'].add(ext[1:])
                    
                    # Check for security-related files
                    if any(pattern.lower() in file.lower() for pattern in SECURITY_PATTERNS):
                        structure['security_files'].append(relative_path)
                    
                    # Check for URL/route definition files
                    if any(pattern.lower() in file.lower() for pattern in URL_PATTERNS):
                        structure['exposed_urls'].append(relative_path)
            
            structure['languages'] = list(structure['languages'])
            return structure
            
        except Exception as e:
            raise Exception(f"Failed to analyze code structure: {str(e)}")
    
    def extract_urls_and_endpoints(self, repo_path: str, url_files: List[str]) -> List[Dict[str, str]]:
        """Extract URLs and endpoints from route files"""
        endpoints = []
        
        for file_path in url_files:
            full_path = os.path.join(repo_path, file_path)
            if not os.path.exists(full_path):
                continue
                
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Simple pattern matching for common frameworks
                patterns = ENDPOINT_PATTERNS
                
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        endpoints.append({
                            'endpoint': match,
                            'file': file_path,
                            'type': 'route'
                        })
                        
            except Exception as e:
                continue
        
        return endpoints
    
    @staticmethod
    def handle_remove_readonly(func, path, exc_info):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, onerror=self.handle_remove_readonly)
        
        # Call parent cleanup
        super().cleanup()