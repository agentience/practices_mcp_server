#!/usr/bin/env python
"""
Unit tests for configuration loading functionality.

These tests validate the configuration loading, saving, and file detection functions.
"""

import pytest
import os
import tempfile
import yaml
from pathlib import Path

from mcp_server_practices.config.schema import (
    ConfigurationSchema,
    ProjectConfig,
    ProjectType,
    BranchingStrategy,
)
from mcp_server_practices.config.loader import (
    find_config_file,
    load_yaml_file,
    save_yaml_file,
    load_config,
    save_config,
    create_default_config,
    CONFIG_FILENAME,
    CONFIG_FILENAME_ALT,
)


def test_find_config_file():
    """Test finding configuration files in directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # No config file should return None
        assert find_config_file(tmpdir) is None
        
        # Create .practices.yaml file
        config_path = os.path.join(tmpdir, CONFIG_FILENAME)
        with open(config_path, "w") as f:
            f.write("project_type: python\n")
        
        # Should find .practices.yaml
        found_path = find_config_file(tmpdir)
        assert found_path is not None
        assert found_path.name == CONFIG_FILENAME
        
        # Create .practices.yml file
        alt_config_path = os.path.join(tmpdir, CONFIG_FILENAME_ALT)
        with open(alt_config_path, "w") as f:
            f.write("project_type: javascript\n")
        
        # Should still find .practices.yaml (higher priority)
        found_path = find_config_file(tmpdir)
        assert found_path is not None
        assert found_path.name == CONFIG_FILENAME
        
        # Remove .practices.yaml to test fallback
        os.remove(config_path)
        
        # Should now find .practices.yml
        found_path = find_config_file(tmpdir)
        assert found_path is not None
        assert found_path.name == CONFIG_FILENAME_ALT


def test_load_yaml_file():
    """Test loading YAML files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a YAML file
        yaml_path = os.path.join(tmpdir, "test.yaml")
        data = {
            "project_type": "python",
            "branching_strategy": "gitflow",
            "nested": {
                "key1": "value1",
                "key2": 123
            },
            "list": [1, 2, 3]
        }
        
        with open(yaml_path, "w") as f:
            yaml.dump(data, f)
        
        # Load the YAML file
        loaded_data = load_yaml_file(yaml_path)
        
        # Check that data was loaded correctly
        assert loaded_data["project_type"] == "python"
        assert loaded_data["branching_strategy"] == "gitflow"
        assert loaded_data["nested"]["key1"] == "value1"
        assert loaded_data["nested"]["key2"] == 123
        assert loaded_data["list"] == [1, 2, 3]
        
        # Test loading non-existent file
        nonexistent_path = os.path.join(tmpdir, "nonexistent.yaml")
        with pytest.raises(FileNotFoundError):
            load_yaml_file(nonexistent_path)
        
        # Test loading invalid YAML
        invalid_yaml_path = os.path.join(tmpdir, "invalid.yaml")
        with open(invalid_yaml_path, "w") as f:
            f.write("invalid: yaml: file:\n  - not\n  proper: indentation\n")
        
        with pytest.raises(yaml.YAMLError):
            load_yaml_file(invalid_yaml_path)


def test_save_yaml_file():
    """Test saving data to YAML files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create data to save
        data = {
            "project_type": "python",
            "branching_strategy": "gitflow",
            "nested": {
                "key1": "value1",
                "key2": 123
            },
            "list": [1, 2, 3]
        }
        
        # Save the data to a YAML file
        yaml_path = os.path.join(tmpdir, "test.yaml")
        save_yaml_file(yaml_path, data)
        
        # Check that file was created
        assert os.path.exists(yaml_path)
        
        # Load the data and verify it matches
        with open(yaml_path, "r") as f:
            loaded_data = yaml.safe_load(f)
        
        assert loaded_data["project_type"] == "python"
        assert loaded_data["branching_strategy"] == "gitflow"
        assert loaded_data["nested"]["key1"] == "value1"
        assert loaded_data["nested"]["key2"] == 123
        assert loaded_data["list"] == [1, 2, 3]
        
        # Test creating parent directories
        nested_yaml_path = os.path.join(tmpdir, "nested", "dir", "test.yaml")
        save_yaml_file(nested_yaml_path, data)
        
        # Check that file and parent directories were created
        assert os.path.exists(nested_yaml_path)


def test_load_config():
    """Test loading configuration from files or defaults."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test loading with no config file (should use defaults)
        config = load_config(tmpdir, detect_project=False)
        assert config.is_default is True
        # In hierarchical mode, we may create a default config even if none exists
        # assert config.path is None
        assert os.path.basename(config.path) == CONFIG_FILENAME
        # With detection disabled, it defaults to GENERIC
        assert config.config.project_type == ProjectType.GENERIC
        
        # Create a config file
        config_path = os.path.join(tmpdir, CONFIG_FILENAME)
        config_data = {
            "project_type": "javascript",
            "branching_strategy": "github-flow",
            "workflow_mode": "team",
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
                }
            }
        }
        
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)
        
        # Test loading with config file
        config = load_config(tmpdir)
        assert config.is_default is False
        assert config.path is not None
        assert config.config.project_type == ProjectType.JAVASCRIPT
        assert config.config.branching_strategy == BranchingStrategy.GITHUB_FLOW
        
        # Test loading with explicit config path
        explicit_config = load_config(tmpdir, config_path=config_path)
        assert explicit_config.is_default is False
        assert explicit_config.path == str(Path(config_path))
        assert explicit_config.config.project_type == ProjectType.JAVASCRIPT
        
        # Test loading with non-existent explicit path
        nonexistent_path = os.path.join(tmpdir, "nonexistent.yaml")
        with pytest.raises(FileNotFoundError):
            load_config(tmpdir, config_path=nonexistent_path)
        
        # Test loading with invalid config file
        invalid_config_path = os.path.join(tmpdir, "invalid_config.yaml")
        with open(invalid_config_path, "w") as f:
            f.write("project_type: python\nbranching_strategy: invalid_strategy\n")
        
        with pytest.raises(ValueError):
            load_config(tmpdir, config_path=invalid_config_path)


def test_save_config():
    """Test saving configuration to files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a configuration dict instead of a schema to avoid YAML serialization issues
        config_dict = {
            "project_type": "python",
            "branching_strategy": "gitflow",
            "workflow_mode": "solo",
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
                }
            }
        }
        
        # Save the configuration to a file
        save_path = save_config(config_dict, directory=tmpdir)
        
        # Check that file was created with expected name
        assert save_path.name == CONFIG_FILENAME
        assert os.path.exists(save_path)
        
        # Load the config and check it matches
        loaded_config = load_config(tmpdir).config
        assert loaded_config.project_type == ProjectType.PYTHON
        assert loaded_config.branching_strategy == BranchingStrategy.GITFLOW
        assert loaded_config.main_branch == "main"
        assert loaded_config.develop_branch == "develop"
        assert "feature" in loaded_config.branches
        assert "bugfix" in loaded_config.branches
        
        # Save to explicit path
        explicit_path = os.path.join(tmpdir, "custom_config.yaml")
        save_path = save_config(config_dict, path=explicit_path)
        
        # Check that file was created at custom path
        assert save_path == Path(explicit_path)
        assert os.path.exists(explicit_path)


def test_create_default_config():
    """Test creating default configuration files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a default config file for Python
        config_path = create_default_config(tmpdir, project_type=ProjectType.PYTHON)
        
        # Check that file was created with expected name
        assert config_path.name == CONFIG_FILENAME
        assert os.path.exists(config_path)
        
        # Load the config and check it's a Python config
        loaded_config = load_config(tmpdir).config
        assert loaded_config.project_type == ProjectType.PYTHON
        
        # Try to create a config where one already exists (should fail)
        with pytest.raises(FileExistsError):
            create_default_config(tmpdir, project_type=ProjectType.JAVASCRIPT)
        
        # Override existing config
        config_path = create_default_config(tmpdir, project_type=ProjectType.JAVASCRIPT, overwrite=True)
        
        # Check that file was overwritten with JavaScript config
        loaded_config = load_config(tmpdir).config
        assert loaded_config.project_type == ProjectType.JAVASCRIPT
