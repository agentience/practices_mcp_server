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
    directory_tools,
    config_tools
)

# Import utility functions from directory_utils
from mcp_server_practices.utils.directory_utils import (
    find_project_root,
    setup_file_logging,
    get_system_instructions
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
    directory_tools.register_tools(mcp, config)  # Register directory tools
    config_tools.register_tools(mcp, config)     # Register configuration tools
    
    # Register system instructions resource
    @mcp.resource(uri="practices://instructions/system", name="Practices System Instructions")
    async def system_instructions_resource():
        """Provide system instructions from the current project."""
        from mcp_server_practices.utils.global_context import get_project_root
        project_root = get_project_root()
        
        # If working directory hasn't been set yet, return initialization instructions
        if project_root is None:
            return TextContent(
                type="text",
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
            type="text",
            text="Load instructions from .practices/system_instructions.md"
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
