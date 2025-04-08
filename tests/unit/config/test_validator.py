#!/usr/bin/env python
"""
Unit tests for configuration validation.

These tests validate the configuration validation functions.
"""

import pytest
from pathlib import Path
import tempfile
import os

from mcp_server_practices.config.schema import (
    ConfigurationSchema,
    ProjectConfig,
    ProjectType,
    BranchingStrategy,
    WorkflowMode,
    BranchConfig,
)
from mcp_server_practices.config.validator import (
    validate_config,
    _validate_branch_configs,
    _validate_version_configs,
    _validate_jira_configs,
    _validate_github_configs,
    validate_file_paths,
)


def test_validate_config():
    """Test the validate_config function."""
    # Valid configuration with all required branches for GitFlow
    valid_config = ConfigurationSchema(
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
                version_bump="patch"
            ),
            "release": BranchConfig(
                pattern="^release/(\\d+\\.\\d+\\.\\d+(?:-[a-zA-Z0-9.]+)?)(?:-(.+))?$",
                base="develop",
                target=["main", "develop"],
                version_bump="minor"
            )
        },
        version={
            "files": [
                {
                    "path": "src/package/__init__.py",
                    "pattern": "__version__ = \"(\\d+\\.\\d+\\.\\d+)\""
                }
            ],
            "use_bumpversion": True,
            "bumpversion_config": ".bumpversion.cfg"
        }
    )
    
    is_valid, errors = validate_config(valid_config)
    assert is_valid is True
    assert len(errors) == 0
    
    # Invalid configuration (missing required branches for GitFlow)
    invalid_config = ConfigurationSchema(
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
            ),
            # Missing bugfix, hotfix, and release branches required for GitFlow
        },
        version={
            "files": [
                {
                    "path": "src/package/__init__.py",
                    "pattern": "__version__ = \"(\\d+\\.\\d+\\.\\d+)\""
                }
            ],
            "use_bumpversion": True,
            "bumpversion_config": ".bumpversion.cfg"
        }
    )
    
    is_valid, errors = validate_config(invalid_config)
    assert is_valid is False
    assert len(errors) > 0
    assert any("GitFlow strategy requires" in error for error in errors)


def test_validate_branch_configs():
    """Test validation of branch configurations."""
    # Valid configuration for GitFlow
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
                version_bump="patch"
            ),
            "release": BranchConfig(
                pattern="^release/(\\d+\\.\\d+\\.\\d+(?:-[a-zA-Z0-9.]+)?)(?:-(.+))?$",
                base="develop",
                target=["main", "develop"],
                version_bump="minor"
            )
        }
    )
    
    errors = _validate_branch_configs(config)
    assert len(errors) == 0
    
    # Missing required branch type for GitFlow
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
            ),
            # Missing bugfix
            # Missing hotfix
            # Missing release
        }
    )
    
    errors = _validate_branch_configs(config)
    assert len(errors) > 0
    assert any("GitFlow strategy requires 'bugfix'" in error for error in errors)
    assert any("GitFlow strategy requires 'hotfix'" in error for error in errors)
    assert any("GitFlow strategy requires 'release'" in error for error in errors)
    
    # Invalid target branch
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
            ),
            "hotfix": BranchConfig(
                pattern="^hotfix/(\\d+\\.\\d+\\.\\d+(?:-[a-zA-Z0-9.]+)?)-(.+)$",
                base="main",
                target=["main", "staging"],  # 'staging' is not a configured branch
                version_bump="patch"
            )
        }
    )
    
    errors = _validate_branch_configs(config)
    assert len(errors) > 0
    assert any("Target branch 'staging'" in error for error in errors)


def test_validate_version_configs():
    """Test validation of version configurations."""
    # Valid configuration
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
        },
        version={
            "files": [
                {
                    "path": "src/package/__init__.py",
                    "pattern": "__version__ = \"(\\d+\\.\\d+\\.\\d+)\""
                }
            ],
            "use_bumpversion": True,
            "bumpversion_config": ".bumpversion.cfg"
        }
    )
    
    errors = _validate_version_configs(config)
    assert len(errors) == 0
    
    # Test with no version files directly through validator function
    # Note: We don't create a full ConfigurationSchema because it has built-in validation
    # that requires at least one file entry
    from mcp_server_practices.config.schema import VersionConfig, VersionFileConfig
    
    # Create a version config with an empty files list
    version_config = VersionConfig(
        files=[],  # Empty files list
        use_bumpversion=True,
        bumpversion_config=".bumpversion.cfg"
    )
    
    # Create a partial config-like object just for testing
    test_config = type('TestConfig', (), {'version': version_config})()
    
    # Test the validator function directly
    errors = _validate_version_configs(test_config)
    assert len(errors) > 0
    assert any("at least one file" in error for error in errors)


def test_validate_jira_configs():
    """Test validation of Jira configurations."""
    # Valid configuration
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
        },
        jira={
            "enabled": True,
            "project_key": "PMS",
            "transition_to_in_progress": True,
            "update_on_pr_creation": True
        }
    )
    
    errors = _validate_jira_configs(config)
    assert len(errors) == 0
    
    # No project key specified
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
        },
        jira={
            "enabled": True,
            "project_key": "",  # Empty project key
            "transition_to_in_progress": True,
            "update_on_pr_creation": True
        }
    )
    
    errors = _validate_jira_configs(config)
    assert len(errors) > 0
    assert any("project_key" in error for error in errors)


def test_validate_file_paths():
    """Test validation of file paths in configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create a more explicit directory structure
        package_dir = tmpdir_path / "package"
        package_dir.mkdir(exist_ok=True)
        
        # Create test files
        init_file = package_dir / "__init__.py"
        with open(init_file, "w") as f:
            f.write('__version__ = "0.1.0"\n')
        
        bumpversion_file = tmpdir_path / ".bumpversion.cfg"
        with open(bumpversion_file, "w") as f:
            f.write("[bumpversion]\ncurrent_version = 0.1.0\n")
                
        # Create a changelog file
        changelog_file = tmpdir_path / "CHANGELOG.md"
        with open(changelog_file, "w") as f:
            f.write("# Changelog\n\n## 0.1.0\n- Initial release\n")
        
        # Verify files were created successfully
        assert init_file.exists(), f"Failed to create {init_file}"
        assert bumpversion_file.exists(), f"Failed to create {bumpversion_file}"
        assert changelog_file.exists(), f"Failed to create {changelog_file}"
        
        # Print the directory structure for debugging
        print(f"Files in {tmpdir_path}:")
        for item in tmpdir_path.glob("**/*"):
            if item.is_file():
                print(f"  {item.relative_to(tmpdir_path)}")
        
        # Valid configuration with existing files
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
            },
            version={
                "files": [
                    {
                        "path": "package/__init__.py",
                        "pattern": "__version__ = \"(\\d+\\.\\d+\\.\\d+)\""
                    }
                ],
                "use_bumpversion": True,
                "bumpversion_config": ".bumpversion.cfg",
                "changelog": "CHANGELOG.md"
            }
        )
        
        all_exist, missing_files = validate_file_paths(config, tmpdir)
        assert all_exist is True, f"Missing files: {missing_files}"
        assert len(missing_files) == 0
        
        # Configuration with missing files
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
            },
            version={
                "files": [
                    {
                        "path": "nonexistent_file.py",
                        "pattern": "__version__ = \"(\\d+\\.\\d+\\.\\d+)\""
                    }
                ],
                "use_bumpversion": True,
                "bumpversion_config": "nonexistent_config.cfg"
            }
        )
        
        all_exist, missing_files = validate_file_paths(config, tmpdir)
        assert all_exist is False
        assert len(missing_files) == 2
        assert "nonexistent_file.py" in missing_files
        assert "nonexistent_config.cfg" in missing_files
        
        # Template placeholders should be skipped
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
            },
            version={
                "files": [
                    {
                        "path": "src/__project__/__init__.py",  # Template path
                        "pattern": "__version__ = \"(\\d+\\.\\d+\\.\\d+)\""
                    }
                ],
                "use_bumpversion": True,
                "bumpversion_config": ".bumpversion.cfg"
            }
        )
        
        all_exist, missing_files = validate_file_paths(config, tmpdir)
        assert all_exist is True  # Special template markers shouldn't fail validation
        assert len(missing_files) == 0
