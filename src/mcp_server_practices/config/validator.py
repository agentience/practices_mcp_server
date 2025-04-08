#!/usr/bin/env python
"""
Configuration validation functionality for the Practices MCP Server.

This module provides functions for validating configuration files,
checking file existence, and ensuring that configurations follow
the project's requirements.

Copyright (c) 2025 Agentience.ai
Author: Troy Molander
License: MIT License - See LICENSE file for details

Version: 0.2.0
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Union, Optional, Tuple

from .schema import ConfigurationSchema, ProjectConfig

logger = logging.getLogger(__name__)


def validate_config(config: Union[ConfigurationSchema, Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validate a configuration against the schema and check for logical errors.
    
    Args:
        config: Configuration to validate (schema object or dict)
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    # Convert dict to ConfigurationSchema if needed
    if isinstance(config, dict):
        try:
            config = ConfigurationSchema(**config)
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False, [f"Schema validation error: {e}"]
    
    errors: List[str] = []
    
    # Check branch configurations
    errors.extend(_validate_branch_configs(config))
    
    # Check version configurations
    if config.version:
        errors.extend(_validate_version_configs(config))
    
    # Check Jira integration configurations
    if config.jira and config.jira.enabled:
        errors.extend(_validate_jira_configs(config))
    
    # Check GitHub integration configurations
    if config.github and config.github.enabled:
        errors.extend(_validate_github_configs(config))
    
    return len(errors) == 0, errors


def _validate_branch_configs(config: ConfigurationSchema) -> List[str]:
    """
    Validate branch configurations for logical errors.
    
    Args:
        config: Configuration to validate
        
    Returns:
        List of error messages
    """
    errors: List[str] = []
    
    # Check if branching strategy and branch configs match
    if config.branching_strategy.value == "gitflow":
        # GitFlow requires develop branch
        if not config.develop_branch:
            errors.append("GitFlow strategy requires a develop_branch")
        
        # GitFlow requires certain branch types
        required_branches = ["feature", "bugfix", "release", "hotfix"]
        for branch_type in required_branches:
            if branch_type not in config.branches:
                errors.append(f"GitFlow strategy requires '{branch_type}' branch configuration")
    
    elif config.branching_strategy.value == "github-flow":
        # GitHub Flow requires certain branch types
        required_branches = ["feature", "bugfix"]
        for branch_type in required_branches:
            if branch_type not in config.branches:
                errors.append(f"GitHub Flow strategy requires '{branch_type}' branch configuration")
    
    elif config.branching_strategy.value == "trunk":
        # Trunk-based requires certain branch types
        required_branches = ["feature", "bugfix"]
        for branch_type in required_branches:
            if branch_type not in config.branches:
                errors.append(f"Trunk-based strategy requires '{branch_type}' branch configuration")
    
    # Check if branch patterns are valid regexes
    for branch_type, branch_config in config.branches.items():
        try:
            re.compile(branch_config.pattern)
        except re.error as e:
            errors.append(f"Invalid regex pattern for '{branch_type}' branch: {e}")
    
    # Check if base branches exist in config
    for branch_type, branch_config in config.branches.items():
        if branch_config.base not in [config.main_branch, config.develop_branch]:
            errors.append(f"Base branch '{branch_config.base}' for '{branch_type}' branch does not exist in configuration")
    
    # Check if target branches exist in config
    for branch_type, branch_config in config.branches.items():
        if branch_config.target:
            for target in branch_config.target:
                if target not in [config.main_branch, config.develop_branch]:
                    errors.append(f"Target branch '{target}' for '{branch_type}' branch does not exist in configuration")
    
    return errors


def _validate_version_configs(config: ConfigurationSchema) -> List[str]:
    """
    Validate version configurations for logical errors.
    
    Args:
        config: Configuration to validate
        
    Returns:
        List of error messages
    """
    errors: List[str] = []
    
    # Check if version files are specified
    if not config.version.files:
        errors.append("Version configuration requires at least one file")
    
    # Check if all version patterns have capture groups
    for file_config in config.version.files:
        try:
            pattern = re.compile(file_config.pattern)
            if pattern.groups < 1:
                errors.append(f"Version pattern '{file_config.pattern}' must have at least one capture group")
        except re.error as e:
            errors.append(f"Invalid regex pattern for version file: {e}")
    
    # Check if bumpversion config exists when use_bumpversion is True
    if config.version.use_bumpversion and config.version.bumpversion_config:
        # Note: We can't check file existence here as we don't have the project path
        pass
    
    return errors


def _validate_jira_configs(config: ConfigurationSchema) -> List[str]:
    """
    Validate Jira configurations for logical errors.
    
    Args:
        config: Configuration to validate
        
    Returns:
        List of error messages
    """
    errors: List[str] = []
    
    # Check if project key is specified
    if not config.jira.project_key:
        errors.append("Jira configuration requires a project_key")
    
    return errors


def _validate_github_configs(config: ConfigurationSchema) -> List[str]:
    """
    Validate GitHub configurations for logical errors.
    
    Args:
        config: Configuration to validate
        
    Returns:
        List of error messages
    """
    errors: List[str] = []
    
    # Nothing to validate for GitHub configs at the moment
    
    return errors


def validate_config_file_exists(
    directory: Union[str, Path], 
    create_if_missing: bool = False,
    project_config: Optional[ProjectConfig] = None
) -> Tuple[bool, Optional[Path]]:
    """
    Validate that a configuration file exists in the specified directory.
    
    Args:
        directory: Directory to check
        create_if_missing: Whether to create a default config if missing
        project_config: Optional ProjectConfig to use when creating
        
    Returns:
        Tuple of (exists, path)
    """
    from .loader import find_config_file, create_default_config
    
    directory = Path(directory).resolve()
    config_path = find_config_file(directory)
    
    if config_path:
        return True, config_path
    
    if create_if_missing:
        try:
            if project_config:
                from .loader import save_config
                config_path = save_config(project_config.config, directory=directory)
            else:
                config_path = create_default_config(directory)
            return True, config_path
        except Exception as e:
            logger.error(f"Failed to create configuration file: {e}")
            return False, None
    
    return False, None


def validate_file_paths(
    config: ConfigurationSchema, 
    project_root: Union[str, Path]
) -> Tuple[bool, List[str]]:
    """
    Validate that file paths in the configuration exist.
    
    Args:
        config: Configuration to validate
        project_root: Project root directory
        
    Returns:
        Tuple of (all_exist, missing_files)
    """
    project_root = Path(project_root).resolve()
    missing_files: List[str] = []
    
    logger.debug(f"Validating file paths in {project_root}")
    
    # Check version files
    if config.version:
        for file_config in config.version.files:
            file_path = project_root / file_config.path
            # Skip "__project__" placeholder paths or template paths
            if "__project__" in file_path.as_posix():
                logger.debug(f"Skipping template path: {file_path}")
                continue
                
            # Check if file exists
            if not file_path.exists():
                logger.debug(f"File not found: {file_path}")
                missing_files.append(file_config.path)
            else:
                logger.debug(f"File found: {file_path}")
        
        # Check bumpversion config
        if config.version.use_bumpversion and config.version.bumpversion_config:
            file_path = project_root / config.version.bumpversion_config
            if not file_path.exists():
                logger.debug(f"Bumpversion config not found: {file_path}")
                missing_files.append(config.version.bumpversion_config)
            else:
                logger.debug(f"Bumpversion config found: {file_path}")
        
        # Check changelog
        if config.version.changelog:
            file_path = project_root / config.version.changelog
            if not file_path.exists():
                logger.debug(f"Changelog not found: {file_path}")
                missing_files.append(config.version.changelog)
            else:
                logger.debug(f"Changelog found: {file_path}")
    
    # Check PR templates
    if config.pull_requests and config.pull_requests.templates:
        templates = config.pull_requests.templates.model_dump(exclude_none=True)
        for template_name, template_path in templates.items():
            if isinstance(template_path, str) and "/" in template_path:
                file_path = project_root / template_path
                if not file_path.exists():
                    logger.debug(f"PR template not found: {file_path}")
                    missing_files.append(template_path)
                else:
                    logger.debug(f"PR template found: {file_path}")
    
    logger.debug(f"Missing files: {missing_files}")
    return len(missing_files) == 0, missing_files
