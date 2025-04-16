#!/usr/bin/env python
"""
Configuration loading functionality for the Practices MCP Server.

This module handles loading, validating, and saving configuration files.
It supports loading from .practices.yaml files and provides fallback
to default configurations when needed.

Copyright (c) 2025 Agentience.ai
Author: Troy Molander
License: MIT License - See LICENSE file for details

Version: 0.2.0
"""

import os
import yaml
import logging
import enum
from pathlib import Path
from typing import Dict, Optional, Union, Any, Tuple

from pydantic import BaseModel

from .schema import ConfigurationSchema, ProjectConfig, ProjectType
from .detector import detect_project_type, get_default_config

logger = logging.getLogger(__name__)

# Standard configuration file name
CONFIG_FILENAME = ".practices.yaml"
CONFIG_FILENAME_ALT = ".practices.yml"


# Custom YAML representers for Pydantic models and enums
def _represent_enum(dumper, data):
    """Custom YAML representer for enum values."""
    return dumper.represent_scalar('tag:yaml.org,2002:str', data.value)


def _represent_pydantic_model(dumper, data):
    """Custom YAML representer for Pydantic models."""
    return dumper.represent_mapping('tag:yaml.org,2002:map', data.model_dump(exclude_none=True))


# Register custom representers
yaml.add_representer(enum.Enum, _represent_enum)
yaml.add_multi_representer(BaseModel, _represent_pydantic_model)


def find_config_file(directory: Union[str, Path] = ".") -> Optional[Path]:
    """
    Find the configuration file in the given directory.
    
    Args:
        directory: Directory to search in (defaults to current directory)
        
    Returns:
        Path to the configuration file or None if not found
    """
    directory = Path(directory).resolve()
    
    # Check for .practices.yaml
    config_path = directory / CONFIG_FILENAME
    if config_path.exists():
        return config_path
        
    # Check for alternative .practices.yml
    config_path_alt = directory / CONFIG_FILENAME_ALT
    if config_path_alt.exists():
        return config_path_alt
        
    return None


def load_yaml_file(path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load a YAML file as a dictionary.
    
    Args:
        path: Path to the YAML file
        
    Returns:
        Dictionary with the YAML content
        
    Raises:
        FileNotFoundError: If the file does not exist
        yaml.YAMLError: If the YAML is invalid
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
        
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file {path}: {e}")
        raise


def save_yaml_file(path: Union[str, Path], data: Dict[str, Any]) -> None:
    """
    Save a dictionary as a YAML file.
    
    Args:
        path: Path to save the YAML file
        data: Dictionary to save
        
    Raises:
        yaml.YAMLError: If the data cannot be serialized to YAML
    """
    path = Path(path)
    
    # Create parent directories if they don't exist
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def load_config(
    directory: Union[str, Path] = ".",
    config_path: Optional[Union[str, Path]] = None,
    detect_project: bool = True,
    use_hierarchy: bool = True,
) -> ProjectConfig:
    """
    Load configuration from a file or use defaults.
    
    Args:
        directory: Directory to search for configuration
        config_path: Explicit path to configuration file (optional)
        detect_project: Whether to detect project type if no config is found
        use_hierarchy: Whether to use hierarchical configuration loading
        
    Returns:
        ProjectConfig with the loaded configuration
        
    Raises:
        FileNotFoundError: If the specified config_path does not exist
        ValueError: If the configuration is invalid
    """
    # Convert paths to Path objects
    directory = Path(directory).resolve()
    
    # If explicit path is provided, use simple loading
    if config_path:
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
            
        # Load the configuration file
        try:
            config_dict = load_yaml_file(path)
            logger.info(f"Loaded configuration from {path}")
        except Exception as e:
            logger.error(f"Error loading configuration from {path}: {e}")
            raise ValueError(f"Invalid configuration file: {e}")
            
        # Validate configuration
        try:
            config = ConfigurationSchema(**config_dict)
        except Exception as e:
            logger.error(f"Invalid configuration: {e}")
            raise ValueError(f"Invalid configuration: {e}")
            
        return ProjectConfig(
            config=config,
            path=str(path),
            is_default=False
        )
    
    # Use hierarchical loading if requested
    if use_hierarchy:
        try:
            from .hierarchy import load_hierarchical_config
            project_config, _ = load_hierarchical_config(directory)
            return project_config
        except ImportError:
            logger.warning("Hierarchical configuration loading not available, falling back to simple loading")
            use_hierarchy = False
    
    # Simple (non-hierarchical) loading
    path = find_config_file(directory)
    is_default = False
    config_dict = {}
    
    if path:
        # Load the configuration file
        try:
            config_dict = load_yaml_file(path)
            logger.info(f"Loaded configuration from {path}")
        except Exception as e:
            logger.error(f"Error loading configuration from {path}: {e}")
            raise ValueError(f"Invalid configuration file: {e}")
    else:
        # No configuration file found, use defaults
        if detect_project:
            # Detect project type and get default configuration
            project_type, confidence, scores = detect_project_type(directory)
            config_dict = get_default_config(project_type)
            logger.info(f"No configuration file found. Using defaults for {project_type} (confidence: {confidence:.2f})")
            is_default = True
        else:
            # Use Python defaults
            config_dict = get_default_config(ProjectType.PYTHON)
            logger.info("No configuration file found. Using Python defaults")
            is_default = True
    
    # Validate configuration
    try:
        config = ConfigurationSchema(**config_dict)
    except Exception as e:
        logger.error(f"Invalid configuration: {e}")
        raise ValueError(f"Invalid configuration: {e}")
    
    return ProjectConfig(
        config=config,
        path=str(path) if path else None,
        is_default=is_default
    )


def save_config(
    config: Union[ConfigurationSchema, Dict[str, Any]],
    path: Optional[Union[str, Path]] = None,
    directory: Union[str, Path] = ".",
) -> Path:
    """
    Save configuration to a file.
    
    Args:
        config: Configuration to save
        path: Path to save the configuration to (optional)
        directory: Directory to save the configuration in (if path is not provided)
        
    Returns:
        Path to the saved configuration file
        
    Raises:
        ValueError: If the configuration is invalid
    """
    # Convert config to dict if it's a ConfigurationSchema
    if isinstance(config, ConfigurationSchema):
        config_dict = config.model_dump(exclude_none=True)
    else:
        # Validate the dictionary against the schema
        try:
            config_schema = ConfigurationSchema(**config)
            config_dict = config
        except Exception as e:
            logger.error(f"Invalid configuration: {e}")
            raise ValueError(f"Invalid configuration: {e}")
    
    # Determine the save path
    if path is None:
        directory = Path(directory).resolve()
        path = directory / CONFIG_FILENAME
    else:
        path = Path(path)
    
    # Save the configuration
    try:
        save_yaml_file(path, config_dict)
        logger.info(f"Saved configuration to {path}")
    except Exception as e:
        logger.error(f"Error saving configuration to {path}: {e}")
        raise ValueError(f"Error saving configuration: {e}")
    
    return path


def create_default_config(
    directory: Union[str, Path] = ".",
    project_type: Optional[ProjectType] = None,
    overwrite: bool = False,
) -> Path:
    """
    Create a default configuration file in the specified directory.
    
    Args:
        directory: Directory to create the configuration in
        project_type: Project type (autodetected if None)
        overwrite: Whether to overwrite an existing configuration file
        
    Returns:
        Path to the created configuration file
        
    Raises:
        FileExistsError: If the configuration file already exists and overwrite is False
    """
    directory = Path(directory).resolve()
    config_path = directory / CONFIG_FILENAME
    
    # Check if the file already exists
    if config_path.exists() and not overwrite:
        raise FileExistsError(f"Configuration file already exists: {config_path}")
    
    # Detect project type if not provided
    if project_type is None:
        project_type = detect_project_type(directory)
    
    # Get default configuration for the project type
    config_dict = get_default_config(project_type)
    
    # Save the configuration
    return save_config(config_dict, config_path)
