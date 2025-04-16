#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2025 Agentience
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Unit tests for directory tools module.
"""
import pytest

pytest.skip("Skipping directory tools tests due to MCP package dependency issues", allow_module_level=True)

import os
import tempfile
import pytest
from pathlib import Path

from mcp_server_practices.utils.global_context import get_project_root, get_current_directory
from mcp_server_practices.tools.directory_tools import register_tools


class MockMCP:
    """Mock MCP server for testing."""
    
    def __init__(self):
        self.registered_tools = {}
        
    def tool(self, func=None):
        """Register a tool."""
        def decorator(func):
            self.registered_tools[func.__name__] = func
            return func
            
        if func is None:
            return decorator
        return decorator(func)


@pytest.fixture
def mock_mcp():
    """Create a mock MCP server."""
    return MockMCP()


@pytest.fixture
def temp_project_dir():
    """Create a temporary directory to simulate a project root."""
    temp_dir = tempfile.mkdtemp()
    # Create a marker file to identify as project root
    with open(os.path.join(temp_dir, "pyproject.toml"), "w") as f:
        f.write("# Test project")
    yield temp_dir
    # Clean up
    import shutil
    shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_set_working_directory(mock_mcp, temp_project_dir):
    """Test setting the working directory."""
    # Register tools
    register_tools(mock_mcp, {})
    
    # Tool should be registered
    assert "set_working_directory" in mock_mcp.registered_tools
    
    # Call the tool
    set_working_directory = mock_mcp.registered_tools["set_working_directory"]
    result = await set_working_directory(temp_project_dir)
    
    # Check global context was updated
    # Use Path.resolve() to normalize paths (handles /var vs /private/var on macOS)
    assert Path(get_project_root()).resolve() == Path(temp_project_dir).resolve()
    assert Path(get_current_directory()).resolve() == Path(temp_project_dir).resolve()
    
    # Check result structure
    assert result["status"] == "success"
    # Use Path.resolve() for directory and project_root comparisons too
    assert Path(result["directory"]).resolve() == Path(temp_project_dir).resolve()
    assert Path(result["project_root"]).resolve() == Path(temp_project_dir).resolve()
    assert "practices_dir" in result
    assert "log_file_path" in result
    assert result["system_instructions_loaded"] is True
    
    # Check .practices directory was created
    practices_dir = os.path.join(temp_project_dir, ".practices")
    assert os.path.exists(practices_dir)
    
    # Check system_instructions.md was created
    system_instructions_path = os.path.join(practices_dir, "system_instructions.md")
    assert os.path.exists(system_instructions_path)
