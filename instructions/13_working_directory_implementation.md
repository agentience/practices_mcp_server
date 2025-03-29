# Working Directory & Dynamic System Instructions Implementation Plan

## Overview

This document outlines the implementation plan for adding working directory awareness to the practices MCP server, which will:

1. Add a `set_working_directory` tool to configure logging and load project settings
2. Use a global context to track the current project root
3. Update the `practices://instructions/system` resource to provide initialization instructions or project-specific instructions
4. Ensure system instructions are stored in the project's `.practices` directory

## Implementation Steps

### 1. Create Global Context Module

First, create a new module to maintain global context across the MCP server:

**File: `src/mcp_server_practices/utils/global_context.py`**
```python
"""Global context for the MCP server."""

# Global variables for tracking state
_current_project_root = None
_current_directory = None

def get_project_root():
    """Get the current project root."""
    return _current_project_root

def set_project_root(project_root):
    """Set the current project root."""
    global _current_project_root
    _current_project_root = project_root

def get_current_directory():
    """Get the current working directory."""
    return _current_directory

def set_current_directory(directory):
    """Set the current working directory."""
    global _current_directory
    _current_directory = directory
```

### 2. Create Directory Tool Module

**File: `src/mcp_server_practices/tools/directory_tools.py`**
```python
"""Tools for working with directories and project settings."""

import os
import logging
from pathlib import Path
from typing import Dict, Any

from mcp_server_practices.mcp_server import find_project_root, setup_file_logging, get_system_instructions
from mcp_server_practices.utils.global_context import set_project_root, set_current_directory

def register_tools(mcp, config):
    """Register directory tools with the MCP server."""
    
    @mcp.tool
    async def set_working_directory(directory_path: str) -> Dict[str, Any]:
        """
        Set the current working directory for practices tools.
        
        This tool:
        1. Configures file logging in the .practices directory
        2. Ensures system_instructions.md exists (creates from template if needed)
        3. Returns configuration information for the project
        
        Args:
            directory_path: Path to set as the current working directory
            
        Returns:
            Dict with configuration info
        """
        # Validate directory exists
        if not os.path.isdir(directory_path):
            raise ValueError(f"Directory does not exist: {directory_path}")
        
        # Find project root from this directory
        project_root = find_project_root(directory_path)
        
        # Update global context
        set_current_directory(directory_path)
        set_project_root(project_root)
        
        # Set up file logging in .practices directory
        practices_dir = os.path.join(project_root, ".practices")
        os.makedirs(practices_dir, exist_ok=True)
        log_file_path = os.path.join(practices_dir, "server.log")
        
        file_handler = setup_file_logging(
            logging_level=logging.INFO,
            project_root=project_root
        )
        
        # Ensure system_instructions.md exists
        instructions = await get_system_instructions(project_root)
        system_instructions_path = os.path.join(practices_dir, "system_instructions.md")
        
        logging.info(f"Set working directory: {directory_path}")
        logging.info(f"Project root: {project_root}")
        logging.info(f"Practices directory: {practices_dir}")
        
        # Return configuration info
        return {
            "status": "success",
            "directory": directory_path,
            "project_root": project_root,
            "practices_dir": practices_dir,
            "log_file_path": log_file_path,
            "system_instructions_loaded": True,
            "system_instructions_path": system_instructions_path
        }
```

### 3. Update System Instructions Resource in MCP Server

**File: `src/mcp_server_practices/mcp_server.py`**

Update the resource registration to use the global context and provide initialization instructions:

```python
from mcp_server_practices.utils.global_context import get_project_root

# ... existing code ...

@mcp.resource(uri="practices://instructions/system", name="Practices System Instructions")
async def system_instructions_resource():
    """Provide system instructions from the current project."""
    project_root = get_project_root()
    
    # If working directory hasn't been set yet, return initialization instructions
    if project_root is None:
        return TextContent(
            content="""
# Practices MCP Server - INITIALIZATION REQUIRED

⚠️ **IMPORTANT: Before using any practices tools, you must set the working directory.**

As the first action when working with a user, you must call:

```python
call_tool("practices", "set_working_directory", {
    "directory_path": "/path/to/current/working/directory"  # Use the current working directory from environment details
})
```

For example:
```python
# Example based on environment details
call_tool("practices", "set_working_directory", {
    "directory_path": os.getcwd()  # or the specific directory shown in environment details
})
```

Only after setting the working directory will you have access to:
- Project-specific system instructions
- Proper logging configuration
- Project context awareness

The working directory should be available in your environment details or can be obtained from the user.
""",
            mime_type="text/markdown"
        )
    
    # Otherwise return the project-specific instructions
    instructions = await get_system_instructions(project_root)
    return TextContent(content=instructions, mime_type="text/markdown")
```

### 4. Update the Create Server Function to Register Directory Tools

**File: `src/mcp_server_practices/mcp_server.py`**

```python
from mcp_server_practices.tools import (
    branch_tools, 
    version_tools, 
    pr_tools, 
    git_tools, 
    license_tools, 
    github_tools,
    directory_tools  # New import
)

def create_server():
    """
    Create and configure the MCP server.
    
    Returns:
        FastMCP: Configured MCP server instance
    """
    # Initialize FastMCP with decorator pattern
    mcp = FastMCP(
        name="practices",
        description="Development practices tools and resources",
        version=__version__,
    )

    # Default configuration
    config = {
        "workflow_mode": "solo",  # "solo" or "team"
        "main_branch": "main",
        "develop_branch": "develop",
        "branching_strategy": "gitflow",
    }

    # Register tools from modules
    branch_tools.register_tools(mcp, config)
    version_tools.register_tools(mcp, config)
    pr_tools.register_tools(mcp, config)
    git_tools.register_tools(mcp, config)
    license_tools.register_tools(mcp, config)
    github_tools.register_tools(mcp, config)
    directory_tools.register_tools(mcp, config)  # Register new directory tools
    
    # Register system instructions resource
    # (system_instructions_resource function defined as shown above)
    
    return mcp
```

### 5. Update the Get System Instructions Function

**File: `src/mcp_server_practices/mcp_server.py`**

Ensure the `get_system_instructions` function is properly handling project roots:

```python
async def get_system_instructions(project_root=None) -> str:
    """
    Get system instructions from .practices/system_instructions.md
    Falls back to default instructions if not found.
    
    Args:
        project_root: Optional project root path, defaults to detected project root
        
    Returns:
        str: System instructions content
    """
    # Determine project root if not provided
    if project_root is None:
        from mcp_server_practices.utils.global_context import get_project_root
        project_root = get_project_root()
        
        if project_root is None:
            # If still None, default to current directory
            cwd = os.getcwd()
            project_root = find_project_root(cwd)
            logging.info(f"No project root set, defaulting to detected root from current directory: {project_root}")
        else:
            logging.info(f"Using project root from global context: {project_root}")
    else:
        logging.info(f"Using provided project root: {project_root}")
    
    # Define paths
    practices_dir = os.path.join(project_root, ".practices")
    system_instructions_path = os.path.join(practices_dir, "system_instructions.md")
    
    # Create directory and copy default if needed
    if not os.path.exists(system_instructions_path):
        # ... existing code for creating/copying template ...
    
    # Load and return instructions
    try:
        with open(system_instructions_path, 'r') as f:
            content = f.read()
            logging.info(f"Successfully read system instructions ({len(content)} bytes)")
            return content
    except Exception as e:
        error_msg = f"Warning: Could not read system instructions: {e}"
        logging.error(error_msg)
        return "# Practices MCP Server\n\nError loading system instructions."
```

### 6. Create a Unit Test for the Directory Tools

**File: `tests/unit/test_directory_tools.py`**
```python
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
Tests for directory tools functionality.
"""

import os
import tempfile
import pytest
from pathlib import Path

import pytest_asyncio

from mcp_server_practices.utils.global_context import get_project_root, get_current_directory
from mcp_server_practices.tools.directory_tools import register_tools


class MockMCP:
    """Mock MCP server for testing."""
    
    def __init__(self):
        self.registered_tools = {}
        
    def tool(self, func):
        """Register a tool."""
        self.registered_tools[func.__name__] = func
        return func


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
    assert get_project_root() == temp_project_dir
    assert get_current_directory() == temp_project_dir
    
    # Check result structure
    assert result["status"] == "success"
    assert result["directory"] == temp_project_dir
    assert result["project_root"] == temp_project_dir
    assert "practices_dir" in result
    assert "log_file_path" in result
    assert result["system_instructions_loaded"] is True
    
    # Check .practices directory was created
    practices_dir = os.path.join(temp_project_dir, ".practices")
    assert os.path.exists(practices_dir)
    
    # Check system_instructions.md was created
    system_instructions_path = os.path.join(practices_dir, "system_instructions.md")
    assert os.path.exists(system_instructions_path)
```

## Execution Plan

1. Create the global context module
2. Implement the directory tools module 
3. Update the MCP server to use the global context and register the new tools
4. Modify the system instructions resource to provide initialization instructions
5. Write tests for the new functionality

Once implemented, the LLM will:
1. Initially see instructions to call `set_working_directory` with the current directory
2. After calling the tool, get project-specific instructions from `.practices/system_instructions.md`
3. Have proper logging and context for all subsequent operations
