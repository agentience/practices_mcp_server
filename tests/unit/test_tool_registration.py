#!/usr/bin/env python
"""
Unit tests for MCP tool registration.
"""
import pytest

pytest.skip("Skipping tool registration tests due to MCP package dependency issues", allow_module_level=True)

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock the mcp modules
sys.modules['mcp'] = MagicMock()
sys.modules['mcp.tools'] = MagicMock()
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = MagicMock()
sys.modules['mcp.server.fastmcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp.server'].TextContent = MagicMock()

# Also mock other imported modules
sys.modules['mcp_server_practices.branch.validator'] = MagicMock()
sys.modules['mcp_server_practices.branch.creator'] = MagicMock()
sys.modules['mcp_server_practices.integrations.jira'] = MagicMock()
sys.modules['mcp_server_practices.pr.generator'] = MagicMock()
sys.modules['mcp_server_practices.pr.workflow'] = MagicMock()

# Now import the modules to test
from src.mcp_server_practices.tools import branch_tools, pr_tools


class TestToolRegistration(unittest.TestCase):
    """Test the tool registration functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_mcp = Mock()
        self.config = {
            "project_key": "PMS",
            "main_branch": "main",
            "develop_branch": "develop",
            "branching_strategy": "gitflow",
        }

    def test_branch_tools_registration_keyword_only(self):
        """Test that branch tools are registered with keyword-only arguments."""
        branch_tools.register_tools(self.mock_mcp, self.config)
        
        # Check tool decorators were called
        self.assertEqual(self.mock_mcp.tool.call_count, 3)
        
        # Get the decorated functions (technically these would be mock calls)
        decorator_calls = self.mock_mcp.tool.call_args_list
        
        for call in decorator_calls:
            # The function should be passed to the decorator when called
            func = call[0][0].__closure__[0].cell_contents
            
            # Check function signature for keyword-only arguments
            import inspect
            sig = inspect.signature(func)
            
            # There should be no positional-or-keyword parameters
            positional_params = [
                p.name for p in sig.parameters.values() 
                if p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
            ]
            self.assertEqual(len(positional_params), 0, 
                            f"Function {func.__name__} has positional parameters: {positional_params}")
            
            # All parameters should be keyword-only (except *args if present)
            for param_name, param in sig.parameters.items():
                if param_name != 'args':  # Skip *args
                    self.assertIn(
                        param.kind, 
                        [inspect.Parameter.KEYWORD_ONLY, inspect.Parameter.VAR_KEYWORD],
                        f"Parameter {param_name} in {func.__name__} is not keyword-only"
                    )

    def test_pr_tools_registration_keyword_only(self):
        """Test that PR tools are registered with keyword-only arguments."""
        pr_tools.register_tools(self.mock_mcp, self.config)
        
        # Check tool decorators were called
        self.assertEqual(self.mock_mcp.tool.call_count, 4)
        
        # Get the decorated functions
        decorator_calls = self.mock_mcp.tool.call_args_list
        
        for call in decorator_calls:
            # The function should be passed to the decorator when called
            func = call[0][0].__closure__[0].cell_contents
            
            # Check function signature for keyword-only arguments
            import inspect
            sig = inspect.signature(func)
            
            # There should be no positional-or-keyword parameters
            positional_params = [
                p.name for p in sig.parameters.values() 
                if p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
            ]
            self.assertEqual(len(positional_params), 0, 
                            f"Function {func.__name__} has positional parameters: {positional_params}")
            
            # All parameters should be keyword-only (except *args if present)
            for param_name, param in sig.parameters.items():
                if param_name != 'args':  # Skip *args
                    self.assertIn(
                        param.kind, 
                        [inspect.Parameter.KEYWORD_ONLY, inspect.Parameter.VAR_KEYWORD],
                        f"Parameter {param_name} in {func.__name__} is not keyword-only"
                    )


if __name__ == "__main__":
    unittest.main()
