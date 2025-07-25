from typing import Dict, Any, List, Optional, Type
import logging
from dataclasses import dataclass

@dataclass
class MCPResource:
    """Represents a resource that can be accessed by agents"""
    uri: str
    data: Any
    metadata: Dict[str, Any]

@dataclass
class MCPTool:
    """Represents a tool that can be used by agents"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    handler: callable

class MCPServer:
    """Central server that manages MCP resources and tools"""
    
    def __init__(self, name: str):
        self.name = name
        self.resources: Dict[str, MCPResource] = {}
        self.tools: Dict[str, MCPTool] = {}
        self.logger = logging.getLogger(f"mcp.server.{name}")
    
    def register_resource(self, uri: str, data: Any, metadata: Dict[str, Any] = None) -> MCPResource:
        """Register a new resource with the server"""
        resource = MCPResource(uri=uri, data=data, metadata=metadata or {})
        self.resources[uri] = resource
        self.logger.info(f"Registered resource: {uri}")
        return resource
    
    def get_resource(self, uri: str) -> Optional[MCPResource]:
        """Get a resource by URI"""
        return self.resources.get(uri)
    
    def register_tool(self, name: str, description: str, 
                     input_schema: Dict[str, Any], 
                     output_schema: Dict[str, Any],
                     handler: callable) -> MCPTool:
        """Register a new tool with the server"""
        tool = MCPTool(
            name=name,
            description=description,
            input_schema=input_schema,
            output_schema=output_schema,
            handler=handler
        )
        self.tools[name] = tool
        self.logger.info(f"Registered tool: {name}")
        return tool
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with the given arguments"""
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        self.logger.info(f"Executing tool: {tool_name}")
        try:
            result = tool.handler(**arguments)
            return {"success": True, "result": result}
        except Exception as e:
            self.logger.error(f"Tool execution failed: {str(e)}")
            return {"success": False, "error": str(e)}