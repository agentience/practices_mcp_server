#!/usr/bin/env python
"""
Version bumping functionality for the Practices MCP Server.

Copyright (c) 2025 Agentience.ai
Author: Troy Molander
License: MIT License - See LICENSE file for details

Version: 0.1.0
"""

import os
import re
import subprocess
from typing import Dict, List, Optional, Any, Tuple

from mcp_server_practices.version.validator import get_current_version, validate_version


class VersionBumper:
    """Bumps version numbers in files according to semantic versioning."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the version bumper with configuration.

        Args:
            config: Configuration dictionary containing version settings
        """
        self.config = config
        self.use_bumpversion = self.config.get("version", {}).get("use_bumpversion", False)
        self.current_version = get_current_version(config)
        
    def bump_version(self, part: str) -> Dict[str, Any]:
        """
        Bump the version according to semantic versioning.

        Args:
            part: Part of the version to bump ('major', 'minor', 'patch', 'prerelease')

        Returns:
            Dictionary with bumping results
        """
        if not self.current_version:
            return {
                "success": False,
                "error": "No current version found"
            }
        
        # Check if we should use bumpversion tool
        if self.use_bumpversion:
            return self._bump_with_bumpversion(part)
        else:
            return self._bump_manually(part)
    
    def _bump_with_bumpversion(self, part: str) -> Dict[str, Any]:
        """
        Bump version using bump2version tool.

        Args:
            part: Part of the version to bump ('major', 'minor', 'patch', 'prerelease')

        Returns:
            Dictionary with bumping results
        """
        if part not in ['major', 'minor', 'patch', 'prerelease']:
            return {
                "success": False,
                "error": f"Invalid version part: {part}. Must be one of: major, minor, patch, prerelease"
            }
        
        try:
            # Run bump2version command
            cmd = ["bump2version", part]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Get the new version
            validation = validate_version(self.config)
            if validation["valid"]:
                new_version = validation["version"]
                
                return {
                    "success": True,
                    "previous_version": self.current_version,
                    "new_version": new_version,
                    "part": part,
                    "message": f"Bumped {part} version: {self.current_version} → {new_version}"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to get new version after bumping"
                }
                
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Error running bump2version: {e.stderr}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error bumping version: {str(e)}"
            }
    
    def _bump_manually(self, part: str) -> Dict[str, Any]:
        """
        Bump version by directly modifying files.

        Args:
            part: Part of the version to bump ('major', 'minor', 'patch', 'prerelease')

        Returns:
            Dictionary with bumping results
        """
        if part not in ['major', 'minor', 'patch', 'prerelease']:
            return {
                "success": False,
                "error": f"Invalid version part: {part}. Must be one of: major, minor, patch, prerelease"
            }
        
        try:
            # Parse current version
            version_parts = self._parse_version(self.current_version)
            if not version_parts:
                return {
                    "success": False,
                    "error": f"Could not parse version: {self.current_version}"
                }
            
            # Bump the requested part
            major, minor, patch, prerelease = version_parts
            
            if part == 'major':
                major += 1
                minor = 0
                patch = 0
                prerelease = None
            elif part == 'minor':
                minor += 1
                patch = 0
                prerelease = None
            elif part == 'patch':
                patch += 1
                prerelease = None
            elif part == 'prerelease':
                if prerelease is None:
                    prerelease = 1
                else:
                    prerelease += 1
            
            # Construct new version string
            new_version = f"{major}.{minor}.{patch}"
            if prerelease is not None:
                new_version += f"-{prerelease}"
            
            # Update files
            updated_files = self._update_version_in_files(new_version)
            
            # Validate after updating
            validation = validate_version(self.config)
            if validation["valid"] and validation["version"] == new_version:
                return {
                    "success": True,
                    "previous_version": self.current_version,
                    "new_version": new_version,
                    "part": part,
                    "updated_files": updated_files,
                    "message": f"Bumped {part} version: {self.current_version} → {new_version}"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to validate version after update",
                    "validation_result": validation
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error bumping version: {str(e)}"
            }
    
    def _parse_version(self, version: str) -> Optional[Tuple[int, int, int, Optional[int]]]:
        """
        Parse a version string into its components.

        Args:
            version: Version string to parse

        Returns:
            Tuple of (major, minor, patch, prerelease) or None if invalid
        """
        # Basic semver pattern: MAJOR.MINOR.PATCH[-PRERELEASE]
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:-(\d+))?", version)
        if match:
            major = int(match.group(1))
            minor = int(match.group(2))
            patch = int(match.group(3))
            prerelease = int(match.group(4)) if match.group(4) else None
            return (major, minor, patch, prerelease)
        return None
    
    def _update_version_in_files(self, new_version: str) -> List[Dict[str, Any]]:
        """
        Update version in all configured files.

        Args:
            new_version: New version string

        Returns:
            List of results for each file update
        """
        results = []
        
        # Get version files from config
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
        
        # Update each file
        for file_config in version_files:
            path = file_config.get("path", "")
            pattern = file_config.get("pattern", "")
            
            if not path or not pattern:
                results.append({
                    "path": path,
                    "success": False,
                    "error": "Missing path or pattern in configuration"
                })
                continue
            
            # Check if file exists
            if not os.path.exists(path):
                results.append({
                    "path": path,
                    "success": False,
                    "error": f"File not found: {path}"
                })
                continue
            
            try:
                # Read file content
                with open(path, "r") as f:
                    content = f.read()
                
                # Replace version
                new_content = re.sub(
                    pattern,
                    lambda m: m.group(0).replace(m.group(1), new_version),
                    content
                )
                
                # Check if content changed
                if new_content == content:
                    results.append({
                        "path": path,
                        "success": False,
                        "error": f"Pattern found but version not updated in {path}"
                    })
                    continue
                
                # Write updated content
                with open(path, "w") as f:
                    f.write(new_content)
                
                results.append({
                    "path": path,
                    "success": True,
                    "message": f"Updated version in {path}: {self.current_version} → {new_version}"
                })
                
            except Exception as e:
                results.append({
                    "path": path,
                    "success": False,
                    "error": f"Error updating {path}: {str(e)}"
                })
        
        return results


def bump_version(part: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Bump the version according to semantic versioning.

    Args:
        part: Part of the version to bump ('major', 'minor', 'patch', 'prerelease')
        config: Optional configuration dictionary

    Returns:
        Dictionary with bumping results
    """
    if config is None:
        config = {}
    
    bumper = VersionBumper(config)
    return bumper.bump_version(part)
