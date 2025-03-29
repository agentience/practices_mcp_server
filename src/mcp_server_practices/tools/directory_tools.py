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
