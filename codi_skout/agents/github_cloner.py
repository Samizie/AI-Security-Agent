import os
import stat
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any
import re


from .base_agent import BaseAgent
from config.constants import SECURITY_PATTERNS, URL_PATTERNS, CODE_EXTENSIONS, ENDPOINT_PATTERNS


# GitHub Cloner Agent
class GitHubClonerAgent(BaseAgent):
    """Agent responsible for cloning GitHub repositories"""
    
    def __init__(self, api_key: str):
        super().__init__("GitHubCloner", api_key)
        self.temp_dir = None
    
    def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clone repository and analyze basic structure"""
        repo_url = task_data.get('repo_url')
        
        try:
            # Clone repository
            clone_result = self.clone_repository(repo_url)
            
            # Analyze basic structure
            structure = self.analyze_code_structure(clone_result['repo_path'])
            
            # Extract endpoints
            endpoints = self.extract_urls_and_endpoints(
                clone_result['repo_path'], 
                structure['exposed_urls']
            )
            
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
                #raise Exception(f"Git clone failed: {result.stderr}")
                print("CLONE STDOUT:", result.stdout)
                print("CLONE STDERR:", result.stderr)
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
            #print(structure)
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





















# import os
# import json
# import stat
# import shutil
# import subprocess
# from pathlib import Path
# from typing import List, Dict, Any

# from langchain.chains import LLMChain
# from langchain.prompts import PromptTemplate

# from .base_agent import BaseAgent


# class GitHubClonerAgent(BaseAgent):
#     """Agent responsible for cloning and analyzing GitHub repositories."""

#     def __init__(self, api_key: str):
#         super().__init__("GitHubCloner", api_key)
#         self.temp_dir = None

#     def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
#         repo_url = task_data.get('repo_url')
#         try:
#             clone_result = self.clone_repository(repo_url)
#             file_list = self.collect_file_metadata(clone_result['repo_path'])

#             structure = self.analyze_structure_with_prompt(file_list)
#             code_snippets = self.extract_code_from_files(clone_result['repo_path'], structure.get("exposed_urls", []))
#             endpoints = self.extract_endpoints_with_prompt(code_snippets)

#             return {
#                 'success': True,
#                 'repo_url': repo_url,
#                 'repo_path': clone_result['repo_path'],
#                 'structure': {**structure, 'files': file_list},
#                 'endpoints': endpoints,
#                 'message': f"Successfully cloned and analyzed {repo_url}"
#             }

#         except Exception as e:
#             return {
#                 'success': False,
#                 'error': str(e),
#                 'message': f"Failed to clone or analyze repository: {str(e)}"
#             }

#     def clone_repository(self, repo_url: str) -> Dict[str, Any]:
#         try:
#             repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
#             base_dir = Path(__file__).resolve().parent.parent / "cloning_data"
#             base_dir.mkdir(parents=True, exist_ok=True)
#             self.temp_dir = str(base_dir / repo_name)

#             if os.path.exists(self.temp_dir):
#                 shutil.rmtree(self.temp_dir, onerror=self.handle_remove_readonly)

#             result = subprocess.run(
#                 ['git', 'clone', repo_url, self.temp_dir],
#                 capture_output=True,
#                 text=True,
#                 timeout=300
#             )

#             if result.returncode != 0:
#                 raise Exception(f"Git clone failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")

#             return {
#                 'success': True,
#                 'repo_path': self.temp_dir,
#                 'stdout': result.stdout,
#                 'stderr': result.stderr
#             }

#         except Exception as e:
#             raise Exception(f"Failed to clone repository: {str(e)}")

#     def collect_file_metadata(self, repo_path: str) -> List[str]:
#         files = []
#         for root, dirs, filenames in os.walk(repo_path):
#             dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]
#             for filename in filenames:
#                 if filename.startswith('.'):
#                     continue
#                 rel_path = os.path.relpath(os.path.join(root, filename), repo_path)
#                 files.append(rel_path)
#         return files

#     def analyze_structure_with_prompt(self, file_list: List[str]) -> Dict[str, Any]:
#         prompt = PromptTemplate(
#             input_variables=["file_list"],
#             template="""
#             You are a static code analyzer. Below is a list of file paths from a repository:

#             {file_list}

#             Based on typical naming conventions and extensions, categorize them into:
#             - config_files
#             - security_files
#             - exposed_urls
#             - database_configs
#             - languages (by extension only)

#             - You must respond in valid JSON no other explanation:
#             {{"config_files": [...], "security_files": [...], "exposed_urls": [...], "database_configs": [...], "languages": [...]}}
#                         """
#         )

#         chain = LLMChain(llm=self.llm, prompt=prompt)
#         formatted_input = "\n".join(file_list)
#         response = chain.run(file_list=formatted_input)

#         try:
#             return json.loads(response)
#         except json.JSONDecodeError:
#             print("Warning: Failed to parse LLM output as JSON.\nResponse:", response)
#             return {
#                 "config_files": [],
#                 "security_files": [],
#                 "exposed_urls": [],
#                 "database_configs": [],
#                 "languages": []
#             }

#     def extract_code_from_files(self, repo_path: str, url_files: List[str], max_chars=1500) -> str:
#         snippets = []
#         for path in url_files:
#             full_path = os.path.join(repo_path, path)
#             if os.path.exists(full_path):
#                 try:
#                     with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
#                         code = f.read()[:max_chars]
#                         snippets.append(f"\n--- {path} ---\n{code}")
#                 except Exception:
#                     continue
#         return "\n".join(snippets)

#     def extract_endpoints_with_prompt(self, code_snippets: str) -> List[Dict[str, str]]:
#         prompt = PromptTemplate(
#             input_variables=["code_snippets"],
#             template="""
#                 You are a senior backend engineer. Given the following code snippets from various files:

#                 {code_snippets}

#                 - Extract all HTTP endpoints
#                 - return a JSON list no explanations, just the JSON:
#                 [
#                 {{"endpoint": "/api/...", "file": "file_name.py", "method": "GET/POST", "framework": "Flask/Express/Django"}}
#                 ]
#                             """
#         )

#         chain = LLMChain(llm=self.llm, prompt=prompt)
#         response = chain.run(code_snippets=code_snippets)

#         try:
#             return json.loads(response)
#         except json.JSONDecodeError:
#             print("Warning: Endpoint extraction returned invalid JSON.\nResponse:", response)
#             return []

#     @staticmethod
#     def handle_remove_readonly(func, path, exc_info):
#         os.chmod(path, stat.S_IWRITE)
#         func(path)

#     def cleanup(self):
#         if self.temp_dir and os.path.exists(self.temp_dir):
#             shutil.rmtree(self.temp_dir, onerror=self.handle_remove_readonly)


























    