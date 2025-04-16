#!/usr/bin/env python3
"""
Configuration verification tool for the Practices MCP Server.

This script validates the project's configuration files against the schema,
checks for logical errors, and displays the effective configuration after
applying the hierarchical configuration system.

Copyright (c) 2025 Agentience.ai
Author: Troy Molander
License: MIT License - See LICENSE file for details

Version: 0.2.0
"""

import argparse
import logging
import os
import sys
import yaml
from pathlib import Path

from src.mcp_server_practices.config.schema import (
    ConfigurationSchema, 
    ProjectConfig,
    ProjectType,
    BranchingStrategy
)
from src.mcp_server_practices.config.loader import load_config
from src.mcp_server_practices.config.validator import validate_config, validate_file_paths
from src.mcp_server_practices.config.detector import detect_project_type


def setup_logging(level=logging.INFO):
    """
    Set up logging configuration.
    
    Args:
        level: Logging level
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )


def parse_args():
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Validate configuration files for the Practices MCP Server"
    )
    parser.add_argument(
        "-p", "--path",
        help="Path to the configuration file (defaults to .practices.yaml in current directory)",
        default=None
    )
    parser.add_argument(
        "-d", "--directory",
        help="Project directory to use (defaults to current directory)",
        default="."
    )
    parser.add_argument(
        "--no-hierarchy",
        help="Disable hierarchical configuration loading",
        action="store_true"
    )
    parser.add_argument(
        "--detect",
        help="Detect project type and show scoring details",
        action="store_true"
    )
    parser.add_argument(
        "-s", "--show-files",
        help="Show validation of referenced files",
        action="store_true"
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Enable verbose output",
        action="store_true"
    )
    parser.add_argument(
        "-q", "--quiet",
        help="Suppress all output except errors",
        action="store_true"
    )
    return parser.parse_args()


def display_config(config_schema, depth=0, hide_defaults=True):
    """
    Display configuration in a tree-like format.
    
    Args:
        config_schema: Configuration schema or dict
        depth: Indentation depth
        hide_defaults: Whether to hide default values
    """
    # Convert to dict for easier manipulation
    if hasattr(config_schema, 'model_dump'):
        config_dict = config_schema.model_dump(exclude_none=True) if hide_defaults else config_schema.model_dump()
    elif isinstance(config_schema, dict):
        config_dict = config_schema
    else:
        print(f"  {'  ' * depth}Unable to display: {type(config_schema)}")
        return
    
    # Indent string
    indent = "  " * depth
    
    # Process each key in the config
    for key, value in config_dict.items():
        if isinstance(value, dict):
            print(f"{indent}{key}:")
            display_config(value, depth + 1, hide_defaults)
        elif isinstance(value, list):
            print(f"{indent}{key}:")
            for item in value:
                if isinstance(item, dict):
                    display_config(item, depth + 1, hide_defaults)
                else:
                    print(f"{indent}  - {item}")
        else:
            print(f"{indent}{key}: {value}")


def display_hierarchical_info(project_root):
    """
    Display information about the hierarchical configuration.
    
    Args:
        project_root: Project root directory
    """
    try:
        from src.mcp_server_practices.config.hierarchy import find_hierarchical_configs
        configs = find_hierarchical_configs(project_root)
        
        if not configs:
            print("No configuration files found in hierarchy.")
            return
        
        print("\nConfiguration files in hierarchy (from root to project):")
        for i, (path, level) in enumerate(configs):
            print(f"  {i+1}. {level.capitalize()} config: {path}")
            
    except ImportError:
        print("Hierarchical configuration loading not available.")


def main():
    """Main entry point."""
    args = parse_args()
    
    # Setup logging level
    if args.quiet:
        setup_logging(logging.ERROR)
    elif args.verbose:
        setup_logging(logging.DEBUG)
    else:
        setup_logging(logging.INFO)
    
    # Get configuration path and directory
    config_path = args.path
    project_dir = Path(args.directory).resolve()
    
    if not project_dir.exists() or not project_dir.is_dir():
        print(f"Error: Directory {project_dir} does not exist or is not a directory")
        sys.exit(1)
    
    # Detect project type if requested
    if args.detect:
        try:
            project_type, confidence, scores = detect_project_type(project_dir)
            print(f"Detected project type: {project_type.value}")
            print(f"Confidence: {confidence:.2f}")
            print("\nScores by project type:")
            for pt, score in scores.items():
                print(f"  {pt.value}: {score:.2f}")
            print()
        except Exception as e:
            print(f"Error detecting project type: {e}")
    
    # Display hierarchical info if using hierarchy
    if not args.no_hierarchy:
        display_hierarchical_info(project_dir)
    
    try:
        # Load configuration
        print(f"\nLoading configuration from {project_dir}")
        project_config = load_config(
            directory=project_dir,
            config_path=config_path,
            use_hierarchy=not args.no_hierarchy
        )
        
        print(f"Using configuration from: {project_config.path or 'Default configuration'}")
        print(f"Is default: {project_config.is_default}")
        
        # Validate configuration schema
        print("\nValidating configuration schema...")
        is_valid, errors = validate_config(project_config.config)
        
        if not is_valid:
            print("Configuration validation failed:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
        
        print("Schema validation successful.")
        
        # Validate file paths if requested
        if args.show_files:
            print("\nValidating referenced files...")
            all_exist, missing = validate_file_paths(project_config.config, project_dir)
            
            if not all_exist:
                print("File validation failed - missing files:")
                for file_path in missing:
                    print(f"  - {file_path}")
                print("\nNote: Some files may be templates and not expected to exist.")
            else:
                print("All referenced files exist.")
        
        # Display effective configuration
        print("\nEffective configuration:")
        display_config(project_config.config)
        
        print("\nConfiguration validation successful!")
        sys.exit(0)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
