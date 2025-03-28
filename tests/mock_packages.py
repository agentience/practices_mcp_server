"""
Mock package implementations for use in testing.
"""
import sys
from unittest.mock import MagicMock

# Create a mock for the mcp tools module
mock_call_tool = MagicMock()

# Create the mcp module
mcp_module = MagicMock()
sys.modules['mcp'] = mcp_module

# Create the mcp.tools module
tools_module = MagicMock()
tools_module.call_tool = mock_call_tool
sys.modules['mcp.tools'] = tools_module

# Update the mcp module to include the tools module
mcp_module.tools = tools_module
