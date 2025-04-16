#!/usr/bin/env python
"""
Configuration system for the Practices MCP Server.

This module provides a flexible and adaptable configuration system
for managing development practices across different project types.

Copyright (c) 2025 Agentience.ai
Author: Troy Molander
License: MIT License - See LICENSE file for details

Version: 0.2.0
"""

__all__ = ["schema", "loader", "validator", "detector", "templates"]

from . import schema
from . import loader
from . import validator
from . import detector
from . import templates

from .schema import ConfigurationSchema, ProjectConfig
from .loader import load_config, save_config
from .validator import validate_config
from .detector import detect_project_type, get_default_config
