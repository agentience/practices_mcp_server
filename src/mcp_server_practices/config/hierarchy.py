#!/usr/bin/env python
"""
Hierarchical configuration loading for the Practices MCP Server.

This module implements hierarchical configuration loading, allowing
configurations to be merged from multiple sources:
1. Default configuration based on project type
2. Team configuration (.practices.yaml in parent directories)
3. Project configuration (.practices.yaml in current directory)
4. User overrides (.practices.user.yaml)

Copyright (c) 2025 Agentience.ai
Author: Troy Molander
License: MIT License - See LICENSE file for details

Version: 0.2.0
"""

import os
import logging
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple

from .schema import ConfigurationSchema, ProjectConfig, ProjectType
from .detector import detect_project_type, get_default_config
from .loader import find_config_file, load_yaml_file

logger = logging.getLogger(__name__)

# Configuration file names
CONFIG_FILENAME = ".practices.yaml"
CONFIG_FILENAME_ALT = ".practices.yml"
USER_CONFIG_FILENAME = ".practices.user.yaml"
USER_CONFIG_FILENAME_ALT = ".practices.user.yml"


def find_hierarchical_configs(
    directory: Union[str, Path]
) -> List[Tuple[Path, str]]:
    """
    Find all configuration files in the directory hierarchy.
    
    Args:
        directory: Project directory
        
    Returns:
        List of (config_path, level) tuples, from root to project
    """
    directory = Path(directory).resolve()
    configs: List[Tuple[Path, str]] = []
    
    # Find user config in project directory
    user_config = directory / USER_CONFIG_FILENAME
    if user_config.exists():
        configs.append((user_config, "user"))
    else:
        user_config_alt = directory / USER_CONFIG_FILENAME_ALT
        if user_config_alt.exists():
            configs.append((user_config_alt, "user"))
    
    # Find project config
    project_config = find_config_file(directory)
    if project_config:
        configs.append((project_config, "project"))
    
    # Find team configs in parent directories
    current = directory.parent
    while current != current.parent:  # Stop at filesystem root
        team_config = find_config_file(current)
        if team_config:
            configs.append((team_config, "team"))
        current = current.parent
    
    # Sort from root to project
    configs.reverse()
    
    return configs


def merge_configs(
    configs: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Merge multiple configurations with increasing specificity.
    
    Args:
        configs: List of configuration dictionaries
        
    Returns:
        Merged configuration dictionary
    """
    if not configs:
        return {}
    
    result = configs[0].copy()
    
    for config in configs[1:]:
        _merge_dicts(result, config)
    
    return result


def _merge_dicts(
    base: Dict[str, Any],
    overlay: Dict[str, Any]
) -> None:
    """
    Merge overlay dict into base dict, modifying base in-place.
    
    Args:
        base: Base dictionary
        overlay: Overlay dictionary with higher priority
    """
    for key, value in overlay.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            # Recursively merge dicts
            _merge_dicts(base[key], value)
        else:
            # Replace or add values
            base[key] = value


def load_hierarchical_config(
    directory: Union[str, Path]
) -> Tuple[ProjectConfig, List[Tuple[Path, str]]]:
    """
    Load configuration from all levels of hierarchy.
    
    Args:
        directory: Project directory
        
    Returns:
        Tuple of (merged ProjectConfig, list of config sources)
    """
    directory = Path(directory).resolve()
    
    # Detect project type
    project_type, confidence, scores = detect_project_type(directory)
    
    # Get default config for project type
    default_config = get_default_config(project_type)
    
    # Find all config files in hierarchy
    config_files = find_hierarchical_configs(directory)
    
    # Load each config file
    configs = [default_config]
    sources = [f"default ({project_type.value})"]
    
    for config_path, level in config_files:
        try:
            config_dict = load_yaml_file(config_path)
            configs.append(config_dict)
            sources.append(f"{level} ({config_path})")
            logger.info(f"Loaded {level} configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading {level} configuration from {config_path}: {e}")
    
    # Merge configs
    merged_config = merge_configs(configs)
    
    # Create ProjectConfig
    config_schema = ConfigurationSchema(**merged_config)
    project_config = ProjectConfig(
        config=config_schema,
        path=str(directory / CONFIG_FILENAME),
        is_default=len(config_files) == 0
    )
    
    logger.info(f"Configuration sources: {', '.join(sources)}")
    
    return project_config, configs


def create_user_config(
    directory: Union[str, Path],
    overrides: Dict[str, Any]
) -> Path:
    """
    Create or update a user configuration file with overrides.
    
    Args:
        directory: Project directory
        overrides: Configuration overrides
        
    Returns:
        Path to the created user config file
    """
    directory = Path(directory).resolve()
    user_config_path = directory / USER_CONFIG_FILENAME
    
    # Load existing user config if it exists
    existing = {}
    if user_config_path.exists():
        try:
            existing = load_yaml_file(user_config_path)
        except Exception as e:
            logger.error(f"Error loading user configuration: {e}")
    
    # Merge with existing
    for key, value in overrides.items():
        if key in existing and isinstance(existing[key], dict) and isinstance(value, dict):
            # Merge dicts
            _merge_dicts(existing[key], value)
        else:
            # Replace or add values
            existing[key] = value
    
    # Write back
    with open(user_config_path, 'w') as f:
        yaml.dump(existing, f, default_flow_style=False)
    
    logger.info(f"Created/updated user configuration at {user_config_path}")
    
    return user_config_path
