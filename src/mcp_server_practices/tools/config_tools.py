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
                },
                "sources": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Configuration sources (if hierarchical loading was used)"
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
        project_root = get_project_root()
        
        # Load the configuration with hierarchical sources
        try:
            from mcp_server_practices.config.hierarchy import load_hierarchical_config
            project_config, sources = load_hierarchical_config(project_root)
            source_names = [f"{i+1}. {s}" for i, s in enumerate([
                "Default configuration",
                *[f"Team config at {path}" for path, level in sources if level == "team"],
                *[f"Project config at {path}" for path, level in sources if level == "project"],
                *[f"User config at {path}" for path, level in sources if level == "user"]
            ])]
        except ImportError:
            # Fallback to simple loading
            project_config = await get_project_config()
            source_names = ["Default configuration"]
            if not project_config.is_default:
                source_names.append(f"Project config at {project_config.path}")
        
        return {
            "config": project_config.config.model_dump(),
            "is_default": project_config.is_default,
            "path": project_config.path,
            "sources": source_names
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
            
    @mcp.tool(
        name="apply_strategy_template",
        description="Apply a branching strategy template to the project configuration",
        input_schema={
            "type": "object",
            "properties": {
                "strategy": {
                    "type": "string",
                    "description": "Branching strategy to apply (gitflow, github-flow, trunk)",
                    "enum": [s.value for s in BranchingStrategy]
                },
                "customize": {
                    "type": "object",
                    "description": "Custom overrides for the template (optional)",
                    "default": None
                },
                "save": {
                    "type": "boolean",
                    "description": "Whether to save the configuration to a file",
                    "default": True
                }
            },
            "required": ["strategy"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean",
                    "description": "Whether the template was applied successfully"
                },
                "config": {
                    "type": "object",
                    "description": "Updated configuration"
                },
                "path": {
                    "type": ["string", "null"],
                    "description": "Path to the saved configuration file (if saved)"
                },
                "error": {
                    "type": ["string", "null"],
                    "description": "Error message if the operation failed"
                }
            }
        }
    )
    async def apply_strategy_template(
        strategy: str,
        customize: Optional[Dict[str, Any]] = None,
        save: bool = True
    ) -> Dict[str, Any]:
        """
        Apply a branching strategy template to the project configuration.
        
        Args:
            strategy: Branching strategy to apply
            customize: Custom overrides for the template (optional)
            save: Whether to save the configuration to a file
            
        Returns:
            Dictionary with result information
        """
        try:
            project_root = get_project_root()
            if project_root is None:
                return {
                    "success": False,
                    "config": None,
                    "path": None,
                    "error": "No project root set. Use set_working_directory first."
                }
            
            # Load current configuration
            project_config = await get_project_config()
            config_dict = project_config.config.model_dump(exclude_none=True)
            
            # Get strategy template
            try:
                strategy_enum = BranchingStrategy(strategy)
            except ValueError:
                return {
                    "success": False,
                    "config": None,
                    "path": None,
                    "error": f"Invalid branching strategy: {strategy}"
                }
            
            # Load strategy templates
            from mcp_server_practices.config.templates import get_template_for_branching_strategy
            
            # Apply strategy template
            strategy_template = get_template_for_branching_strategy(strategy_enum)
            
            # Update configuration with strategy template
            for key, value in strategy_template.items():
                if key == "branches":
                    # Merge branch configurations, preserving custom branches
                    if "branches" not in config_dict:
                        config_dict["branches"] = {}
                    
                    for branch_type, branch_config in value.items():
                        config_dict["branches"][branch_type] = branch_config
                else:
                    # Other keys directly override
                    config_dict[key] = value
            
            # Apply custom overrides if provided
            if customize:
                from mcp_server_practices.config.hierarchy import _merge_dicts
                _merge_dicts(config_dict, customize)
            
            # Create updated configuration
            updated_config = ConfigurationSchema(**config_dict)
            
            # Save configuration if requested
            path = None
            if save:
                path = save_config(
                    config=updated_config,
                    directory=project_root
                )
            
            return {
                "success": True,
                "config": updated_config.model_dump(exclude_none=True),
                "path": str(path) if path else None,
                "error": None
            }
        except Exception as e:
            logger.error(f"Error applying strategy template: {e}")
            return {
                "success": False,
                "config": None,
                "path": None,
                "error": f"Error applying strategy template: {str(e)}"
            }
            
    @mcp.tool(
        name="create_user_config",
        description="Create or update user-specific configuration overrides",
        input_schema={
            "type": "object",
            "properties": {
                "overrides": {
                    "type": "object",
                    "description": "Configuration overrides"
                }
            },
            "required": ["overrides"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean",
                    "description": "Whether the user configuration was created successfully"
                },
                "path": {
                    "type": ["string", "null"],
                    "description": "Path to the created user configuration file"
                },
                "error": {
                    "type": ["string", "null"],
                    "description": "Error message if the creation failed"
                }
            }
        }
    )
    async def create_user_config_tool(overrides: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update user-specific configuration overrides.
        
        Args:
            overrides: Configuration overrides
            
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
            
            # Create user config
            from mcp_server_practices.config.hierarchy import create_user_config
            user_config_path = create_user_config(project_root, overrides)
            
            return {
                "success": True,
                "path": str(user_config_path),
                "error": None
            }
        except Exception as e:
            logger.error(f"Error creating user configuration: {e}")
            return {
                "success": False,
                "path": None,
                "error": f"Error creating user configuration: {str(e)}"
            }
