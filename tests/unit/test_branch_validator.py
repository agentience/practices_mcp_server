#!/usr/bin/env python
"""
Unit tests for the branch validator module.
"""

import unittest
from mcp_server_practices.branch.validator import validate_branch_name


class TestBranchValidator(unittest.TestCase):
    """Test the branch validator functionality."""

    def setUp(self):
        """Set up test configuration."""
        self.config = {
            "project_key": "PMS",
            "main_branch": "main",
            "develop_branch": "develop",
            "branching_strategy": "gitflow",
        }

    def test_feature_branch_validation(self):
        """Test validation of feature branches."""
        # Valid feature branch
        result = validate_branch_name("feature/PMS-123-add-user-authentication", self.config)
        self.assertTrue(result["valid"])
        self.assertEqual(result["branch_type"], "feature")
        self.assertEqual(result["base_branch"], "develop")
        self.assertEqual(result["components"]["identifier"], "PMS-123")
        self.assertEqual(result["components"]["description"], "add-user-authentication")

        # Invalid feature branch (wrong project key)
        result = validate_branch_name("feature/ABC-123-add-user-authentication", self.config)
        self.assertFalse(result["valid"])

        # Invalid feature branch (missing issue ID)
        result = validate_branch_name("feature/add-user-authentication", self.config)
        self.assertFalse(result["valid"])

    def test_bugfix_branch_validation(self):
        """Test validation of bugfix branches."""
        # Valid bugfix branch
        result = validate_branch_name("bugfix/PMS-456-fix-login-issue", self.config)
        self.assertTrue(result["valid"])
        self.assertEqual(result["branch_type"], "bugfix")
        self.assertEqual(result["base_branch"], "develop")
        self.assertEqual(result["components"]["identifier"], "PMS-456")
        self.assertEqual(result["components"]["description"], "fix-login-issue")

    def test_hotfix_branch_validation(self):
        """Test validation of hotfix branches."""
        # Valid hotfix branch
        result = validate_branch_name("hotfix/1.0.1-critical-security-fix", self.config)
        self.assertTrue(result["valid"])
        self.assertEqual(result["branch_type"], "hotfix")
        self.assertEqual(result["base_branch"], "main")
        self.assertEqual(result["components"]["version"], "1.0.1-critical")
        self.assertEqual(result["components"]["description"], "security-fix")

        # Invalid hotfix branch (wrong version format)
        result = validate_branch_name("hotfix/v1.0-critical-fix", self.config)
        self.assertFalse(result["valid"])

    def test_release_branch_validation(self):
        """Test validation of release branches."""
        # Valid release branch
        result = validate_branch_name("release/1.1.0", self.config)
        self.assertTrue(result["valid"])
        self.assertEqual(result["branch_type"], "release")
        self.assertEqual(result["base_branch"], "develop")
        self.assertEqual(result["components"]["version"], "1.1.0")
        self.assertIsNone(result["components"]["description"])

        # Valid release branch with description
        result = validate_branch_name("release/1.1.0-beta", self.config)
        self.assertTrue(result["valid"])
        self.assertEqual(result["components"]["version"], "1.1.0-beta")

    def test_docs_branch_validation(self):
        """Test validation of docs branches."""
        # Valid docs branch
        result = validate_branch_name("docs/update-readme", self.config)
        self.assertTrue(result["valid"])
        self.assertEqual(result["branch_type"], "docs")
        self.assertEqual(result["base_branch"], "develop")
        self.assertEqual(result["components"]["description"], "update-readme")

    def test_custom_project_key(self):
        """Test validation with a custom project key."""
        custom_config = self.config.copy()
        custom_config["project_key"] = "ABC"

        # Valid feature branch with custom project key
        result = validate_branch_name("feature/ABC-123-add-feature", custom_config)
        self.assertTrue(result["valid"])
        self.assertEqual(result["components"]["identifier"], "ABC-123")

        # Invalid feature branch with custom project key
        result = validate_branch_name("feature/PMS-123-add-feature", custom_config)
        self.assertFalse(result["valid"])


if __name__ == "__main__":
    unittest.main()
