from typing import Dict, Any, List, Optional, Callable
import logging
import threading
import time
import queue

from .message_broker import MessageBroker
from .errors import AgentError, AgentTimeoutError, AgentExecutionError

class AgentMonitor:
    """Monitor for agent health and recovery"""
    
    def __init__(self, message_broker: MessageBroker, agent_factory):
        self.message_broker = message_broker
        self.agent_factory = agent_factory
        self.logger = logging.getLogger("mcp.agent_monitor")
        self.agent_status: Dict[str, Dict[str, Any]] = {}
        self.running = False
        self.thread = None
        self.check_interval = 10  # seconds
    
    def start(self):
        """Start the agent monitor"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitoring_loop)
        self.thread.daemon = True
        self.thread.start()
        self.logger.info("Agent monitor started")
    
    def stop(self):
        """Stop the agent monitor"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
        self.logger.info("Agent monitor stopped")
    
    def register_agent(self, agent_name: str, agent_type: str):
        """Register an agent for monitoring"""
        self.agent_status[agent_name] = {
            "type": agent_type,
            "status": "registered",
            "last_heartbeat": time.time(),
            "error_count": 0,
            "last_error": None
        }
        
        # Subscribe to heartbeat messages
        self.message_broker.subscribe(
            f"monitor.heartbeat.{agent_name}",
            lambda message: self._handle_heartbeat(agent_name, message)
        )
        
        self.logger.info(f"Registered agent for monitoring: {agent_name}")
    
    def unregister_agent(self, agent_name: str):
        """Unregister an agent from monitoring"""
        if agent_name in self.agent_status:
            del self.agent_status[agent_name]
            
            # Unsubscribe from heartbeat messages
            self.message_broker.unsubscribe(
                f"monitor.heartbeat.{agent_name}",
                lambda message: self._handle_heartbeat(agent_name, message)
            )
            
            self.logger.info(f"Unregistered agent from monitoring: {agent_name}")
    
    def update_agent_status(self, agent_name: str, status: str, error: Optional[Exception] = None):
        """Update the status of an agent"""
        if agent_name not in self.agent_status:
            self.logger.warning(f"Attempted to update status for unknown agent: {agent_name}")
            return
        
        self.agent_status[agent_name]["status"] = status
        
        if status == "error" and error:
            self.agent_status[agent_name]["last_error"] = str(error)
            self.agent_status[agent_name]["error_count"] += 1
        
        self.logger.debug(f"Updated agent status: {agent_name} -> {status}")
    
    def _handle_heartbeat(self, agent_name: str, message):
        """Handle a heartbeat message from an agent"""
        if agent_name in self.agent_status:
            self.agent_status[agent_name]["last_heartbeat"] = time.time()
            self.agent_status[agent_name]["status"] = "active"
    
    def _monitoring_loop(self):
        """Background thread for monitoring agents"""
        while self.running:
            try:
                # Check all agents
                current_time = time.time()
                
                for agent_name, status in self.agent_status.items():
                    # Check if the agent is still alive
                    if status["status"] != "error" and current_time - status["last_heartbeat"] > 30:
                        self.logger.warning(f"Agent {agent_name} has not sent a heartbeat in 30 seconds")
                        
                        # Mark as potentially dead
                        status["status"] = "unresponsive"
                        
                        # Try to ping the agent
                        try:
                            self.message_broker.publish(
                                sender="agent_monitor",
                                recipient=agent_name,
                                message_type="ping",
                                content={"timestamp": current_time}
                            )
                        except Exception as e:
                            self.logger.error(f"Failed to ping agent {agent_name}: {str(e)}")
                    
                    # Check if unresponsive agents need recovery
                    if status["status"] == "unresponsive" and current_time - status["last_heartbeat"] > 60:
                        self.logger.error(f"Agent {agent_name} is unresponsive, attempting recovery")
                        
                        # Attempt to recover the agent
                        self._recover_agent(agent_name, status["type"])
                
                # Sleep for the check interval
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(1)  # Sleep briefly to avoid tight loop on error
    
    def _recover_agent(self, agent_name: str, agent_type: str):
        """Attempt to recover a failed agent"""
        try:
            # Get the existing agent
            existing_agent = self.agent_factory.get_agent(agent_name)
            
            # Create a new agent of the same type
            new_agent = self.agent_factory.create_agent(agent_type)
            
            # Replace the old agent
            self.agent_factory.agents[agent_name] = new_agent
            
            # Clean up the old agent
            existing_agent.cleanup()
            
            # Update status
            self.agent_status[agent_name]["status"] = "recovered"
            self.agent_status[agent_name]["last_heartbeat"] = time.time()
            
            self.logger.info(f"Successfully recovered agent {agent_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to recover agent {agent_name}: {str(e)}")
            self.agent_status[agent_name]["status"] = "error"
            self.agent_status[agent_name]["last_error"] = str(e)
            self.agent_status[agent_name]["error_count"] += 1