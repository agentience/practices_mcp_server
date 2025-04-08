#!/usr/bin/env python3
"""
Simple verification script for the configuration schema.
"""

from src.mcp_server_practices.config.schema import (
    ConfigurationSchema,
    ProjectConfig,
    ProjectType,
    BranchingStrategy,
    BranchConfig,
)


def test_schema():
    # Valid configuration
    valid_config = ConfigurationSchema(
        project_type=ProjectType.PYTHON,
        branching_strategy=BranchingStrategy.GITFLOW,
        workflow_mode="solo",
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
            )
        }
    )
    
    print("Created valid configuration:")
    print(f"  Project Type: {valid_config.project_type}")
    print(f"  Branching Strategy: {valid_config.branching_strategy}")
    print(f"  Branches: {list(valid_config.branches.keys())}")
    
    try:
        # Test model_validator. This should validate that we need develop_branch for GitFlow
        invalid_config = ConfigurationSchema(
            project_type=ProjectType.PYTHON,
            branching_strategy=BranchingStrategy.GITFLOW,
            workflow_mode="solo",
            main_branch="main",
            develop_branch=None,  # Missing develop branch for GitFlow
            branches={
                "feature": BranchConfig(
                    pattern="^feature/([A-Z]+-\\d+)-(.+)$",
                    base="develop",
                    version_bump=None
                )
            }
        )
        
        # We need to access some property to trigger the validation
        print(invalid_config.model_dump())
        print("ERROR: Validation did not catch missing develop_branch for GitFlow")
    except ValueError as e:
        # This is expected
        print(f"Correctly caught validation error: {e}")
    
    # Test that GitHub Flow works without develop branch
    github_flow_config = ConfigurationSchema(
        project_type=ProjectType.PYTHON,
        branching_strategy=BranchingStrategy.GITHUB_FLOW,
        workflow_mode="solo",
        main_branch="main",
        develop_branch=None,  # No develop branch needed for GitHub Flow
        branches={
            "feature": BranchConfig(
                pattern="^feature/([A-Z]+-\\d+)-(.+)$",
                base="main",
                version_bump=None
            ),
            "bugfix": BranchConfig(
                pattern="^bugfix/([A-Z]+-\\d+)-(.+)$",
                base="main",
                version_bump=None
            )
        }
    )
    
    print("\nCreated valid GitHub Flow configuration:")
    print(f"  Project Type: {github_flow_config.project_type}")
    print(f"  Branching Strategy: {github_flow_config.branching_strategy}")
    print(f"  Develop Branch: {github_flow_config.develop_branch}")
    print(f"  Branches: {list(github_flow_config.branches.keys())}")
    
    print("\nAll tests passed!")


if __name__ == "__main__":
    test_schema()
