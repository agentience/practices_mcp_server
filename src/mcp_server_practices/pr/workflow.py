#!/usr/bin/env python
"""
PR preparation workflow functionality for the Practices MCP Server.
"""

import os
import subprocess
from typing import Dict, Any, Optional, List, Tuple

from .generator import generate_pr_description, create_pull_request


class PRWorkflow:
    """Manages the PR preparation workflow."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the PR workflow manager with configuration.

        Args:
            config: Configuration dictionary with PR workflow settings
        """
        self.config = config

    def prepare_pr(self, branch_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Prepare a PR for the current branch or specified branch.

        Args:
            branch_name: Optional branch name, if None will use current branch

        Returns:
            Dictionary with PR preparation results
        """
        # Get current branch if not specified
        if branch_name is None:
            current_branch = self._get_current_branch()
            if not current_branch["success"]:
                return current_branch
            branch_name = current_branch["branch"]
        
        # Check for uncommitted changes if configured
        if self.config.get("pr_workflow", {}).get("check_uncommitted", True):
            uncommitted = self._check_uncommitted_changes()
            if not uncommitted["success"]:
                return uncommitted
            elif uncommitted["has_changes"]:
                return {
                    "success": False,
                    "error": "There are uncommitted changes in the repository. Commit or stash them before preparing a PR.",
                    "has_uncommitted": True,
                    "branch_name": branch_name,
                }
        
        # Run tests if configured - tests MUST pass before a PR can be considered ready
        # This is a strict requirement for maintaining code quality
        if self.config.get("pr_workflow", {}).get("run_tests", True):
            test_result = self._run_tests()
            if not test_result["success"]:
                return {
                    "success": False,
                    "error": f"Tests failed: {test_result.get('error', 'See test output for details')}",
                    "branch_name": branch_name,
                    "test_output": test_result.get("output", ""),
                    "message": "All tests must pass before a feature is considered complete. Fix failing tests before preparing a PR."
                }
        
        # Generate PR description
        pr_data = generate_pr_description(branch_name, self.config)
        if not pr_data["success"]:
            return pr_data
        
        # Check for PR readiness based on code quality or other checks
        ready_result = self._check_pr_readiness()
        
        return {
            "success": True,
            "branch_name": branch_name,
            "description": pr_data["description"],
            "title": pr_data["title"],
            "base_branch": pr_data["base_branch"],
            "ready": ready_result["ready"],
            "warnings": ready_result.get("warnings", []),
            "suggestions": ready_result.get("suggestions", []),
        }

    def submit_pr(self, branch_name: Optional[str] = None, force: bool = False) -> Dict[str, Any]:
        """
        Submit a PR for the current branch or specified branch.

        Args:
            branch_name: Optional branch name, if None will use current branch
            force: If True, bypass readiness checks

        Returns:
            Dictionary with PR submission results
        """
        # Prepare PR first
        if not force:
            prep_result = self.prepare_pr(branch_name)
            if not prep_result["success"]:
                return prep_result
            
            # Check if PR is ready to be submitted
            if not prep_result["ready"]:
                return {
                    "success": False,
                    "error": "PR is not ready for submission. See warnings and suggestions.",
                    "branch_name": prep_result["branch_name"],
                    "warnings": prep_result.get("warnings", []),
                    "suggestions": prep_result.get("suggestions", []),
                    "description": prep_result["description"],
                }
            
            branch_name = prep_result["branch_name"]
        
        # Get current branch if still not specified
        if branch_name is None:
            current_branch = self._get_current_branch()
            if not current_branch["success"]:
                return current_branch
            branch_name = current_branch["branch"]
        
        # Create the PR
        return create_pull_request(branch_name, self.config)

    def _get_current_branch(self) -> Dict[str, Any]:
        """
        Get the current Git branch.

        Returns:
            Dictionary with the current branch information
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            branch = result.stdout.strip()
            
            return {
                "success": True,
                "branch": branch,
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to get current branch: {e.stderr}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get current branch: {str(e)}",
            }

    def _check_uncommitted_changes(self) -> Dict[str, Any]:
        """
        Check for uncommitted changes in the repository.

        Returns:
            Dictionary with uncommitted changes check results
        """
        try:
            # Check for staged and unstaged changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True,
            )
            
            changes = result.stdout.strip()
            has_changes = len(changes) > 0
            
            return {
                "success": True,
                "has_changes": has_changes,
                "changes": changes,
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to check uncommitted changes: {e.stderr}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to check uncommitted changes: {str(e)}",
            }

    def _run_tests(self) -> Dict[str, Any]:
        """
        Run tests for the repository.

        Returns:
            Dictionary with test results
        """
        try:
            # Get test command from config or use default
            test_cmd = self.config.get("pr_workflow", {}).get("test_command", "pytest")
            
            if isinstance(test_cmd, str):
                # Split string command into list
                test_cmd = test_cmd.split()
            
            # Run the test command
            result = subprocess.run(
                test_cmd,
                capture_output=True,
                text=True,
            )
            
            # Check if tests passed (return code 0)
            success = result.returncode == 0
            
            return {
                "success": success,
                "output": result.stdout + result.stderr,
                "return_code": result.returncode,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to run tests: {str(e)}",
            }

    def _check_pr_readiness(self) -> Dict[str, Any]:
        """
        Check if the PR is ready to be submitted.

        Returns:
            Dictionary with PR readiness check results
        """
        warnings = []
        suggestions = []
        ready = True
        
        # Check for lint errors if configured
        if self.config.get("pr_workflow", {}).get("check_lint", True):
            lint_result = self._run_lint()
            if not lint_result["success"]:
                ready = False
                warnings.append(f"Linting failed: {lint_result.get('error', '')}")
            elif lint_result.get("issues", 0) > 0:
                ready = self.config.get("pr_workflow", {}).get("allow_lint_warnings", True)
                warnings.append(f"Linting found {lint_result.get('issues', 0)} issues")
                suggestions.append("Fix linting issues before submitting")
        
        # Check for test coverage if configured
        if self.config.get("pr_workflow", {}).get("check_coverage", False):
            coverage = self._check_test_coverage()
            min_coverage = self.config.get("pr_workflow", {}).get("min_coverage", 80)
            
            if not coverage["success"]:
                warnings.append(f"Could not check test coverage: {coverage.get('error', '')}")
            elif coverage.get("percentage", 0) < min_coverage:
                ready = self.config.get("pr_workflow", {}).get("allow_low_coverage", True)
                warnings.append(f"Test coverage ({coverage.get('percentage', 0)}%) is below minimum ({min_coverage}%)")
                suggestions.append("Add more tests to increase coverage")
        
        return {
            "ready": ready,
            "warnings": warnings,
            "suggestions": suggestions,
        }

    def _run_lint(self) -> Dict[str, Any]:
        """
        Run linting on the repository.

        Returns:
            Dictionary with linting results
        """
        try:
            # Get lint command from config or use default
            lint_cmd = self.config.get("pr_workflow", {}).get("lint_command", "flake8")
            
            if isinstance(lint_cmd, str):
                # Split string command into list
                lint_cmd = lint_cmd.split()
            
            # Run the lint command
            result = subprocess.run(
                lint_cmd,
                capture_output=True,
                text=True,
            )
            
            # Check if linting passed (return code 0)
            success = result.returncode == 0
            
            # Count number of issues
            issues = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            
            return {
                "success": success,
                "output": result.stdout + result.stderr,
                "return_code": result.returncode,
                "issues": issues,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to run linting: {str(e)}",
            }

    def _check_test_coverage(self) -> Dict[str, Any]:
        """
        Check test coverage for the repository.

        Returns:
            Dictionary with test coverage results
        """
        try:
            # Get coverage command from config or use default
            cov_cmd = self.config.get("pr_workflow", {}).get("coverage_command", "pytest --cov=src")
            
            if isinstance(cov_cmd, str):
                # Split string command into list
                cov_cmd = cov_cmd.split()
            
            # Run the coverage command
            result = subprocess.run(
                cov_cmd,
                capture_output=True,
                text=True,
            )
            
            # Extract coverage percentage (this is a simple extraction and might need adjustment)
            output = result.stdout + result.stderr
            
            # Look for coverage pattern like "TOTAL                            100      23      77%"
            import re
            match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
            
            if match:
                percentage = int(match.group(1))
            else:
                percentage = 0
            
            return {
                "success": result.returncode == 0,
                "percentage": percentage,
                "output": output,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to check test coverage: {str(e)}",
            }


def prepare_pr(branch_name: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Prepare a PR for the current branch or specified branch.

    Args:
        branch_name: Optional branch name, if None will use current branch
        config: Optional configuration dictionary

    Returns:
        Dictionary with PR preparation results
    """
    if config is None:
        config = {}
    
    workflow = PRWorkflow(config)
    return workflow.prepare_pr(branch_name)


def submit_pr(branch_name: Optional[str] = None, force: bool = False, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Submit a PR for the current branch or specified branch.

    Args:
        branch_name: Optional branch name, if None will use current branch
        force: If True, bypass readiness checks
        config: Optional configuration dictionary

    Returns:
        Dictionary with PR submission results
    """
    if config is None:
        config = {}
    
    workflow = PRWorkflow(config)
    return workflow.submit_pr(branch_name, force)
