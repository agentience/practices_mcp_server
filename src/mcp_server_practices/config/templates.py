#!/usr/bin/env python
"""
Configuration templates for the Practices MCP Server.

This module provides predefined configuration templates for different
project types and branching strategies. These templates are used as defaults
when a user doesn't have a custom configuration.

Copyright (c) 2025 Agentience.ai
Author: Troy Molander
License: MIT License - See LICENSE file for details

Version: 0.2.0
"""

import logging
from typing import Dict, Any, Optional, List

from .schema import ProjectType, BranchingStrategy

logger = logging.getLogger(__name__)

# Templates by project type
PROJECT_TYPE_TEMPLATES = {
    ProjectType.PYTHON: {
        "version": {
            "files": [
                {
                    "path": "src/__project__/__init__.py",
                    "pattern": "__version__ = \"(\\d+\\.\\d+\\.\\d+)\""
                },
                {
                    "path": "pyproject.toml",
                    "pattern": "version = \"(\\d+\\.\\d+\\.\\d+)\""
                }
            ],
            "use_bumpversion": True,
            "bumpversion_config": ".bumpversion.cfg",
            "changelog": "CHANGELOG.md"
        },
        "pre_commit": {
            "hooks": [
                {
                    "id": "black",
                    "name": "black",
                    "description": "Format Python code with Black",
                    "entry": "black",
                    "language": "python",
                    "types": ["python"]
                },
                {
                    "id": "isort",
                    "name": "isort",
                    "description": "Sort Python imports",
                    "entry": "isort",
                    "language": "python",
                    "types": ["python"]
                },
                {
                    "id": "flake8",
                    "name": "flake8",
                    "description": "Check Python code style with Flake8",
                    "entry": "flake8",
                    "language": "python",
                    "types": ["python"]
                },
                {
                    "id": "mypy",
                    "name": "mypy",
                    "description": "Check Python types with mypy",
                    "entry": "mypy",
                    "language": "python",
                    "types": ["python"]
                }
            ]
        },
        "license_headers": {
            "template": "Copyright (c) 2025 Agentience.ai\nAuthor: Troy Molander\nLicense: MIT License - See LICENSE file for details\n\nVersion: 0.2.0",
            "file_types": [
                {
                    "extension": ".py",
                    "prefix": "# "
                }
            ]
        }
    },
    ProjectType.JAVASCRIPT: {
        "version": {
            "files": [
                {
                    "path": "package.json",
                    "pattern": "\"version\": \"(\\d+\\.\\d+\\.\\d+)\""
                }
            ],
            "use_bumpversion": False,
            "changelog": "CHANGELOG.md"
        },
        "pre_commit": {
            "hooks": [
                {
                    "id": "prettier",
                    "name": "prettier",
                    "description": "Format JavaScript code with Prettier",
                    "entry": "prettier --write",
                    "language": "node",
                    "types": ["javascript", "jsx", "json"]
                },
                {
                    "id": "eslint",
                    "name": "eslint",
                    "description": "Lint JavaScript code with ESLint",
                    "entry": "eslint --fix",
                    "language": "node",
                    "types": ["javascript", "jsx"]
                }
            ]
        },
        "license_headers": {
            "template": "Copyright (c) 2025 Agentience.ai\nAuthor: Troy Molander\nLicense: MIT License - See LICENSE file for details\n\nVersion: 0.2.0",
            "file_types": [
                {
                    "extension": ".js",
                    "prefix": "// "
                },
                {
                    "extension": ".jsx",
                    "prefix": "// "
                }
            ]
        }
    },
    ProjectType.TYPESCRIPT: {
        "version": {
            "files": [
                {
                    "path": "package.json",
                    "pattern": "\"version\": \"(\\d+\\.\\d+\\.\\d+)\""
                }
            ],
            "use_bumpversion": False,
            "changelog": "CHANGELOG.md"
        },
        "pre_commit": {
            "hooks": [
                {
                    "id": "prettier",
                    "name": "prettier",
                    "description": "Format TypeScript code with Prettier",
                    "entry": "prettier --write",
                    "language": "node",
                    "types": ["typescript", "tsx", "json"]
                },
                {
                    "id": "eslint",
                    "name": "eslint",
                    "description": "Lint TypeScript code with ESLint",
                    "entry": "eslint --fix",
                    "language": "node",
                    "types": ["typescript", "tsx"]
                }
            ]
        },
        "license_headers": {
            "template": "Copyright (c) 2025 Agentience.ai\nAuthor: Troy Molander\nLicense: MIT License - See LICENSE file for details\n\nVersion: 0.2.0",
            "file_types": [
                {
                    "extension": ".ts",
                    "prefix": "// "
                },
                {
                    "extension": ".tsx",
                    "prefix": "// "
                }
            ]
        }
    },
    ProjectType.JAVA: {
        "version": {
            "files": [
                {
                    "path": "pom.xml",
                    "pattern": "<version>(\\d+\\.\\d+\\.\\d+)</version>"
                }
            ],
            "use_bumpversion": False,
            "changelog": "CHANGELOG.md"
        },
        "pre_commit": {
            "hooks": [
                {
                    "id": "checkstyle",
                    "name": "checkstyle",
                    "description": "Check Java code style with Checkstyle",
                    "entry": "mvn checkstyle:check",
                    "language": "system",
                    "types": ["java"]
                },
                {
                    "id": "spotless",
                    "name": "spotless",
                    "description": "Format Java code with Spotless",
                    "entry": "mvn spotless:apply",
                    "language": "system",
                    "types": ["java"]
                }
            ]
        },
        "license_headers": {
            "template": "Copyright (c) 2025 Agentience.ai\nAuthor: Troy Molander\nLicense: MIT License - See LICENSE file for details\n\nVersion: 0.2.0",
            "file_types": [
                {
                    "extension": ".java",
                    "start": "/*",
                    "prefix": " * ",
                    "end": " */"
                }
            ]
        }
    },
    ProjectType.CSHARP: {
        "version": {
            "files": [
                {
                    "path": "Directory.Build.props",
                    "pattern": "<Version>(\\d+\\.\\d+\\.\\d+)</Version>"
                }
            ],
            "use_bumpversion": False,
            "changelog": "CHANGELOG.md"
        },
        "pre_commit": {
            "hooks": [
                {
                    "id": "dotnet-format",
                    "name": "dotnet-format",
                    "description": "Format C# code with dotnet format",
                    "entry": "dotnet format",
                    "language": "system",
                    "types": ["csharp"]
                }
            ]
        },
        "license_headers": {
            "template": "Copyright (c) 2025 Agentience.ai\nAuthor: Troy Molander\nLicense: MIT License - See LICENSE file for details\n\nVersion: 0.2.0",
            "file_types": [
                {
                    "extension": ".cs",
                    "prefix": "// "
                }
            ]
        }
    },
    ProjectType.GO: {
        "version": {
            "files": [
                {
                    "path": "version.go",
                    "pattern": "const Version = \"(\\d+\\.\\d+\\.\\d+)\""
                }
            ],
            "use_bumpversion": False,
            "changelog": "CHANGELOG.md"
        },
        "pre_commit": {
            "hooks": [
                {
                    "id": "go-fmt",
                    "name": "go-fmt",
                    "description": "Format Go code with go fmt",
                    "entry": "go fmt",
                    "language": "system",
                    "types": ["go"]
                },
                {
                    "id": "go-vet",
                    "name": "go-vet",
                    "description": "Check Go code with go vet",
                    "entry": "go vet",
                    "language": "system",
                    "types": ["go"]
                },
                {
                    "id": "golint",
                    "name": "golint",
                    "description": "Lint Go code with golint",
                    "entry": "golint",
                    "language": "system",
                    "types": ["go"]
                }
            ]
        },
        "license_headers": {
            "template": "Copyright (c) 2025 Agentience.ai\nAuthor: Troy Molander\nLicense: MIT License - See LICENSE file for details\n\nVersion: 0.2.0",
            "file_types": [
                {
                    "extension": ".go",
                    "prefix": "// "
                }
            ]
        }
    },
    ProjectType.RUST: {
        "version": {
            "files": [
                {
                    "path": "Cargo.toml",
                    "pattern": "version = \"(\\d+\\.\\d+\\.\\d+)\""
                }
            ],
            "use_bumpversion": False,
            "changelog": "CHANGELOG.md"
        },
        "pre_commit": {
            "hooks": [
                {
                    "id": "rustfmt",
                    "name": "rustfmt",
                    "description": "Format Rust code with rustfmt",
                    "entry": "cargo fmt",
                    "language": "system",
                    "types": ["rust"]
                },
                {
                    "id": "clippy",
                    "name": "clippy",
                    "description": "Lint Rust code with clippy",
                    "entry": "cargo clippy",
                    "language": "system",
                    "types": ["rust"]
                }
            ]
        },
        "license_headers": {
            "template": "Copyright (c) 2025 Agentience.ai\nAuthor: Troy Molander\nLicense: MIT License - See LICENSE file for details\n\nVersion: 0.2.0",
            "file_types": [
                {
                    "extension": ".rs",
                    "prefix": "// "
                }
            ]
        }
    },
    ProjectType.GENERIC: {
        "version": {
            "files": [
                {
                    "path": "VERSION",
                    "pattern": "(\\d+\\.\\d+\\.\\d+)"
                }
            ],
            "use_bumpversion": False,
            "changelog": "CHANGELOG.md"
        },
        "license_headers": {
            "template": "Copyright (c) 2025 Agentience.ai\nAuthor: Troy Molander\nLicense: MIT License - See LICENSE file for details\n\nVersion: 0.2.0",
            "file_types": [
                {
                    "extension": ".py",
                    "prefix": "# "
                },
                {
                    "extension": ".js",
                    "prefix": "// "
                },
                {
                    "extension": ".java",
                    "start": "/*",
                    "prefix": " * ",
                    "end": " */"
                },
                {
                    "extension": ".cs",
                    "prefix": "// "
                },
                {
                    "extension": ".go",
                    "prefix": "// "
                },
                {
                    "extension": ".rs",
                    "prefix": "// "
                }
            ]
        }
    }
}


# Templates by branching strategy
BRANCHING_STRATEGY_TEMPLATES = {
    BranchingStrategy.GITFLOW: {
        "branching_strategy": "gitflow",
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
            },
            "hotfix": {
                "pattern": "^hotfix/(\\d+\\.\\d+\\.\\d+(?:-[a-zA-Z0-9.]+)?)-(.+)$",
                "base": "main",
                "target": ["main", "develop"],
                "version_bump": "patch"
            },
            "release": {
                "pattern": "^release/(\\d+\\.\\d+\\.\\d+(?:-[a-zA-Z0-9.]+)?)(?:-(.+))?$",
                "base": "develop",
                "target": ["main", "develop"],
                "version_bump": "minor"
            },
            "docs": {
                "pattern": "^docs/(.+)$",
                "base": "develop",
                "version_bump": None
            }
        }
    },
    BranchingStrategy.GITHUB_FLOW: {
        "branching_strategy": "github-flow",
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
            },
            "hotfix": {
                "pattern": "^hotfix/(\\d+\\.\\d+\\.\\d+(?:-[a-zA-Z0-9.]+)?)-(.+)$",
                "base": "main",
                "version_bump": "patch"
            },
            "docs": {
                "pattern": "^docs/(.+)$",
                "base": "main",
                "version_bump": None
            }
        }
    },
    BranchingStrategy.TRUNK: {
        "branching_strategy": "trunk",
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
            },
            "release": {
                "pattern": "^release/(\\d+\\.\\d+\\.\\d+(?:-[a-zA-Z0-9.]+)?)$",
                "base": "main",
                "version_bump": "minor"
            }
        }
    }
}


# PR template by branch type
PR_TEMPLATES = {
    "feature": "# {ticket_id}: {description}\n\n## Summary\nThis PR implements {description} functionality ({ticket_id}).\n\n## Changes\n-\n\n## Testing\n-\n\n## Related Issues\n- {ticket_id}: {ticket_description}",
    "bugfix": "# {ticket_id}: Fix {description}\n\n## Summary\nThis PR fixes {description} issue ({ticket_id}).\n\n## Root Cause\n-\n\n## Changes\n-\n\n## Testing\n-\n\n## Related Issues\n- {ticket_id}: {ticket_description}",
    "release": "# Release {version}\n\n## Summary\nThis PR prepares the release of version {version}.\n\n## Changes\n- Version bump to {version}\n- Updated CHANGELOG.md\n\n## Testing\n- Verified all tests pass\n- Checked version consistency\n\n## Release Notes\nSee CHANGELOG.md for details.",
    "hotfix": "# Hotfix {version}: {description}\n\n## Summary\nThis PR fixes a critical issue in production: {description}.\n\n## Root Cause\n-\n\n## Changes\n-\n\n## Testing\n-\n\n## Deployment Plan\n-"
}


def get_template_for_project_type(project_type: ProjectType) -> Dict[str, Any]:
    """
    Get the template for a specific project type.
    
    Args:
        project_type: Type of project
        
    Returns:
        Dictionary with template configuration for the project type
    """
    if project_type in PROJECT_TYPE_TEMPLATES:
        return PROJECT_TYPE_TEMPLATES[project_type]
    
    # Fallback to GENERIC
    logger.warning(f"No template found for project type {project_type}, using GENERIC")
    return PROJECT_TYPE_TEMPLATES[ProjectType.GENERIC]


def get_template_for_branching_strategy(strategy: BranchingStrategy) -> Dict[str, Any]:
    """
    Get the template for a specific branching strategy.
    
    Args:
        strategy: Branching strategy
        
    Returns:
        Dictionary with template configuration for the branching strategy
    """
    if strategy in BRANCHING_STRATEGY_TEMPLATES:
        return BRANCHING_STRATEGY_TEMPLATES[strategy]
    
    # Fallback to GITFLOW
    logger.warning(f"No template found for branching strategy {strategy}, using GITFLOW")
    return BRANCHING_STRATEGY_TEMPLATES[BranchingStrategy.GITFLOW]


def get_pr_template(branch_type: str) -> Optional[str]:
    """
    Get the PR template for a specific branch type.
    
    Args:
        branch_type: Type of branch
        
    Returns:
        PR template for the branch type or None if not found
    """
    if branch_type in PR_TEMPLATES:
        return PR_TEMPLATES[branch_type]
    
    return None


def merge_templates(templates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge multiple templates into a single configuration.
    
    Args:
        templates: List of templates to merge
        
    Returns:
        Dictionary with merged configuration
    """
    result: Dict[str, Any] = {}
    
    for template in templates:
        for key, value in template.items():
            if key not in result:
                result[key] = value
            elif isinstance(value, dict) and isinstance(result[key], dict):
                # Merge dictionaries recursively
                result[key] = {**result[key], **value}
            else:
                # Override with the latest value
                result[key] = value
    
    return result
