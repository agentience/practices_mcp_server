#!/usr/bin/env python
"""
Project type detection and default configuration generation.

This module provides functionality to detect the type of a project based
on files in the project directory and to generate default configurations
for different project types.

Copyright (c) 2025 Agentience.ai
Author: Troy Molander
License: MIT License - See LICENSE file for details

Version: 0.2.0
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Union, Optional, List, Set, Tuple

from .schema import ProjectType, BranchingStrategy, WorkflowMode

logger = logging.getLogger(__name__)

# Mapping of file patterns to project types
PROJECT_TYPE_INDICATORS = {
    ProjectType.PYTHON: [
        {"file": "pyproject.toml"},
        {"file": "setup.py"},
        {"file": "requirements.txt"},
        {"dir": "src", "file": "__init__.py"},
        {"ext": ".py", "min_count": 3},
    ],
    ProjectType.JAVASCRIPT: [
        {"file": "package.json"},
        {"file": "node_modules"},
        {"ext": ".js", "min_count": 3},
        {"ext": ".jsx", "min_count": 1},
    ],
    ProjectType.TYPESCRIPT: [
        {"file": "tsconfig.json"},
        {"ext": ".ts", "min_count": 3},
        {"ext": ".tsx", "min_count": 1},
    ],
    ProjectType.JAVA: [
        {"file": "pom.xml"},
        {"file": "build.gradle"},
        {"dir": "src/main/java"},
        {"ext": ".java", "min_count": 3},
    ],
    ProjectType.CSHARP: [
        {"file": ".sln"},
        {"ext": ".csproj", "min_count": 1},
        {"ext": ".cs", "min_count": 3},
    ],
    ProjectType.GO: [
        {"file": "go.mod"},
        {"file": "go.sum"},
        {"ext": ".go", "min_count": 3},
    ],
    ProjectType.RUST: [
        {"file": "Cargo.toml"},
        {"file": "Cargo.lock"},
        {"ext": ".rs", "min_count": 3},
    ],
}


def detect_project_type(directory: Union[str, Path]) -> ProjectType:
    """
    Detect the project type based on files in the directory.
    
    Args:
        directory: Project directory to analyze
        
    Returns:
        Detected project type (defaults to GENERIC if unknown)
    """
    directory = Path(directory).resolve()
    
    if not directory.exists() or not directory.is_dir():
        logger.warning(f"Directory does not exist or is not a directory: {directory}")
        return ProjectType.GENERIC
    
    # Check each project type's indicators
    scores: Dict[ProjectType, int] = {pt: 0 for pt in ProjectType}
    
    for project_type, indicators in PROJECT_TYPE_INDICATORS.items():
        for indicator in indicators:
            if "file" in indicator and "dir" in indicator:
                # Check for file in specific directory
                file_path = directory / indicator["dir"] / indicator["file"]
                if file_path.exists():
                    scores[project_type] += 2  # Higher score for specific path matches
            elif "file" in indicator:
                # Check for file in root
                file_path = directory / indicator["file"]
                if file_path.exists():
                    scores[project_type] += 2  # Higher score for specific file matches
            elif "ext" in indicator:
                # Count files with extension
                ext = indicator["ext"]
                min_count = indicator.get("min_count", 1)
                
                # Recursively find files with the extension
                count = 0
                for root, _, files in os.walk(directory):
                    for file in files:
                        if file.endswith(ext):
                            count += 1
                            if count >= min_count:
                                break
                    if count >= min_count:
                        break
                
                if count >= min_count:
                    scores[project_type] += 1  # Lower score for extension matches
    
    # Get the project type with the highest score
    max_score = 0
    detected_type = ProjectType.GENERIC
    
    for project_type, score in scores.items():
        if score > max_score:
            max_score = score
            detected_type = project_type
    
    logger.info(f"Detected project type: {detected_type} (score: {max_score})")
    return detected_type


def detect_branching_strategy(directory: Union[str, Path]) -> BranchingStrategy:
    """
    Detect the branching strategy based on the repository structure.
    
    Args:
        directory: Project directory with Git repository
        
    Returns:
        Detected branching strategy (defaults to GITFLOW)
    """
    # This is a simplified implementation - a real one would analyze
    # the Git history and branch structure
    return BranchingStrategy.GITFLOW


def get_default_gitflow_config() -> Dict[str, Any]:
    """
    Get default GitFlow configuration.
    
    Returns:
        Dictionary with GitFlow configuration
    """
    return {
        "branching_strategy": "gitflow",
        "main_branch": "main",
        "develop_branch": "develop",
        "branches": {
            "feature": {
                "pattern": "^feature/([A-Z]+-\\d+)-(.+)$",
                "base": "develop",
                "version_bump": None
            },
            "bugfix": {
                "pattern": "^bugfix/([A-Z]+-\\d+)-(.+)$",
                "base": "develop",
                "version_bump": None
            },
            "hotfix": {
                "pattern": "^hotfix/(\\d+\\.\\d+\\.\\d+(?:-[a-zA-Z0-9.]+)?)-(.+)$",
                "base": "main",
                "target": ["main", "develop"],
                "version_bump": "patch"
            },
            "release": {
                "pattern": "^release/(\\d+\\.\\d+\\.\\d+(?:-[a-zA-Z0-9.]+)?)(?:-(.+))?$",
                "base": "develop",
                "target": ["main", "develop"],
                "version_bump": "minor"
            },
            "docs": {
                "pattern": "^docs/(.+)$",
                "base": "develop",
                "version_bump": None
            }
        }
    }


def get_default_github_flow_config() -> Dict[str, Any]:
    """
    Get default GitHub Flow configuration.
    
    Returns:
        Dictionary with GitHub Flow configuration
    """
    return {
        "branching_strategy": "github-flow",
        "main_branch": "main",
        "branches": {
            "feature": {
                "pattern": "^feature/([A-Z]+-\\d+)-(.+)$",
                "base": "main",
                "version_bump": None
            },
            "bugfix": {
                "pattern": "^bugfix/([A-Z]+-\\d+)-(.+)$",
                "base": "main",
                "version_bump": None
            },
            "hotfix": {
                "pattern": "^hotfix/(\\d+\\.\\d+\\.\\d+(?:-[a-zA-Z0-9.]+)?)-(.+)$",
                "base": "main",
                "version_bump": "patch"
            },
            "docs": {
                "pattern": "^docs/(.+)$",
                "base": "main",
                "version_bump": None
            }
        }
    }


def get_default_trunk_config() -> Dict[str, Any]:
    """
    Get default Trunk-Based Development configuration.
    
    Returns:
        Dictionary with Trunk-Based Development configuration
    """
    return {
        "branching_strategy": "trunk",
        "main_branch": "main",
        "branches": {
            "feature": {
                "pattern": "^feature/([A-Z]+-\\d+)-(.+)$",
                "base": "main",
                "version_bump": None
            },
            "bugfix": {
                "pattern": "^bugfix/([A-Z]+-\\d+)-(.+)$",
                "base": "main",
                "version_bump": None
            },
            "release": {
                "pattern": "^release/(\\d+\\.\\d+\\.\\d+(?:-[a-zA-Z0-9.]+)?)$",
                "base": "main",
                "version_bump": "minor"
            }
        }
    }


def get_default_python_version_config() -> Dict[str, Any]:
    """
    Get default version configuration for Python projects.
    
    Returns:
        Dictionary with Python version configuration
    """
    return {
        "files": [
            {
                "path": "src/__project__/__init__.py",
                "pattern": "__version__ = \"(\\d+\\.\\d+\\.\\d+)\""
            },
            {
                "path": "pyproject.toml",
                "pattern": "version = \"(\\d+\\.\\d+\\.\\d+)\""
            }
        ],
        "use_bumpversion": True,
        "bumpversion_config": ".bumpversion.cfg",
        "changelog": "CHANGELOG.md"
    }


def get_default_javascript_version_config() -> Dict[str, Any]:
    """
    Get default version configuration for JavaScript projects.
    
    Returns:
        Dictionary with JavaScript version configuration
    """
    return {
        "files": [
            {
                "path": "package.json",
                "pattern": "\"version\": \"(\\d+\\.\\d+\\.\\d+)\""
            }
        ],
        "use_bumpversion": False,
        "changelog": "CHANGELOG.md"
    }


def get_default_java_version_config() -> Dict[str, Any]:
    """
    Get default version configuration for Java projects.
    
    Returns:
        Dictionary with Java version configuration
    """
    return {
        "files": [
            {
                "path": "pom.xml",
                "pattern": "<version>(\\d+\\.\\d+\\.\\d+)</version>"
            }
        ],
        "use_bumpversion": False,
        "changelog": "CHANGELOG.md"
    }


def get_default_pr_config() -> Dict[str, Any]:
    """
    Get default PR configuration.
    
    Returns:
        Dictionary with PR configuration
    """
    return {
        "templates": {
            "feature": "# {ticket_id}: {description}\n\n## Summary\nThis PR implements {description} functionality ({ticket_id}).\n\n## Changes\n-\n\n## Testing\n-\n\n## Related Issues\n- {ticket_id}: {ticket_description}",
            "bugfix": "# {ticket_id}: Fix {description}\n\n## Summary\nThis PR fixes {description} issue ({ticket_id}).\n\n## Root Cause\n-\n\n## Changes\n-\n\n## Testing\n-\n\n## Related Issues\n- {ticket_id}: {ticket_description}",
            "release": "# Release {version}\n\n## Summary\nThis PR prepares the release of version {version}.\n\n## Changes\n- Version bump to {version}\n- Updated CHANGELOG.md\n\n## Testing\n- Verified all tests pass\n- Checked version consistency\n\n## Release Notes\nSee CHANGELOG.md for details.",
            "hotfix": "# Hotfix {version}: {description}\n\n## Summary\nThis PR fixes a critical issue in production: {description}.\n\n## Root Cause\n-\n\n## Changes\n-\n\n## Testing\n-\n\n## Deployment Plan\n-"
        },
        "checks": {
            "run_tests": True,
            "run_linting": True
        }
    }


def get_default_jira_config(project_key: str = "PMS") -> Dict[str, Any]:
    """
    Get default Jira configuration.
    
    Args:
        project_key: Jira project key
        
    Returns:
        Dictionary with Jira configuration
    """
    return {
        "enabled": True,
        "project_key": project_key,
        "transition_to_in_progress": True,
        "update_on_pr_creation": True
    }


def get_default_github_config() -> Dict[str, Any]:
    """
    Get default GitHub configuration.
    
    Returns:
        Dictionary with GitHub configuration
    """
    return {
        "enabled": True,
        "create_pr": True,
        "required_checks": ["tests"]
    }


def get_default_generic_version_config() -> Dict[str, Any]:
    """
    Get default version configuration for generic projects.
    
    Returns:
        Dictionary with generic version configuration
    """
    return {
        "files": [
            {
                "path": "VERSION",
                "pattern": "(\\d+\\.\\d+\\.\\d+)"
            }
        ],
        "use_bumpversion": False,
        "changelog": "CHANGELOG.md"
    }


def get_default_config(project_type: ProjectType) -> Dict[str, Any]:
    """
    Get default configuration for a project type.
    
    Args:
        project_type: Project type to get configuration for
        
    Returns:
        Dictionary with default configuration
    """
    # Start with GitFlow branching strategy
    config = get_default_gitflow_config()
    
    # Set project type
    config["project_type"] = project_type.value
    
    # Set workflow mode
    config["workflow_mode"] = WorkflowMode.SOLO.value
    
    # Add version configuration based on project type
    if project_type == ProjectType.PYTHON:
        config["version"] = get_default_python_version_config()
    elif project_type in [ProjectType.JAVASCRIPT, ProjectType.TYPESCRIPT]:
        config["version"] = get_default_javascript_version_config()
    elif project_type == ProjectType.JAVA:
        config["version"] = get_default_java_version_config()
    else:
        # Generic version config for any other project type
        config["version"] = get_default_generic_version_config()
    
    # Add PR configuration
    config["pull_requests"] = get_default_pr_config()
    
    # Add Jira configuration
    config["jira"] = get_default_jira_config()
    
    # Add GitHub configuration
    config["github"] = get_default_github_config()
    
    return config
