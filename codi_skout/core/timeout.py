from typing import Dict, Any, Optional, Callable, TypeVar, Generic
import logging
import threading
import time
import functools

from .errors import AgentTimeoutError

T = TypeVar('T')

class TimeoutManager:
    """Manager for handling timeouts in agent tasks"""
    
    def __init__(self):
        self.logger = logging.getLogger("mcp.timeout")
        self.tasks: Dict[str, Dict[str, Any]] = {}
    
    def with_timeout(self, timeout: float, task_name: Optional[str] = None):
        """Decorator for functions that need timeout handling"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                nonlocal task_name
                if not task_name:
                    task_name = func.__name__
                
                # Create a result container
                result_container = {"result": None, "exception": None, "completed": False}
                
                # Create a thread to run the function
                def run_task():
                    try:
                        result_container["result"] = func(*args, **kwargs)
                        result_container["completed"] = True
                    except Exception as e:
                        result_container["exception"] = e
                        result_container["completed"] = True
                
                thread = threading.Thread(target=run_task)
                thread.daemon = True
                
                # Register the task
                task_id = f"{task_name}_{time.time()}"
                self.tasks[task_id] = {
                    "name": task_name,
                    "thread": thread,
                    "start_time": time.time(),
                    "timeout": timeout,
                    "result_container": result_container
                }
                
                # Start the thread
                thread.start()
                
                # Wait for the thread to complete or timeout
                thread.join(timeout=timeout)
                
                # Check if the task completed
                if not result_container["completed"]:
                    error_msg = f"Task {task_name} timed out after {timeout} seconds"
                    self.logger.error(error_msg)
                    
                    # Clean up the task
                    if task_id in self.tasks:
                        del self.tasks[task_id]
                    
                    raise AgentTimeoutError(error_msg, {
                        "task_name": task_name,
                        "timeout": timeout
                    })
                
                # Clean up the task
                if task_id in self.tasks:
                    del self.tasks[task_id]
                
                # Check if there was an exception
                if result_container["exception"]:
                    raise result_container["exception"]
                
                return result_container["result"]
            
            return wrapper
        
        return decorator
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task (note: this doesn't actually stop the thread)"""
        if task_id in self.tasks:
            self.logger.info(f"Cancelling task {task_id}")
            del self.tasks[task_id]
            return True
        return False
    
    def get_running_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all running tasks"""
        current_time = time.time()
        
        result = {}
        for task_id, task in self.tasks.items():
            result[task_id] = {
                "name": task["name"],
                "running_time": current_time - task["start_time"],
                "timeout": task["timeout"]
            }
        
        return result