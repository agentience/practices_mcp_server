#!/usr/bin/env python
"""
Unit tests for configuration schema.

These tests validate the configuration schema validation logic.
"""

import pytest
from pathlib import Path
import re

from mcp_server_practices.config.schema import (
    ConfigurationSchema,
    ProjectConfig,
    ProjectType,
    BranchingStrategy,
    WorkflowMode,
    BranchConfig,
    VersionFileConfig,
    VersionConfig,
    VersionBump,
)


def test_branch_config_validation():
    """Test validation of branch configuration."""
    # Valid configuration
    valid_config = BranchConfig(
        pattern="^feature/([A-Z]+-\\d+)-(.+)$",
        base="develop",
        version_bump=None
    )
    assert valid_config.pattern == "^feature/([A-Z]+-\\d+)-(.+)$"
    assert valid_config.base == "develop"
    assert valid_config.version_bump is None
    
    # Invalid regex pattern
    with pytest.raises(ValueError) as excinfo:
        BranchConfig(
            pattern="^feature/([A-Z+-\\d+)-(.+)$",  # Invalid regex (unclosed character class)
            base="develop",
            version_bump=None
        )
    assert "Invalid regex pattern" in str(excinfo.value)


def test_version_file_config_validation():
    """Test validation of version file configuration."""
    # Valid configuration
    valid_config = VersionFileConfig(
        path="src/package/__init__.py",
        pattern="__version__ = \"(\\d+\\.\\d+\\.\\d+)\""
    )
    assert valid_config.path == "src/package/__init__.py"
    assert valid_config.pattern == "__version__ = \"(\\d+\\.\\d+\\.\\d+)\""
    
    # Pattern without capture group
    with pytest.raises(ValueError) as excinfo:
        VersionFileConfig(
            path="src/package/__init__.py",
            pattern="__version__ = \"\\d+\\.\\d+\\.\\d+\""  # No capture group
        )
    assert "Pattern must contain at least one capture group" in str(excinfo.value)
    
    # Invalid regex pattern
    with pytest.raises(ValueError) as excinfo:
        VersionFileConfig(
            path="src/package/__init__.py",
            pattern="__version__ = \"(\\d+\\.\\d+\\.\\d+"  # Unclosed parenthesis
        )
    assert "Invalid regex pattern" in str(excinfo.value)


def test_version_config_validation():
    """Test validation of version configuration."""
    # Valid configuration
    valid_config = VersionConfig(
        files=[
            VersionFileConfig(
                path="src/package/__init__.py",
                pattern="__version__ = \"(\\d+\\.\\d+\\.\\d+)\""
            ),
            VersionFileConfig(
                path="pyproject.toml",
                pattern="version = \"(\\d+\\.\\d+\\.\\d+)\""
            )
        ],
        use_bumpversion=True,
        bumpversion_config=".bumpversion.cfg",
        changelog="CHANGELOG.md"
    )
    assert len(valid_config.files) == 2
    assert valid_config.use_bumpversion is True
    assert valid_config.bumpversion_config == ".bumpversion.cfg"
    assert valid_config.changelog == "CHANGELOG.md"


def test_configuration_schema_validation():
    """Test validation of full configuration schema."""
    # Minimal valid configuration
    minimal_config = ConfigurationSchema(
        project_type=ProjectType.PYTHON,
        branching_strategy=BranchingStrategy.GITFLOW,
        workflow_mode=WorkflowMode.SOLO,
        main_branch="main",
        develop_branch="develop",
        branches={
            "feature": BranchConfig(
                pattern="^feature/([A-Z]+-\\d+)-(.+)$",
                base="develop",
                version_bump=None
            )
        }
    )
    assert minimal_config.project_type == ProjectType.PYTHON
    assert minimal_config.branching_strategy == BranchingStrategy.GITFLOW
    assert minimal_config.workflow_mode == WorkflowMode.SOLO
    assert minimal_config.main_branch == "main"
    assert minimal_config.develop_branch == "develop"
    assert "feature" in minimal_config.branches
    
    # GitFlow without develop branch should fail
    with pytest.raises(ValueError) as excinfo:
        config = ConfigurationSchema(
            project_type=ProjectType.PYTHON,
            branching_strategy=BranchingStrategy.GITFLOW,
            workflow_mode=WorkflowMode.SOLO,
            main_branch="main",
            develop_branch=None,
            branches={
                "feature": BranchConfig(
                    pattern="^feature/([A-Z]+-\\d+)-(.+)$",
                    base="develop",
                    version_bump=None
                )
            }
        )
        # The validator runs after model creation with the new model_validator decorator
        _ = config.model_dump()
    assert "develop_branch must be set for GitFlow" in str(excinfo.value)
    
    # GitHub Flow is valid without develop branch
    github_flow_config = ConfigurationSchema(
        project_type=ProjectType.PYTHON,
        branching_strategy=BranchingStrategy.GITHUB_FLOW,
        workflow_mode=WorkflowMode.SOLO,
        main_branch="main",
        develop_branch=None,
        branches={
            "feature": BranchConfig(
                pattern="^feature/([A-Z]+-\\d+)-(.+)$",
                base="main",
                version_bump=None
            ),
            "bugfix": BranchConfig(
                pattern="^bugfix/([A-Z]+-\\d+)-(.+)$",
                base="main",
                version_bump=None
            )
        }
    )
    assert github_flow_config.branching_strategy == BranchingStrategy.GITHUB_FLOW
    assert github_flow_config.develop_branch is None


def test_project_config():
    """Test project configuration wrapper."""
    # Create a configuration
    config = ConfigurationSchema(
        project_type=ProjectType.PYTHON,
        branching_strategy=BranchingStrategy.GITFLOW,
        workflow_mode=WorkflowMode.SOLO,
        main_branch="main",
        develop_branch="develop",
        branches={
            "feature": BranchConfig(
                pattern="^feature/([A-Z]+-\\d+)-(.+)$",
                base="develop",
                version_bump=None
            )
        }
    )
    
    # Wrap in ProjectConfig
    project_config = ProjectConfig(
        config=config,
        path="/path/to/config.yaml",
        is_default=False
    )
    
    assert project_config.config is config
    assert project_config.path == "/path/to/config.yaml"
    assert project_config.is_default is False
    
    # Default configuration
    default_config = ProjectConfig(
        config=config,
        path=None,
        is_default=True
    )
    
    assert default_config.config is config
    assert default_config.path is None
    assert default_config.is_default is True


def test_enum_values():
    """Test enum values."""
    # ProjectType
    assert ProjectType.PYTHON.value == "python"
    assert ProjectType.JAVASCRIPT.value == "javascript"
    assert ProjectType.TYPESCRIPT.value == "typescript"
    assert ProjectType.JAVA.value == "java"
    assert ProjectType.CSHARP.value == "csharp"
    assert ProjectType.GO.value == "go"
    assert ProjectType.RUST.value == "rust"
    assert ProjectType.GENERIC.value == "generic"
    
    # BranchingStrategy
    assert BranchingStrategy.GITFLOW.value == "gitflow"
    assert BranchingStrategy.GITHUB_FLOW.value == "github-flow"
    assert BranchingStrategy.TRUNK.value == "trunk"
    
    # WorkflowMode
    assert WorkflowMode.SOLO.value == "solo"
    assert WorkflowMode.TEAM.value == "team"
    
    # VersionBump
    assert VersionBump.MAJOR.value == "major"
    assert VersionBump.MINOR.value == "minor"
    assert VersionBump.PATCH.value == "patch"
    assert VersionBump.NONE.value == "none"


def test_full_configuration():
    """Test a full configuration with all options."""
    # Create a complete configuration
    full_config = ConfigurationSchema(
        project_type=ProjectType.PYTHON,
        branching_strategy=BranchingStrategy.GITFLOW,
        workflow_mode=WorkflowMode.TEAM,
        main_branch="main",
        develop_branch="develop",
        branches={
            "feature": BranchConfig(
                pattern="^feature/([A-Z]+-\\d+)-(.+)$",
                base="develop",
                version_bump=None
            ),
            "bugfix": BranchConfig(
                pattern="^bugfix/([A-Z]+-\\d+)-(.+)$",
                base="develop",
                version_bump=None
            ),
            "hotfix": BranchConfig(
                pattern="^hotfix/(\\d+\\.\\d+\\.\\d+(?:-[a-zA-Z0-9.]+)?)-(.+)$",
                base="main",
                target=["main", "develop"],
                version_bump=VersionBump.PATCH
            ),
            "release": BranchConfig(
                pattern="^release/(\\d+\\.\\d+\\.\\d+(?:-[a-zA-Z0-9.]+)?)(?:-(.+))?$",
                base="develop",
                target=["main", "develop"],
                version_bump=VersionBump.MINOR
            ),
            "docs": BranchConfig(
                pattern="^docs/(.+)$",
                base="develop",
                version_bump=None
            )
        },
        version=VersionConfig(
            files=[
                VersionFileConfig(
                    path="src/package/__init__.py",
                    pattern="__version__ = \"(\\d+\\.\\d+\\.\\d+)\""
                ),
                VersionFileConfig(
                    path="pyproject.toml",
                    pattern="version = \"(\\d+\\.\\d+\\.\\d+)\""
                )
            ],
            use_bumpversion=True,
            bumpversion_config=".bumpversion.cfg",
            changelog="CHANGELOG.md"
        ),
        jira={
            "enabled": True,
            "project_key": "PMS",
            "transition_to_in_progress": True,
            "update_on_pr_creation": True
        },
        github={
            "enabled": True,
            "create_pr": True,
            "required_checks": ["tests", "lint"]
        }
    )
    
    assert full_config.project_type == ProjectType.PYTHON
    assert full_config.branching_strategy == BranchingStrategy.GITFLOW
    assert full_config.workflow_mode == WorkflowMode.TEAM
    assert full_config.main_branch == "main"
    assert full_config.develop_branch == "develop"
    
    assert len(full_config.branches) == 5
    assert "feature" in full_config.branches
    assert "bugfix" in full_config.branches
    assert "hotfix" in full_config.branches
    assert "release" in full_config.branches
    assert "docs" in full_config.branches
    
    assert full_config.branches["hotfix"].version_bump == VersionBump.PATCH
    assert full_config.branches["release"].version_bump == VersionBump.MINOR
    
    assert full_config.version.use_bumpversion is True
    assert len(full_config.version.files) == 2
    
    assert full_config.jira.project_key == "PMS"
    assert full_config.github.required_checks == ["tests", "lint"]
