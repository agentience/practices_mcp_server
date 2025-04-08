#!/usr/bin/env python
"""
Unit tests for project type detection.

These tests validate the project type detection and default configuration generation.
"""

import pytest
from pathlib import Path
import tempfile
import os
import shutil

from mcp_server_practices.config.schema import (
    ProjectType,
    BranchingStrategy,
    WorkflowMode,
)
from mcp_server_practices.config.detector import (
    detect_project_type,
    detect_branching_strategy,
    get_default_config,
    get_default_gitflow_config,
    get_default_github_flow_config,
    get_default_trunk_config,
    PROJECT_TYPE_INDICATORS,
)


def test_detect_project_type():
    """Test detection of project type based on files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test Python project detection
        python_dir = os.path.join(tmpdir, "python_project")
        os.makedirs(python_dir, exist_ok=True)
        os.makedirs(os.path.join(python_dir, "src"), exist_ok=True)
        
        # Create Python files
        with open(os.path.join(python_dir, "pyproject.toml"), "w") as f:
            f.write("[project]\nname = \"test-project\"\n")
        
        with open(os.path.join(python_dir, "src", "__init__.py"), "w") as f:
            f.write("# Python module\n")
            
        with open(os.path.join(python_dir, "main.py"), "w") as f:
            f.write("# Main module\n")
            
        # Detect project type
        detected_type = detect_project_type(python_dir)
        assert detected_type == ProjectType.PYTHON
        
        # Test JavaScript project detection
        js_dir = os.path.join(tmpdir, "js_project")
        os.makedirs(js_dir, exist_ok=True)
        
        # Create JavaScript files
        with open(os.path.join(js_dir, "package.json"), "w") as f:
            f.write('{"name": "test-project", "version": "1.0.0"}\n')
        
        with open(os.path.join(js_dir, "index.js"), "w") as f:
            f.write("// Main module\n")
            
        with open(os.path.join(js_dir, "app.js"), "w") as f:
            f.write("// App module\n")
            
        with open(os.path.join(js_dir, "utils.js"), "w") as f:
            f.write("// Utils module\n")
            
        # Detect project type
        detected_type = detect_project_type(js_dir)
        assert detected_type == ProjectType.JAVASCRIPT
        
        # Test TypeScript project detection
        ts_dir = os.path.join(tmpdir, "ts_project")
        os.makedirs(ts_dir, exist_ok=True)
        
        # Create TypeScript files
        with open(os.path.join(ts_dir, "tsconfig.json"), "w") as f:
            f.write('{"compilerOptions": {}}\n')
        
        with open(os.path.join(ts_dir, "index.ts"), "w") as f:
            f.write("// Main module\n")
            
        with open(os.path.join(ts_dir, "app.ts"), "w") as f:
            f.write("// App module\n")
            
        with open(os.path.join(ts_dir, "utils.ts"), "w") as f:
            f.write("// Utils module\n")
            
        # Detect project type
        detected_type = detect_project_type(ts_dir)
        assert detected_type == ProjectType.TYPESCRIPT
        
        # Test empty directory
        empty_dir = os.path.join(tmpdir, "empty_project")
        os.makedirs(empty_dir, exist_ok=True)
        
        # Detect project type
        detected_type = detect_project_type(empty_dir)
        assert detected_type == ProjectType.GENERIC


def test_get_default_config():
    """Test generation of default configuration for project types."""
    # Test Python project configuration
    config = get_default_config(ProjectType.PYTHON)
    assert config["project_type"] == "python"
    assert config["branching_strategy"] == "gitflow"
    assert config["workflow_mode"] == "solo"
    assert config["main_branch"] == "main"
    assert config["develop_branch"] == "develop"
    assert "feature" in config["branches"]
    assert "version" in config
    assert config["version"]["use_bumpversion"] is True
    assert len(config["version"]["files"]) > 0
    
    # Test JavaScript project configuration
    config = get_default_config(ProjectType.JAVASCRIPT)
    assert config["project_type"] == "javascript"
    assert "version" in config
    assert config["version"]["use_bumpversion"] is False
    assert len(config["version"]["files"]) > 0
    assert config["version"]["files"][0]["path"] == "package.json"
    
    # Test TypeScript project configuration
    config = get_default_config(ProjectType.TYPESCRIPT)
    assert config["project_type"] == "typescript"
    assert "version" in config
    assert config["version"]["use_bumpversion"] is False
    assert len(config["version"]["files"]) > 0
    assert config["version"]["files"][0]["path"] == "package.json"
    
    # Test generic project configuration
    config = get_default_config(ProjectType.GENERIC)
    assert config["project_type"] == "generic"
    assert "version" in config
    assert len(config["version"]["files"]) > 0
    assert config["version"]["files"][0]["path"] == "VERSION"


def test_version_configs_by_project_type():
    """Test that version configurations match project types."""
    python_config = get_default_config(ProjectType.PYTHON)
    js_config = get_default_config(ProjectType.JAVASCRIPT)
    java_config = get_default_config(ProjectType.JAVA)
    
    # Python should use bumpversion and have Python-specific files
    assert python_config["version"]["use_bumpversion"] is True
    assert any("__init__.py" in file["path"] for file in python_config["version"]["files"])
    assert any("pyproject.toml" in file["path"] for file in python_config["version"]["files"])
    
    # JavaScript should use package.json
    assert js_config["version"]["use_bumpversion"] is False
    assert any("package.json" in file["path"] for file in js_config["version"]["files"])
    
    # Java should use pom.xml
    assert java_config["version"]["use_bumpversion"] is False
    assert any("pom.xml" in file["path"] for file in java_config["version"]["files"])


def test_branching_strategies():
    """Test different branching strategies."""
    # Start with a Python project but use different branching strategies
    gitflow_config = get_default_gitflow_config()
    gitflow_config["project_type"] = ProjectType.PYTHON.value
    
    github_flow_config = get_default_github_flow_config()
    github_flow_config["project_type"] = ProjectType.PYTHON.value
    
    trunk_config = get_default_trunk_config()
    trunk_config["project_type"] = ProjectType.PYTHON.value
    
    # GitFlow should have develop branch
    assert gitflow_config["develop_branch"] == "develop"
    assert "release" in gitflow_config["branches"]
    assert "hotfix" in gitflow_config["branches"]
    
    # GitHub Flow has everything based on main
    assert github_flow_config["main_branch"] == "main"
    assert "feature" in github_flow_config["branches"]
    assert github_flow_config["branches"]["feature"]["base"] == "main"
    
    # Trunk-based has everything based on main
    assert trunk_config["main_branch"] == "main"
    assert "feature" in trunk_config["branches"]
    assert trunk_config["branches"]["feature"]["base"] == "main"
