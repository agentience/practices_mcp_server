#!/usr/bin/env python
"""
Version validation functionality for the Practices MCP Server.

Copyright (c) 2025 Agentience.ai
Author: Troy Molander
License: MIT License - See LICENSE file for details

Version: 0.1.0
"""

import os
import re
from typing import Dict, List, Optional, Any, Pattern


class VersionValidator:
    """Validates version consistency across different files in a project."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the version validator with configuration.

        Args:
            config: Configuration dictionary containing version pattern settings
        """
        self.config = config
        self.version_files = self._get_version_files()
        self.expected_version = None
        
    def _get_version_files(self) -> List[Dict[str, Any]]:
        """
        Get version files configuration from the config.

        Returns:
            List of version file configurations
        """
        # Get version files from config or use default
        version_files = self.config.get("version", {}).get("files", [])
        
        # If no version files are configured, use default
        if not version_files:
            # Default: Check for version in __init__.py and pyproject.toml
            version_files = [
                {
                    "path": "src/mcp_server_practices/__init__.py",
                    "pattern": r'__version__\s*=\s*"(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?)"'
                },
                {
                    "path": "pyproject.toml",
                    "pattern": r'version\s*=\s*"(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?)"'
                }
            ]
            
        return version_files

    def validate(self) -> Dict[str, Any]:
        """
        Validate version consistency across configured files.

        Returns:
            Dictionary with validation results
        """
        # Collect versions from all configured files
        versions = []
        file_results = []
        
        for file_config in self.version_files:
            path = file_config.get("path", "")
            pattern = file_config.get("pattern", "")
            
            if not path or not pattern:
                file_results.append({
                    "path": path,
                    "valid": False,
                    "error": "Missing path or pattern in configuration"
                })
                continue
                
            # Check if file exists
            if not os.path.exists(path):
                file_results.append({
                    "path": path,
                    "valid": False,
                    "error": f"File not found: {path}"
                })
                continue
                
            # Extract version from file
            try:
                with open(path, "r") as f:
                    content = f.read()
                    
                match = re.search(pattern, content)
                if match:
                    version = match.group(1)
                    versions.append(version)
                    file_results.append({
                        "path": path,
                        "valid": True,
                        "version": version
                    })
                else:
                    file_results.append({
                        "path": path,
                        "valid": False,
                        "error": f"Version pattern not found in {path}"
                    })
            except Exception as e:
                file_results.append({
                    "path": path,
                    "valid": False,
                    "error": f"Error reading {path}: {str(e)}"
                })
                
        # Check if all versions are consistent
        if not versions:
            return {
                "valid": False,
                "error": "No version information found",
                "file_results": file_results
            }
            
        # Store the first version as expected
        self.expected_version = versions[0]
        
        # Check if all versions match the expected version
        consistent = all(version == self.expected_version for version in versions)
        
        if consistent:
            return {
                "valid": True,
                "version": self.expected_version,
                "file_results": file_results
            }
        else:
            return {
                "valid": False,
                "error": "Inconsistent versions found",
                "expected_version": self.expected_version,
                "versions": versions,
                "file_results": file_results
            }
            
    def is_valid_version(self, version: str) -> bool:
        """
        Check if a version string follows semantic versioning.

        Args:
            version: Version string to validate

        Returns:
            True if valid semver, False otherwise
        """
        # Semver pattern: MAJOR.MINOR.PATCH[-PRE_RELEASE][+BUILD]
        semver_pattern = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
        return bool(re.match(semver_pattern, version))
            
    def get_current_version(self) -> Optional[str]:
        """
        Get the current version of the project.

        Returns:
            Current version or None if not found
        """
        # Validate first to populate expected_version
        if self.expected_version is None:
            result = self.validate()
            if not result["valid"]:
                return None
                
        return self.expected_version


def validate_version(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Validate version consistency across files.

    Args:
        config: Optional configuration dictionary

    Returns:
        Dictionary with validation results
    """
    if config is None:
        config = {}
    
    validator = VersionValidator(config)
    return validator.validate()


def get_current_version(config: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Get the current version of the project.

    Args:
        config: Optional configuration dictionary

    Returns:
        Current version or None if not found
    """
    if config is None:
        config = {}
    
    validator = VersionValidator(config)
    return validator.get_current_version()
