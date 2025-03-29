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
MCP server implementation for development practices using modern decorator pattern.
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple

# Import directly from mcp package
from mcp.server import FastMCP
from mcp.server.fastmcp.server import TextContent

from mcp_server_practices import __version__
from mcp_server_practices.tools import (
    branch_tools, 
    version_tools, 
    pr_tools, 
    git_tools, 
    license_tools, 
    github_tools,
    directory_tools  # New import
)

def setup_file_logging(
    logging_level: int,
    project_root: Optional[str] = None,
    log_file_path: Optional[str] = None
) -> Optional[logging.FileHandler]:
    """
    Set up file logging for the MCP server.
    
    Args:
        logging_level: Logging level to use for the file handler
        project_root: Optional project root path, defaults to detected project root
        log_file_path: Optional custom path for the log file, defaults to .practices/server.log
        
    Returns:
        logging.FileHandler if file logging was set up successfully, None otherwise
    """
    try:
        # Determine log file path
        if log_file_path:
            # Use provided log file path
            log_path = Path(log_file_path)
            # Create parent directories if needed
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_path = str(log_path)
            logging.info(f"Using custom log file path: {file_path}")
        else:
            # Use default path in .practices directory
            if project_root is None:
                project_root = find_project_root()
            
            practices_dir = os.path.join(project_root, ".practices")
            os.makedirs(practices_dir, exist_ok=True)
            file_path = os.path.join(practices_dir, "server.log")
            logging.info(f"Using default log file path: {file_path}")
        
        # Create file handler
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(logging_level)
        
        # Use the same format as console logging
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s %(message)s',
            datefmt='%m/%d/%y %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Add file handler to root logger
        logging.getLogger().addHandler(file_handler)
        logging.info(f"File logging enabled: {file_path}")
        
        return file_handler
    except Exception as e:
        logging.error(f"Failed to set up file logging: {e}")
        return None


def find_project_root(start_path: Optional[str] = None) -> str:
    """
    Find the project root by looking for common project markers.
    
    Args:
        start_path: Starting path for the search, defaults to current directory
        
    Returns:
        str: Path to the project root
    """
    if start_path is None:
        start_path = os.getcwd()
    
    path = Path(start_path).resolve()
    
    # Marker files that might indicate a project root
    markers = [
        '.git',
        'pyproject.toml',
        'setup.py',
        '.practices.yaml',
        '.practices.yml',
        'mcp_server_practices.code-workspace'
    ]
    
    # Start from the current directory and search upwards
    while path != path.parent:
        logging.info(f"Checking for project markers in: {path}")
        
        for marker in markers:
            if (path / marker).exists():
                logging.info(f"Found project marker '{marker}' in: {path}")
                return str(path)
        
        # Move up one directory
        path = path.parent
    
    # If no markers found, return the start path
    logging.warning(f"No project markers found, using start path: {start_path}")
    return start_path

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
        logging.info(f"System instructions file not found at: {system_instructions_path}")
        if not os.path.exists(practices_dir):
            logging.info(f"Creating .practices directory at: {practices_dir}")
            try:
                os.makedirs(practices_dir, exist_ok=True)
                logging.info(f"Successfully created .practices directory")
            except Exception as e:
                logging.error(f"Failed to create .practices directory: {e}")
        else:
            logging.info(f".practices directory already exists at: {practices_dir}")
            
        # Get default template path
        default_instructions = Path(__file__).parent / "templates" / "system_instructions.md"
        
        # Copy default if it exists
        if default_instructions.exists():
            import shutil
            logging.info(f"Copying default template from: {default_instructions}")
            try:
                shutil.copy(default_instructions, system_instructions_path)
                logging.info(f"Successfully copied template to: {system_instructions_path}")
            except Exception as e:
                logging.error(f"Failed to copy template: {e}")
        else:
            # If template doesn't exist yet, create basic instructions
            logging.info(f"Default template not found, creating basic instructions")
            try:
                with open(system_instructions_path, 'w') as f:
                    f.write("# Practices MCP Server - System Instructions\n\n"
                            "This file contains instructions for AI assistants on how to use "
                            "the development practices tools and follow established conventions.\n")
                logging.info(f"Successfully created basic instructions at: {system_instructions_path}")
            except Exception as e:
                logging.error(f"Failed to create basic instructions: {e}")
    
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
    @mcp.resource(uri="practices://instructions/system", name="Practices System Instructions")
    async def system_instructions_resource():
        """Provide system instructions from the current project."""
        from mcp_server_practices.utils.global_context import get_project_root
        project_root = get_project_root()
        
        # If working directory hasn't been set yet, return initialization instructions
        if project_root is None:
            return TextContent(
                text="""
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
"""
            )
        
        # Otherwise return the project-specific instructions
        instructions = await get_system_instructions(project_root)
        return TextContent(
            text=instructions
        )

    return mcp

# Create a main function to make it compatible with project.scripts
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Practices MCP Server')
    parser.add_argument(
        '--log-level', 
        default='ERROR',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set the logging level (default: ERROR)'
    )
    parser.add_argument(
        '--project-root',
        help='Specify the project root directory'
    )
    parser.add_argument(
        '--log-file',
        action='store_true',
        default=True,
        help='Enable logging to a file (default: enabled)'
    )
    parser.add_argument(
        '--no-log-file',
        action='store_false',
        dest='log_file',
        help='Disable logging to a file'
    )
    parser.add_argument(
        '--log-file-path',
        help='Specify a custom path for the log file (default: {project_root}/.practices/server.log)'
    )
    args = parser.parse_args()
    
    # Configure logging level
    logging_level = getattr(logging, args.log_level)
    
    # Reset root logger handlers to prevent console logging
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set up a null handler to suppress console output
    root_logger.addHandler(logging.NullHandler())
    
    # Set up a console logger just for the file path message
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(message)s', datefmt='%m/%d/%y %H:%M:%S')
    console_handler.setFormatter(formatter)
    console_logger = logging.getLogger("console_only")
    console_logger.setLevel(logging.INFO)
    console_logger.addHandler(console_handler)
    # Make sure this logger doesn't propagate to the root logger
    console_logger.propagate = False
    
    # Configure loggers with specified level
    logging.getLogger().setLevel(logging_level)
    logging.getLogger('mcp').setLevel(logging_level)
    
    # Set up file logging if enabled
    if args.log_file:
        # Get project_root from args or detect it
        project_root = args.project_root
        if project_root is None:
            project_root = find_project_root()
            
        # Set up file logging
        # Print the file path to console - this is the only console output
        if args.log_file_path:
            file_path = args.log_file_path
        else:
            practices_dir = os.path.join(project_root, ".practices")
            file_path = os.path.join(practices_dir, "server.log")
        
        console_logger.info(f"Setting up file logging to {file_path}")
        
        file_handler = setup_file_logging(
            logging_level=logging_level,
            project_root=project_root,
            log_file_path=args.log_file_path
        )
        
        if file_handler is None:
            logging.error("File logging setup failed. No logging available since console logging is disabled.")
    else:
        logging.error("File logging is disabled. No logging available since console logging is also disabled.")
    
    # Create server and set up error handling
    mcp = create_server()
    mcp.onerror = lambda error: logging.error(f"[MCP Error] {error}")
    
    # Run the server
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(mcp.run())
    except KeyboardInterrupt:
        logging.info("Server stopped")

# This allows running the server directly or importing it as a module
if __name__ == "__main__":
    main()
