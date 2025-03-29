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
