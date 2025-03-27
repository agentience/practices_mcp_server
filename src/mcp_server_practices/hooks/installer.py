#!/usr/bin/env python
"""
Pre-commit hooks installation functionality.

Copyright (c) 2025 Agentience.ai
Author: Troy Molander
License: MIT License - See LICENSE file for details

Version: 0.1.0
"""

import os
import subprocess
import time
from typing import Dict, Any, List, Optional
import shutil
import sys

from .templates import get_default_config


def check_git_repo_init(path: str) -> Dict[str, Any]:
    """
    Check if a Git repository was recently initialized.
    
    Args:
        path: Path to check for Git repository
        
    Returns:
        Dict with information about the repository
    """
    git_dir = os.path.join(path, ".git")
    
    # Check if .git directory exists
    if not os.path.isdir(git_dir):
        return {
            "success": False,
            "initialized": False,
            "error": "Not a Git repository"
        }
    
    try:
        # Get creation time of .git directory
        creation_time = os.path.getctime(git_dir)
        current_time = time.time()
        
        # If created within the last 5 minutes, consider it newly initialized
        is_new = (current_time - creation_time) < 300  # 5 minutes
        
        # Get default branch
        result = subprocess.run(
            ["git", "-C", path, "symbolic-ref", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=False
        )
        default_branch = result.stdout.strip() if result.returncode == 0 else "unknown"
        
        return {
            "success": True,
            "initialized": True,
            "is_newly_initialized": is_new,
            "default_branch": default_branch,
            "git_dir": git_dir
        }
    except Exception as e:
        return {
            "success": False,
            "initialized": True,
            "error": str(e)
        }


def install_hooks(repo_path: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Install pre-commit hooks in a Git repository.
    
    Args:
        repo_path: Path to the Git repository
        config: Optional configuration overrides
        
    Returns:
        Dict with installation result
    """
    repo_check = check_git_repo_init(repo_path)
    
    if not repo_check.get("initialized", False):
        return {
            "success": False,
            "error": "Not a Git repository"
        }
    
    # Ensure pre-commit is installed
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "pre-commit"],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": f"Failed to install pre-commit: {e.stderr}"
        }
    
    # Create pre-commit config file if it doesn't exist
    config_path = os.path.join(repo_path, ".pre-commit-config.yaml")
    
    if not os.path.exists(config_path):
        config_content = get_default_config(config)
        
        try:
            with open(config_path, "w") as f:
                f.write(config_content)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create config file: {str(e)}"
            }
    
    # Install the hooks
    try:
        result = subprocess.run(
            ["pre-commit", "install"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        return {
            "success": True,
            "message": "Pre-commit hooks installed successfully",
            "output": result.stdout
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": f"Failed to install hooks: {e.stderr}"
        }


def update_hooks(repo_path: str) -> Dict[str, Any]:
    """
    Update pre-commit hooks in a Git repository.
    
    Args:
        repo_path: Path to the Git repository
        
    Returns:
        Dict with update result
    """
    repo_check = check_git_repo_init(repo_path)
    
    if not repo_check.get("initialized", False):
        return {
            "success": False,
            "error": "Not a Git repository"
        }
    
    # Check if pre-commit is installed
    config_path = os.path.join(repo_path, ".pre-commit-config.yaml")
    if not os.path.exists(config_path):
        return {
            "success": False,
            "error": "Pre-commit hooks not installed"
        }
    
    # Update the hooks
    try:
        result = subprocess.run(
            ["pre-commit", "autoupdate"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        return {
            "success": True,
            "message": "Pre-commit hooks updated successfully",
            "output": result.stdout
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": f"Failed to update hooks: {e.stderr}"
        }
