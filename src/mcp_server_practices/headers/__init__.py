#!/usr/bin/env python
"""
headers - License header management for the Practices MCP Server.

Copyright (c) 2025 Agentience.ai
Author: Troy Molander
License: MIT License - See LICENSE file for details

Version: 0.1.0
"""

from .manager import add_license_header, verify_license_header
from .templates import get_header_template

__all__ = ["add_license_header", "verify_license_header", "get_header_template"]
