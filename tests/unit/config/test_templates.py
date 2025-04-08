#!/usr/bin/env python
"""
Unit tests for configuration templates.

These tests validate the configuration templates for different project types
and branching strategies.
"""

import pytest
from typing import Dict, Any, List

from mcp_server_practices.config.schema import (
    ProjectType,
    BranchingStrategy,
)
from mcp_server_practices.config.templates import (
    get_template_for_project_type,
    get_template_for_branching_strategy,
    get_pr_template,
    merge_templates,
    PROJECT_TYPE_TEMPLATES,
    BRANCHING_STRATEGY_TEMPLATES,
    PR_TEMPLATES,
)


def test_get_template_for_project_type():
    """Test retrieving templates for specific project types."""
    # Test Python template
    python_template = get_template_for_project_type(ProjectType.PYTHON)
    assert "version" in python_template
    assert python_template["version"]["use_bumpversion"] is True
    assert any("__init__.py" in file["path"] for file in python_template["version"]["files"])
    
    # Test JavaScript template
    js_template = get_template_for_project_type(ProjectType.JAVASCRIPT)
    assert "version" in js_template
    assert js_template["version"]["use_bumpversion"] is False
    assert any("package.json" in file["path"] for file in js_template["version"]["files"])
    
    # Test Generic template (fallback)
    generic_template = get_template_for_project_type(ProjectType.GENERIC)
    assert "version" in generic_template
    assert any("VERSION" in file["path"] for file in generic_template["version"]["files"])
    
    # Test each supported project type has a template
    for project_type in ProjectType:
        template = get_template_for_project_type(project_type)
        assert template is not None


def test_get_template_for_branching_strategy():
    """Test retrieving templates for specific branching strategies."""
    # Test GitFlow template
    gitflow_template = get_template_for_branching_strategy(BranchingStrategy.GITFLOW)
    assert gitflow_template["branching_strategy"] == "gitflow"
    assert gitflow_template["main_branch"] == "main"
    assert gitflow_template["develop_branch"] == "develop"
    assert "feature" in gitflow_template["branches"]
    assert "bugfix" in gitflow_template["branches"]
    assert "release" in gitflow_template["branches"]
    assert "hotfix" in gitflow_template["branches"]
    
    # Test GitHub Flow template
    github_flow_template = get_template_for_branching_strategy(BranchingStrategy.GITHUB_FLOW)
    assert github_flow_template["branching_strategy"] == "github-flow"
    assert github_flow_template["main_branch"] == "main"
    assert "develop_branch" not in github_flow_template  # GitHub Flow doesn't use develop branch
    assert "feature" in github_flow_template["branches"]
    assert github_flow_template["branches"]["feature"]["base"] == "main"
    
    # Test Trunk-Based template
    trunk_template = get_template_for_branching_strategy(BranchingStrategy.TRUNK)
    assert trunk_template["branching_strategy"] == "trunk"
    assert trunk_template["main_branch"] == "main"
    assert "feature" in trunk_template["branches"]
    assert trunk_template["branches"]["feature"]["base"] == "main"
    
    # Test each supported strategy has a template
    for strategy in BranchingStrategy:
        template = get_template_for_branching_strategy(strategy)
        assert template is not None
        assert template["branching_strategy"] == strategy.value


def test_get_pr_template():
    """Test retrieving PR templates for different branch types."""
    # Test feature PR template
    feature_template = get_pr_template("feature")
    assert feature_template is not None
    assert "{ticket_id}" in feature_template
    assert "{description}" in feature_template
    
    # Test bugfix PR template
    bugfix_template = get_pr_template("bugfix")
    assert bugfix_template is not None
    assert "Fix" in bugfix_template
    assert "Root Cause" in bugfix_template
    
    # Test release PR template
    release_template = get_pr_template("release")
    assert release_template is not None
    assert "Release {version}" in release_template
    assert "CHANGELOG.md" in release_template
    
    # Test hotfix PR template
    hotfix_template = get_pr_template("hotfix")
    assert hotfix_template is not None
    assert "Hotfix {version}" in hotfix_template
    assert "Deployment Plan" in hotfix_template
    
    # Test nonexistent PR template
    nonexistent_template = get_pr_template("nonexistent")
    assert nonexistent_template is None


def test_merge_templates():
    """Test merging multiple templates into a single configuration."""
    # Create template fragments
    template1 = {
        "key1": "value1",
        "key2": {
            "nested1": "nested1",
            "nested2": "nested2"
        }
    }
    
    template2 = {
        "key3": "value3",
        "key2": {
            "nested3": "nested3"
        }
    }
    
    template3 = {
        "key1": "updated_value1",
        "key4": ["item1", "item2"]
    }
    
    # Merge templates
    merged = merge_templates([template1, template2, template3])
    
    # Check merged results
    assert merged["key1"] == "updated_value1"  # Should be overwritten by template3
    assert merged["key3"] == "value3"  # Should be added from template2
    assert merged["key4"] == ["item1", "item2"]  # Should be added from template3
    
    # Check that nested dictionaries are merged (not overwritten)
    assert "nested1" in merged["key2"]
    assert "nested2" in merged["key2"]
    assert "nested3" in merged["key2"]
    assert merged["key2"]["nested1"] == "nested1"
    assert merged["key2"]["nested2"] == "nested2"
    assert merged["key2"]["nested3"] == "nested3"


def test_template_consistency():
    """Test consistency of templates across project types and strategies."""
    # Check that all branching strategies have required branch configs
    strategies = BRANCHING_STRATEGY_TEMPLATES.keys()
    for strategy in strategies:
        template = BRANCHING_STRATEGY_TEMPLATES[strategy]
        assert "branches" in template
        assert "feature" in template["branches"]
        assert "pattern" in template["branches"]["feature"]
        assert "base" in template["branches"]["feature"]
    
    # Check that all project types have required version configs
    project_types = PROJECT_TYPE_TEMPLATES.keys()
    for project_type in project_types:
        template = PROJECT_TYPE_TEMPLATES[project_type]
        if "version" in template:
            assert "files" in template["version"]
            assert len(template["version"]["files"]) > 0
            assert "use_bumpversion" in template["version"]
    
    # Check that all PR templates have expected placeholders
    for branch_type, template in PR_TEMPLATES.items():
        if branch_type in ["feature", "bugfix"]:
            assert "{ticket_id}" in template
            assert "{description}" in template
        elif branch_type in ["release", "hotfix"]:
            assert "{version}" in template
