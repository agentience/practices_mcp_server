#!/usr/bin/env python
"""
Tests for the version management functionality.

Copyright (c) 2025 Agentience.ai
Author: Troy Molander
License: MIT License - See LICENSE file for details

Version: 0.1.0
"""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from mcp_server_practices.version.validator import validate_version, get_current_version, VersionValidator
from mcp_server_practices.version.bumper import bump_version, VersionBumper


class TestVersionValidator(unittest.TestCase):
    """Test the version validator functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary version files for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create a mock __init__.py file
        self.init_path = os.path.join(self.temp_dir.name, "__init__.py")
        with open(self.init_path, "w") as f:
            f.write('"""Version module."""\n\n__version__ = "0.1.0"\n')
        
        # Create a mock pyproject.toml file
        self.pyproject_path = os.path.join(self.temp_dir.name, "pyproject.toml")
        with open(self.pyproject_path, "w") as f:
            f.write('[project]\nname = "test-project"\nversion = "0.1.0"\n')
        
        # Set up configuration for testing
        self.config = {
            "version": {
                "files": [
                    {
                        "path": self.init_path,
                        "pattern": r'__version__\s*=\s*"(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?)"'
                    },
                    {
                        "path": self.pyproject_path,
                        "pattern": r'version\s*=\s*"(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?)"'
                    }
                ]
            }
        }
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def test_validate_matching_versions(self):
        """Test validation with matching versions."""
        result = validate_version(self.config)
        self.assertTrue(result["valid"])
        self.assertEqual(result["version"], "0.1.0")
    
    def test_validate_mismatched_versions(self):
        """Test validation with mismatched versions."""
        # Modify one of the files to have a different version
        with open(self.init_path, "w") as f:
            f.write('"""Version module."""\n\n__version__ = "0.2.0"\n')
        
        result = validate_version(self.config)
        self.assertFalse(result["valid"])
        self.assertEqual(result["error"], "Inconsistent versions found")
        self.assertEqual(result["expected_version"], "0.2.0")
        self.assertEqual(result["versions"], ["0.2.0", "0.1.0"])
    
    def test_get_current_version(self):
        """Test getting the current version."""
        version = get_current_version(self.config)
        self.assertEqual(version, "0.1.0")
    
    def test_invalid_version_path(self):
        """Test validation with invalid file path."""
        invalid_config = {
            "version": {
                "files": [
                    {
                        "path": os.path.join(self.temp_dir.name, "nonexistent.py"),
                        "pattern": r'__version__\s*=\s*"(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?)"'
                    }
                ]
            }
        }
        
        result = validate_version(invalid_config)
        self.assertFalse(result["valid"])
        self.assertEqual(result["error"], "No version information found")
    
    def test_is_valid_version(self):
        """Test version format validation."""
        validator = VersionValidator(self.config)
        
        # Valid versions
        self.assertTrue(validator.is_valid_version("1.0.0"))
        self.assertTrue(validator.is_valid_version("0.1.0"))
        self.assertTrue(validator.is_valid_version("2.3.4"))
        self.assertTrue(validator.is_valid_version("1.0.0-alpha"))
        self.assertTrue(validator.is_valid_version("1.0.0-alpha.1"))
        self.assertTrue(validator.is_valid_version("1.0.0+build.1"))
        self.assertTrue(validator.is_valid_version("1.0.0-beta+build.1"))
        
        # Invalid versions
        self.assertFalse(validator.is_valid_version("1"))
        self.assertFalse(validator.is_valid_version("1.0"))
        self.assertFalse(validator.is_valid_version("v1.0.0"))
        self.assertFalse(validator.is_valid_version("version 1.0.0"))
        self.assertFalse(validator.is_valid_version("1.0.0.0"))


class TestVersionBumper(unittest.TestCase):
    """Test the version bumper functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary version files for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create a mock __init__.py file
        self.init_path = os.path.join(self.temp_dir.name, "__init__.py")
        with open(self.init_path, "w") as f:
            f.write('"""Version module."""\n\n__version__ = "0.1.0"\n')
        
        # Create a mock pyproject.toml file
        self.pyproject_path = os.path.join(self.temp_dir.name, "pyproject.toml")
        with open(self.pyproject_path, "w") as f:
            f.write('[project]\nname = "test-project"\nversion = "0.1.0"\n')
        
        # Set up configuration for testing
        self.config = {
            "version": {
                "files": [
                    {
                        "path": self.init_path,
                        "pattern": r'__version__\s*=\s*"(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?)"'
                    },
                    {
                        "path": self.pyproject_path,
                        "pattern": r'version\s*=\s*"(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?)"'
                    }
                ]
            }
        }
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def test_bump_patch_version(self):
        """Test bumping the patch version."""
        result = bump_version("patch", self.config)
        self.assertTrue(result["success"])
        self.assertEqual(result["previous_version"], "0.1.0")
        self.assertEqual(result["new_version"], "0.1.1")
        
        # Verify files were updated
        with open(self.init_path, "r") as f:
            content = f.read()
            self.assertIn('__version__ = "0.1.1"', content)
        
        with open(self.pyproject_path, "r") as f:
            content = f.read()
            self.assertIn('version = "0.1.1"', content)
    
    def test_bump_minor_version(self):
        """Test bumping the minor version."""
        result = bump_version("minor", self.config)
        self.assertTrue(result["success"])
        self.assertEqual(result["previous_version"], "0.1.0")
        self.assertEqual(result["new_version"], "0.2.0")
        
        # Verify files were updated
        with open(self.init_path, "r") as f:
            content = f.read()
            self.assertIn('__version__ = "0.2.0"', content)
    
    def test_bump_major_version(self):
        """Test bumping the major version."""
        result = bump_version("major", self.config)
        self.assertTrue(result["success"])
        self.assertEqual(result["previous_version"], "0.1.0")
        self.assertEqual(result["new_version"], "1.0.0")
        
        # Verify files were updated
        with open(self.init_path, "r") as f:
            content = f.read()
            self.assertIn('__version__ = "1.0.0"', content)
    
    def test_bump_prerelease(self):
        """Test bumping the prerelease."""
        # First create a prerelease version
        with open(self.init_path, "w") as f:
            f.write('"""Version module."""\n\n__version__ = "0.1.0-1"\n')
        
        with open(self.pyproject_path, "w") as f:
            f.write('[project]\nname = "test-project"\nversion = "0.1.0-1"\n')
        
        result = bump_version("prerelease", self.config)
        self.assertTrue(result["success"])
        self.assertEqual(result["previous_version"], "0.1.0-1")
        self.assertEqual(result["new_version"], "0.1.0-2")
    
    def test_invalid_part(self):
        """Test with an invalid version part."""
        result = bump_version("invalid", self.config)
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Invalid version part: invalid. Must be one of: major, minor, patch, prerelease")
    
    @patch('subprocess.run')
    def test_bump_with_bumpversion(self, mock_run):
        """Test bumping version with bump2version tool."""
        # Configure to use bumpversion
        config = self.config.copy()
        config["version"]["use_bumpversion"] = True
        
        # Mock subprocess.run to simulate successful bump2version execution
        mock_run.return_value = MagicMock(stdout="", stderr="")
        
        # Mock validate_version to return the expected new version
        with patch('mcp_server_practices.version.bumper.validate_version') as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "version": "0.1.1"
            }
            
            result = bump_version("patch", config)
            self.assertTrue(result["success"])
            self.assertEqual(result["new_version"], "0.1.1")
            
            # Verify bump2version was called with correct arguments
            mock_run.assert_called_once()
            args, kwargs = mock_run.call_args
            self.assertEqual(args[0], ["bump2version", "patch"])


if __name__ == "__main__":
    unittest.main()
