#!/usr/bin/env python
"""
Configuration schema for the Practices MCP Server.

This module provides Pydantic models for validating and working with
configuration files. These schemas define the structure of the .practices.yaml
configuration file and provide validation rules.

Copyright (c) 2025 Agentience.ai
Author: Troy Molander
License: MIT License - See LICENSE file for details

Version: 0.2.0
"""

from enum import Enum
from typing import Dict, List, Optional, Union, Any, Pattern
import re
from pydantic import (
    BaseModel, 
    Field, 
    validator, 
    constr,
    field_validator,
    model_validator,
)


class ProjectType(str, Enum):
    """Supported project types."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    GENERIC = "generic"


class BranchingStrategy(str, Enum):
    """Supported branching strategies."""
    GITFLOW = "gitflow"
    GITHUB_FLOW = "github-flow"
    TRUNK = "trunk"


class WorkflowMode(str, Enum):
    """Workflow modes for development process."""
    SOLO = "solo"
    TEAM = "team"


class VersionBump(str, Enum):
    """Version bump types."""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    NONE = "none"


class BranchConfig(BaseModel):
    """Configuration for a specific branch type."""
    pattern: str = Field(..., description="Regex pattern for branch names")
    base: str = Field(..., description="Base branch to create from and merge to")
    target: Optional[List[str]] = Field(
        None, description="List of branches to merge to (for release and hotfix branches)"
    )
    version_bump: Optional[VersionBump] = Field(
        None, description="Type of version bump to perform"
    )

    @field_validator("pattern")
    def validate_pattern(cls, v):
        """Validate that the pattern is a valid regex."""
        try:
            re.compile(v)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        return v


class VersionFileConfig(BaseModel):
    """Configuration for a version file."""
    path: str = Field(..., description="Path to the file containing version")
    pattern: str = Field(..., description="Regex pattern to match version string")

    @field_validator("pattern")
    def validate_pattern(cls, v):
        """Validate that the pattern is a valid regex with capture group."""
        try:
            pattern = re.compile(v)
            # Check if there's at least one capture group
            if pattern.groups < 1:
                raise ValueError("Pattern must contain at least one capture group for the version")
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        return v


class VersionConfig(BaseModel):
    """Configuration for version management."""
    files: List[VersionFileConfig] = Field(
        ..., description="List of files containing version strings"
    )
    use_bumpversion: bool = Field(
        True, description="Whether to use bump2version for version management"
    )
    bumpversion_config: Optional[str] = Field(
        ".bumpversion.cfg", description="Path to the bump2version configuration file"
    )
    changelog: Optional[str] = Field(
        "CHANGELOG.md", description="Path to the changelog file"
    )


class PRTemplateConfig(BaseModel):
    """Configuration for PR templates."""
    feature: Optional[str] = Field(
        None, description="Template for feature PR descriptions"
    )
    bugfix: Optional[str] = Field(
        None, description="Template for bugfix PR descriptions"
    )
    release: Optional[str] = Field(
        None, description="Template for release PR descriptions"
    )
    hotfix: Optional[str] = Field(
        None, description="Template for hotfix PR descriptions"
    )
    docs: Optional[str] = Field(
        None, description="Template for documentation PR descriptions"
    )


class PRCheckConfig(BaseModel):
    """Configuration for PR checks."""
    run_tests: bool = Field(
        True, description="Whether to run tests before allowing PR creation"
    )
    run_linting: bool = Field(
        True, description="Whether to run linting before allowing PR creation"
    )


class PRConfig(BaseModel):
    """Configuration for PR management."""
    templates: Optional[PRTemplateConfig] = Field(
        None, description="Templates for PR descriptions"
    )
    checks: Optional[PRCheckConfig] = Field(
        None, description="Checks to run before PR creation"
    )


class JiraConfig(BaseModel):
    """Configuration for Jira integration."""
    enabled: bool = Field(
        True, description="Whether Jira integration is enabled"
    )
    project_key: str = Field(
        ..., description="Jira project key"
    )
    transition_to_in_progress: bool = Field(
        True, description="Whether to transition tickets to In Progress when creating branches"
    )
    update_on_pr_creation: bool = Field(
        True, description="Whether to update Jira tickets when PRs are created"
    )


class GitHubConfig(BaseModel):
    """Configuration for GitHub integration."""
    enabled: bool = Field(
        True, description="Whether GitHub integration is enabled"
    )
    owner: Optional[str] = Field(
        None, description="GitHub repository owner"
    )
    repo: Optional[str] = Field(
        None, description="GitHub repository name"
    )
    create_pr: bool = Field(
        True, description="Whether to automatically create PRs"
    )
    required_checks: Optional[List[str]] = Field(
        None, description="List of required checks for PRs"
    )


class PreCommitConfig(BaseModel):
    """Configuration for pre-commit hooks."""
    hooks: List[Dict[str, Any]] = Field(
        [], description="List of pre-commit hooks to install"
    )


class LicenseHeaderTemplate(BaseModel):
    """Template for license headers."""
    template: str = Field(
        ..., description="License header template text"
    )
    file_types: List[Dict[str, str]] = Field(
        [], description="Configuration for different file types"
    )


class ConfigurationSchema(BaseModel):
    """Main configuration schema."""
    project_type: ProjectType = Field(
        ProjectType.PYTHON, description="Project language or framework"
    )
    branching_strategy: BranchingStrategy = Field(
        BranchingStrategy.GITFLOW, description="Branching strategy to use"
    )
    workflow_mode: WorkflowMode = Field(
        WorkflowMode.SOLO, description="Development workflow mode"
    )
    main_branch: str = Field(
        "main", description="Name of the main/production branch"
    )
    develop_branch: Optional[str] = Field(
        "develop", description="Name of the development branch (for GitFlow)"
    )
    branches: Dict[str, BranchConfig] = Field(
        {}, description="Configuration for branch types"
    )
    version: Optional[VersionConfig] = Field(
        None, description="Configuration for version management"
    )
    pull_requests: Optional[PRConfig] = Field(
        None, description="Configuration for pull requests"
    )
    jira: Optional[JiraConfig] = Field(
        None, description="Configuration for Jira integration"
    )
    github: Optional[GitHubConfig] = Field(
        None, description="Configuration for GitHub integration"
    )
    pre_commit: Optional[PreCommitConfig] = Field(
        None, description="Configuration for pre-commit hooks"
    )
    license_headers: Optional[LicenseHeaderTemplate] = Field(
        None, description="Configuration for license headers"
    )

    @model_validator(mode='after')
    def validate_branch_configs(self) -> 'ConfigurationSchema':
        """Validate that required branch configurations are present."""
        if self.branching_strategy == BranchingStrategy.GITFLOW:
            # Check that develop branch is set for GitFlow
            if not self.develop_branch:
                raise ValueError("develop_branch must be set for GitFlow")
                
        # Check that branch configurations exist for basic branch types
        if "feature" not in self.branches:
            raise ValueError("Branch configuration for 'feature' is required")
            
        return self
    
    @model_validator(mode='after')
    def validate_version_config(self) -> 'ConfigurationSchema':
        """Validate version configuration for consistency."""
        if self.version is not None:
            # Check that version files are specified
            if not self.version.files:
                raise ValueError("At least one version file must be specified")
                
        return self


class ProjectConfig(BaseModel):
    """Configuration with file location information."""
    config: ConfigurationSchema = Field(
        ..., description="Project configuration"
    )
    path: Optional[str] = Field(
        None, description="Path to configuration file"
    )
    is_default: bool = Field(
        False, description="Whether this is a default configuration"
    )
