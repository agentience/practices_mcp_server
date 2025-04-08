#!/usr/bin/env python
"""
Configuration tools for the Practices MCP Server.

This module provides tools for working with project configurations.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

from mcp.server import FastMCP

from mcp_server_practices.config.schema import (
    ConfigurationSchema,
    ProjectConfig,
    ProjectType,
    BranchingStrategy,
)
from mcp_server_practices.config.loader import (
    load_config,
    save_config,
    create_default_config,
)
from mcp_server_practices.config.validator import (
    validate_config,
    validate_file_paths,
)
from mcp_server_practices.config.detector import (
    detect_project_type,
    get_default_config,
)
from mcp_server_practices.utils.global_context import get_project_root

logger = logging.getLogger(__name__)


async def get_project_config() -> ProjectConfig:
    """
    Get the current project configuration.
    
    This function loads the configuration from the project root, or
    uses a default configuration if none is found.
    
    Returns:
        ProjectConfig: The current project configuration
    """
    project_root = get_project_root()
    if project_root is None:
        logger.warning("No project root set. Using default configuration.")
        return ProjectConfig(
            config=ConfigurationSchema(
                project_type=ProjectType.PYTHON,
                branching_strategy=BranchingStrategy.GITFLOW,
                workflow_mode="solo",
                main_branch="main",
                develop_branch="develop",
                branches={
                    "feature": {
                        "pattern": "^feature/([A-Z]+-\\d+)-(.+)$",
                        "base": "develop",
                        "version_bump": None
                    }
                }
            ),
            path=None,
            is_default=True
        )
    
    return load_config(project_root)


def register_tools(mcp: FastMCP, config: Dict[str, Any]):
    """
    Register configuration tools with the MCP server.
    
    Args:
        mcp: MCP server instance
        config: Server configuration
    """
    @mcp.tool(
        name="get_config",
        description="Get the current project configuration",
        output_schema={
            "type": "object",
            "properties": {
                "config": {
                    "type": "object",
                    "description": "Project configuration"
                },
                "is_default": {
                    "type": "boolean",
                    "description": "Whether this is a default configuration"
                },
                "path": {
                    "type": ["string", "null"],
                    "description": "Path to the configuration file, or null if default"
                }
            }
        }
    )
    async def get_config() -> Dict[str, Any]:
        """
        Get the current project configuration.
        
        Returns:
            Dictionary with project configuration
        """
        project_config = await get_project_config()
        return {
            "config": project_config.config.model_dump(),
            "is_default": project_config.is_default,
            "path": project_config.path
        }

    @mcp.tool(
        name="create_config",
        description="Create a default configuration file",
        input_schema={
            "type": "object",
            "properties": {
                "project_type": {
                    "type": "string",
                    "description": "Project type (python, javascript, typescript, java, csharp, go, rust, generic)",
                    "enum": [pt.value for pt in ProjectType]
                },
                "overwrite": {
                    "type": "boolean",
                    "description": "Whether to overwrite existing configuration",
                    "default": False
                }
            }
        },
        output_schema={
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean",
                    "description": "Whether the configuration was created successfully"
                },
                "path": {
                    "type": ["string", "null"],
                    "description": "Path to the created configuration file"
                },
                "error": {
                    "type": ["string", "null"],
                    "description": "Error message if the creation failed"
                }
            }
        }
    )
    async def create_config(project_type: Optional[str] = None, overwrite: bool = False) -> Dict[str, Any]:
        """
        Create a default configuration file in the project root.
        
        Args:
            project_type: Project type (optional, auto-detected if not provided)
            overwrite: Whether to overwrite existing configuration
            
        Returns:
            Dictionary with result information
        """
        try:
            project_root = get_project_root()
            if project_root is None:
                return {
                    "success": False,
                    "path": None,
                    "error": "No project root set. Use set_working_directory first."
                }
            
            # Convert string project_type to enum
            pt = None
            if project_type is not None:
                try:
                    pt = ProjectType(project_type)
                except ValueError:
                    return {
                        "success": False,
                        "path": None,
                        "error": f"Invalid project type: {project_type}"
                    }
            
            # Create default configuration
            config_path = create_default_config(
                directory=project_root,
                project_type=pt,
                overwrite=overwrite
            )
            
            return {
                "success": True,
                "path": str(config_path),
                "error": None
            }
        except FileExistsError:
            return {
                "success": False,
                "path": None,
                "error": "Configuration file already exists. Use overwrite=True to overwrite."
            }
        except Exception as e:
            logger.error(f"Error creating configuration: {e}")
            return {
                "success": False,
                "path": None,
                "error": f"Error creating configuration: {str(e)}"
            }

    @mcp.tool(
        name="validate_config",
        description="Validate the current project configuration",
        output_schema={
            "type": "object",
            "properties": {
                "valid": {
                    "type": "boolean",
                    "description": "Whether the configuration is valid"
                },
                "errors": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List of validation errors"
                },
                "missing_files": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List of missing files referenced in configuration"
                }
            }
        }
    )
    async def validate_config_tool() -> Dict[str, Any]:
        """
        Validate the current project configuration.
        
        Returns:
            Dictionary with validation results
        """
        try:
            project_root = get_project_root()
            if project_root is None:
                return {
                    "valid": False,
                    "errors": ["No project root set. Use set_working_directory first."],
                    "missing_files": []
                }
            
            # Load current configuration
            project_config = await get_project_config()
            
            # Validate configuration against schema
            is_valid, errors = validate_config(project_config.config)
            
            # Validate file paths if configuration is valid
            missing_files = []
            if is_valid:
                all_exist, missing = validate_file_paths(project_config.config, project_root)
                if not all_exist:
                    is_valid = False
                    missing_files = missing
            
            return {
                "valid": is_valid,
                "errors": errors,
                "missing_files": missing_files
            }
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return {
                "valid": False,
                "errors": [f"Error validating configuration: {str(e)}"],
                "missing_files": []
            }

    @mcp.tool(
        name="detect_project_type",
        description="Detect the project type based on files in the directory",
        output_schema={
            "type": "object",
            "properties": {
                "project_type": {
                    "type": "string",
                    "description": "Detected project type"
                },
                "confidence": {
                    "type": "string",
                    "description": "Confidence level (high, medium, low)"
                },
                "details": {
                    "type": "object",
                    "description": "Details about the detection"
                }
            }
        }
    )
    async def detect_project_type_tool() -> Dict[str, Any]:
        """
        Detect the project type based on files in the directory.
        
        Returns:
            Dictionary with detected project type
        """
        try:
            project_root = get_project_root()
            if project_root is None:
                return {
                    "project_type": "generic",
                    "confidence": "low",
                    "details": {
                        "error": "No project root set. Use set_working_directory first."
                    }
                }
            
            # Detect project type
            detected_type = detect_project_type(project_root)
            
            # Determine confidence level based on detected type
            confidence = "high" if detected_type != ProjectType.GENERIC else "low"
            
            return {
                "project_type": detected_type.value,
                "confidence": confidence,
                "details": {
                    "indicators": {
                        "pyproject.toml": os.path.exists(os.path.join(project_root, "pyproject.toml")),
                        "setup.py": os.path.exists(os.path.join(project_root, "setup.py")),
                        "package.json": os.path.exists(os.path.join(project_root, "package.json")),
                        "tsconfig.json": os.path.exists(os.path.join(project_root, "tsconfig.json")),
                        "pom.xml": os.path.exists(os.path.join(project_root, "pom.xml")),
                        "build.gradle": os.path.exists(os.path.join(project_root, "build.gradle")),
                        "go.mod": os.path.exists(os.path.join(project_root, "go.mod")),
                        "Cargo.toml": os.path.exists(os.path.join(project_root, "Cargo.toml")),
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error detecting project type: {e}")
            return {
                "project_type": "generic",
                "confidence": "low",
                "details": {
                    "error": f"Error detecting project type: {str(e)}"
                }
            }

    @mcp.tool(
        name="save_config",
        description="Save a configuration to a file",
        input_schema={
            "type": "object",
            "properties": {
                "config": {
                    "type": "object",
                    "description": "Configuration to save"
                },
                "path": {
                    "type": "string",
                    "description": "Path to save the configuration to (optional)",
                    "default": None
                }
            },
            "required": ["config"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean",
                    "description": "Whether the configuration was saved successfully"
                },
                "path": {
                    "type": ["string", "null"],
                    "description": "Path to the saved configuration file"
                },
                "error": {
                    "type": ["string", "null"],
                    "description": "Error message if the save failed"
                }
            }
        }
    )
    async def save_config_tool(config: Dict[str, Any], path: Optional[str] = None) -> Dict[str, Any]:
        """
        Save a configuration to a file.
        
        Args:
            config: Configuration to save
            path: Path to save the configuration to (optional)
            
        Returns:
            Dictionary with result information
        """
        try:
            project_root = get_project_root()
            if project_root is None:
                return {
                    "success": False,
                    "path": None,
                    "error": "No project root set. Use set_working_directory first."
                }
            
            # Validate configuration before saving
            try:
                config_schema = ConfigurationSchema(**config)
            except Exception as e:
                return {
                    "success": False,
                    "path": None,
                    "error": f"Invalid configuration: {str(e)}"
                }
            
            # Save configuration
            save_path = save_config(
                config=config_schema,
                path=path,
                directory=project_root
            )
            
            return {
                "success": True,
                "path": str(save_path),
                "error": None
            }
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return {
                "success": False,
                "path": None,
                "error": f"Error saving configuration: {str(e)}"
            }
