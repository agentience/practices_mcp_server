#!/usr/bin/env python
"""
Unit tests for PR functionality.
"""
import pytest

pytest.skip("Skipping PR functionality tests due to MCP package dependency issues", allow_module_level=True)

import unittest
from unittest.mock import patch, MagicMock
import json
import tempfile
import os
import sys

# Mock mcp.tools which is imported in our code but not available in tests
sys.modules['mcp.tools'] = MagicMock()
sys.modules['mcp'] = MagicMock()

from src.mcp_server_practices.pr.templates import get_template, TemplateManager
from src.mcp_server_practices.pr.generator import generate_pr_description, PRGenerator
from src.mcp_server_practices.pr.workflow import prepare_pr, PRWorkflow


class TestPRTemplates(unittest.TestCase):
    """Test cases for PR templates functionality."""

    def test_get_template_default(self):
        """Test getting a default template."""
        template = get_template("feature")
        self.assertIn("{jira_id}", template)
        self.assertIn("Changes", template)
        self.assertIn("Testing", template)

    def test_get_template_unknown_type(self):
        """Test getting a template for an unknown branch type."""
        template = get_template("unknown")
        self.assertIn("{branch_name}", template)
        self.assertIn("Changes", template)

    def test_custom_templates(self):
        """Test custom templates from config."""
        config = {
            "pr_templates": {
                "feature": "Custom feature template for {jira_id}"
            }
        }
        manager = TemplateManager(config)
        self.assertEqual(manager.get_template("feature"), "Custom feature template for {jira_id}")
        # Other templates should still use defaults
        self.assertIn("HOTFIX {version}", manager.get_template("hotfix"))


class TestPRGenerator(unittest.TestCase):
    """Test cases for PR generator functionality."""

    @patch("src.mcp_server_practices.pr.generator.validate_branch_name")
    @patch("src.mcp_server_practices.pr.generator.get_template")
    def test_generate_description_feature(self, mock_get_template, mock_validate):
        """Test generating a PR description for a feature branch."""
        # Mock validation result
        mock_validate.return_value = {
            "valid": True,
            "branch_type": "feature",
            "components": {
                "identifier": "PMS-123",
                "description": "add-pr-tools"
            },
            "base_branch": "develop"
        }
        
        # Mock template
        mock_get_template.return_value = "PR for {jira_id}: {description}"
        
        # Test generation
        result = generate_pr_description("feature/PMS-123-add-pr-tools")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["description"], "PR for PMS-123: add-pr-tools")
        self.assertEqual(result["branch_name"], "feature/PMS-123-add-pr-tools")
        self.assertEqual(result["base_branch"], "develop")

    @patch("src.mcp_server_practices.pr.generator.validate_branch_name")
    def test_generate_description_invalid_branch(self, mock_validate):
        """Test generating a PR description for an invalid branch."""
        # Mock validation result
        mock_validate.return_value = {
            "valid": False,
            "error": "Invalid branch name"
        }
        
        # Test generation
        result = generate_pr_description("invalid-branch")
        
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Invalid branch name")

    @patch("src.mcp_server_practices.pr.generator.validate_branch_name")
    @patch("src.mcp_server_practices.pr.generator.get_template")
    @patch("src.mcp_server_practices.pr.generator.get_issue")
    def test_generate_description_with_jira(self, mock_get_issue, mock_get_template, mock_validate):
        """Test generating a PR description with Jira information."""
        # Mock validation result
        mock_validate.return_value = {
            "valid": True,
            "branch_type": "feature",
            "components": {
                "identifier": "PMS-123",
                "description": "add-pr-tools"
            },
            "base_branch": "develop"
        }
        
        # Mock Jira issue
        mock_get_issue.return_value = {
            "fields": {
                "summary": "Add PR tools functionality",
                "status": {
                    "name": "In Progress"
                }
            }
        }
        
        # Mock template
        mock_get_template.return_value = "{jira_id}: {jira_summary}"
        
        # Test generation
        result = generate_pr_description("feature/PMS-123-add-pr-tools")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["description"], "PMS-123: Add PR tools functionality")
        self.assertEqual(result["jira_id"], "PMS-123")


class TestPRWorkflow(unittest.TestCase):
    """Test cases for PR workflow functionality."""

    @patch("src.mcp_server_practices.pr.workflow.PRWorkflow._get_current_branch")
    @patch("src.mcp_server_practices.pr.workflow.PRWorkflow._check_uncommitted_changes")
    @patch("src.mcp_server_practices.pr.workflow.generate_pr_description")
    @patch("src.mcp_server_practices.pr.workflow.PRWorkflow._check_pr_readiness")
    @patch("src.mcp_server_practices.pr.workflow.PRWorkflow._run_tests")
    def test_prepare_pr_successful(self, mock_run_tests, mock_readiness, mock_generate, mock_uncommitted, mock_branch):
        """Test preparing a PR successfully."""
        # Mock current branch
        mock_branch.return_value = {
            "success": True,
            "branch": "feature/PMS-123-add-pr-tools"
        }
        
        # Mock uncommitted changes
        mock_uncommitted.return_value = {
            "success": True,
            "has_changes": False
        }
        
        # Mock PR description
        mock_generate.return_value = {
            "success": True,
            "description": "PR description",
            "title": "PMS-123: Add PR tools",
            "base_branch": "develop",
            "branch_name": "feature/PMS-123-add-pr-tools",
            "branch_type": "feature",
            "components": {}
        }
        
        # Mock test run
        mock_run_tests.return_value = {
            "success": True,
            "output": "All tests passed",
            "return_code": 0
        }
        
        # Mock readiness check
        mock_readiness.return_value = {
            "ready": True,
            "warnings": [],
            "suggestions": []
        }
        
        # Test preparation
        result = prepare_pr()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["description"], "PR description")
        self.assertEqual(result["title"], "PMS-123: Add PR tools")
        self.assertEqual(result["base_branch"], "develop")
        self.assertTrue(result["ready"])

    @patch("src.mcp_server_practices.pr.workflow.PRWorkflow._get_current_branch")
    @patch("src.mcp_server_practices.pr.workflow.PRWorkflow._check_uncommitted_changes")
    def test_prepare_pr_uncommitted_changes(self, mock_uncommitted, mock_branch):
        """Test preparing a PR with uncommitted changes."""
        # Mock current branch
        mock_branch.return_value = {
            "success": True,
            "branch": "feature/PMS-123-add-pr-tools"
        }
        
        # Mock uncommitted changes
        mock_uncommitted.return_value = {
            "success": True,
            "has_changes": True,
            "changes": "M file.txt"
        }
        
        # Test preparation
        result = prepare_pr()
        
        self.assertFalse(result["success"])
        self.assertIn("uncommitted changes", result["error"])
        self.assertTrue(result["has_uncommitted"])

    @patch("subprocess.run")
    def test_get_current_branch(self, mock_subprocess):
        """Test getting the current branch."""
        # Mock subprocess result
        mock_process = MagicMock()
        mock_process.stdout = "feature/PMS-123-add-pr-tools\n"
        mock_process.returncode = 0
        mock_subprocess.return_value = mock_process
        
        # Create workflow and test
        workflow = PRWorkflow({})
        result = workflow._get_current_branch()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["branch"], "feature/PMS-123-add-pr-tools")


if __name__ == "__main__":
    unittest.main()
