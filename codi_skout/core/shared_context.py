from typing import Dict, Any, List, Optional, Set
import json
import logging

class SharedContext:
    """Manager for shared context between agents"""
    
    def __init__(self):
        self.context: Dict[str, Any] = {}
        self.watchers: Dict[str, Set[str]] = {}  # path -> set of agent names
        self.logger = logging.getLogger("mcp.shared_context")
    
    def set(self, path: str, value: Any, agent: Optional[str] = None) -> None:
        """Set a value in the shared context"""
        # Parse the path and navigate to the correct location
        parts = path.strip("/").split("/")
        current = self.context
        
        # Create intermediate dictionaries if they don't exist
        for i, part in enumerate(parts[:-1]):
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        
        # Set the value
        current[parts[-1]] = value
        self.logger.debug(f"Set context value at {path}")
        
        # Notify watchers
        if agent:
            self._notify_watchers(path, agent)
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get a value from the shared context"""
        # Parse the path and navigate to the correct location
        parts = path.strip("/").split("/")
        current = self.context
        
        # Navigate through the path
        for part in parts:
            if part not in current:
                return default
            current = current[part]
        
        return current
    
    def watch(self, path: str, agent: str) -> None:
        """Register an agent to watch a path for changes"""
        if path not in self.watchers:
            self.watchers[path] = set()
        
        self.watchers[path].add(agent)
        self.logger.debug(f"Agent {agent} is now watching {path}")
    
    def unwatch(self, path: str, agent: str) -> None:
        """Unregister an agent from watching a path"""
        if path in self.watchers and agent in self.watchers[path]:
            self.watchers[path].remove(agent)
            self.logger.debug(f"Agent {agent} is no longer watching {path}")
    
    def _notify_watchers(self, path: str, agent: str) -> None:
        """Notify watchers of a change to a path"""
        # Find all watchers that should be notified
        # This includes watchers of the exact path and parent paths
        parts = path.strip("/").split("/")
        paths_to_check = []
        
        # Build list of paths to check (the path itself and all parent paths)
        current_path = ""
        for part in parts:
            current_path = f"{current_path}/{part}" if current_path else part
            paths_to_check.append(current_path)
        
        # Notify all watchers
        notified_agents = set()
        for p in paths_to_check:
            if p in self.watchers:
                for watcher in self.watchers[p]:
                    if watcher != agent and watcher not in notified_agents:
                        # In a real implementation, this would send a notification
                        # to the agent using the message broker
                        self.logger.debug(f"Would notify {watcher} about change to {path} by {agent}")
                        notified_agents.add(watcher)
    
    def dump(self) -> str:
        """Dump the entire context as a JSON string"""
        return json.dumps(self.context, indent=2)
    
    def load(self, json_str: str) -> None:
        """Load the context from a JSON string"""
        self.context = json.loads(json_str)
        self.logger.info("Loaded context from JSON")