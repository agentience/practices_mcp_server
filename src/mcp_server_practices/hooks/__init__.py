#!/usr/bin/env python
"""
hooks - Pre-commit hooks management for the Practices MCP Server.

Copyright (c) 2025 Agentience.ai
Author: Troy Molander
License: MIT License - See LICENSE file for details

Version: 0.1.0
"""

from .installer import install_hooks, check_git_repo_init, update_hooks
from .templates import get_default_config

__all__ = ["install_hooks", "check_git_repo_init", "update_hooks", "get_default_config"]
