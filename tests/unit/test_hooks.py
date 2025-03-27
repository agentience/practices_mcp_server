#!/usr/bin/env python
"""
Tests for pre-commit hooks functionality.

Copyright (c) 2025 Agentience.ai
Author: Troy Molander
License: MIT License - See LICENSE file for details

Version: 0.1.0
"""

import os
import sys
import tempfile
import time
import unittest
from unittest import mock

import pytest

# Add src directory to path to allow imports to work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from mcp_server_practices.hooks.installer import check_git_repo_init, install_hooks, update_hooks
from mcp_server_practices.hooks.templates import get_default_config


class TestHooksInstaller:
    """Tests for the hooks installer module."""

    def test_get_default_config(self):
        """Test that default configuration is generated correctly."""
        # Test default config
        default_config = get_default_config()
        assert "pre-commit" in default_config
        assert "hooks" in default_config
        assert "license-headers" in default_config

        # Test Python-specific config
        python_config = get_default_config({"project_type": "python"})
        assert "black" in python_config
        assert "ruff" in python_config
        assert "mypy" in python_config

        # Test JavaScript config
        js_config = get_default_config({"project_type": "javascript"})
        assert "eslint" in js_config
        assert "prettier" in js_config

    @mock.patch("os.path.isdir")
    def test_check_git_repo_init_not_a_repo(self, mock_isdir):
        """Test checking a non-git repository."""
        mock_isdir.return_value = False

        result = check_git_repo_init("/path/to/repo")
        
        assert result["success"] is False
        assert result["initialized"] is False
        assert "Not a Git repository" in result["error"]

    @mock.patch("os.path.isdir")
    @mock.patch("os.path.getctime")
    @mock.patch("time.time")
    @mock.patch("subprocess.run")
    def test_check_git_repo_init_newly_initialized(self, mock_run, mock_time, mock_getctime, mock_isdir):
        """Test checking a newly initialized git repository."""
        mock_isdir.return_value = True
        mock_getctime.return_value = 1000  # Git dir creation time
        mock_time.return_value = 1100  # Current time (less than 5 minutes later)
        
        # Mock subprocess.run result for getting default branch
        mock_process = mock.Mock()
        mock_process.returncode = 0
        mock_process.stdout = "main\n"
        mock_run.return_value = mock_process

        result = check_git_repo_init("/path/to/repo")
        
        assert result["success"] is True
        assert result["initialized"] is True
        assert result["is_newly_initialized"] is True
        assert result["default_branch"] == "main"

    @mock.patch("os.path.isdir")
    @mock.patch("os.path.getctime")
    @mock.patch("time.time")
    @mock.patch("subprocess.run")
    def test_check_git_repo_init_existing_repo(self, mock_run, mock_time, mock_getctime, mock_isdir):
        """Test checking an existing git repository."""
        mock_isdir.return_value = True
        mock_getctime.return_value = 1000  # Git dir creation time
        mock_time.return_value = 1500  # Current time (more than 5 minutes later)
        
        # Mock subprocess.run result for getting default branch
        mock_process = mock.Mock()
        mock_process.returncode = 0
        mock_process.stdout = "main\n"
        mock_run.return_value = mock_process

        result = check_git_repo_init("/path/to/repo")
        
        assert result["success"] is True
        assert result["initialized"] is True
        assert result["is_newly_initialized"] is False
        assert result["default_branch"] == "main"

    @mock.patch("mcp_server_practices.hooks.installer.check_git_repo_init")
    @mock.patch("subprocess.run")
    @mock.patch("os.path.exists")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_install_hooks_success(self, mock_open, mock_exists, mock_run, mock_check_git_repo_init):
        """Test successful installation of pre-commit hooks."""
        # Mock git repo check
        mock_check_git_repo_init.return_value = {
            "success": True,
            "initialized": True,
            "is_newly_initialized": True,
            "default_branch": "main"
        }
        
        # Mock pre-commit config file doesn't exist
        mock_exists.return_value = False
        
        # Mock subprocess.run for pip install and pre-commit install
        mock_run.return_value = mock.Mock(returncode=0, stdout="Hooks installed successfully")
        
        result = install_hooks("/path/to/repo")
        
        assert result["success"] is True
        assert "installed successfully" in result["message"]
        
        # Verify the config file was created
        mock_open.assert_called_once()
        
        # Verify pre-commit install was called
        mock_run.assert_called_with(
            ["pre-commit", "install"],
            cwd="/path/to/repo",
            capture_output=True,
            text=True,
            check=True
        )

    @mock.patch("mcp_server_practices.hooks.installer.check_git_repo_init")
    def test_install_hooks_not_a_repo(self, mock_check_git_repo_init):
        """Test installing hooks in a non-git repository."""
        # Mock git repo check failure
        mock_check_git_repo_init.return_value = {
            "success": False,
            "initialized": False,
            "error": "Not a Git repository"
        }
        
        result = install_hooks("/path/to/repo")
        
        assert result["success"] is False
        assert "Not a Git repository" in result["error"]

    @mock.patch("mcp_server_practices.hooks.installer.check_git_repo_init")
    @mock.patch("os.path.exists")
    @mock.patch("subprocess.run")
    def test_update_hooks_success(self, mock_run, mock_exists, mock_check_git_repo_init):
        """Test successful update of pre-commit hooks."""
        # Mock git repo check
        mock_check_git_repo_init.return_value = {
            "success": True,
            "initialized": True,
            "is_newly_initialized": False,
            "default_branch": "main"
        }
        
        # Mock pre-commit config file exists
        mock_exists.return_value = True
        
        # Mock subprocess.run for autoupdate
        mock_run.return_value = mock.Mock(returncode=0, stdout="Hooks updated successfully")
        
        result = update_hooks("/path/to/repo")
        
        assert result["success"] is True
        assert "updated successfully" in result["message"]
        
        # Verify pre-commit autoupdate was called
        mock_run.assert_called_with(
            ["pre-commit", "autoupdate"],
            cwd="/path/to/repo",
            capture_output=True,
            text=True,
            check=True
        )

    @mock.patch("mcp_server_practices.hooks.installer.check_git_repo_init")
    @mock.patch("os.path.exists")
    def test_update_hooks_no_config(self, mock_exists, mock_check_git_repo_init):
        """Test updating hooks when no config file exists."""
        # Mock git repo check
        mock_check_git_repo_init.return_value = {
            "success": True,
            "initialized": True,
            "is_newly_initialized": False,
            "default_branch": "main"
        }
        
        # Mock pre-commit config file doesn't exist
        mock_exists.return_value = False
        
        result = update_hooks("/path/to/repo")
        
        assert result["success"] is False
        assert "not installed" in result["error"]
