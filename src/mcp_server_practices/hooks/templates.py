#!/usr/bin/env python
"""
Pre-commit hooks templates and configuration.

Copyright (c) 2025 Agentience.ai
Author: Troy Molander
License: MIT License - See LICENSE file for details

Version: 0.1.0
"""

from typing import Dict, Any, Optional

# Default pre-commit configuration template
DEFAULT_CONFIG = """# Default pre-commit configuration for development practices
# See https://pre-commit.com for more information
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files
    -   id: check-case-conflict
    -   id: check-merge-conflict
    -   id: detect-private-key

-   repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.275
    hooks:
    -   id: ruff
        args: [--fix, --exit-non-zero-on-fix]

-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black

-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
    -   id: mypy
        exclude: ^tests/
        additional_dependencies: [types-requests, types-pyyaml]

# Local hook for license headers
-   repo: local
    hooks:
    -   id: license-headers
        name: license headers
        entry: practices header batch --check
        language: system
        types: [python]
        stages: [commit]
"""

# Python-specific pre-commit configuration
PYTHON_CONFIG = """# Python-specific pre-commit configuration
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files
    -   id: check-case-conflict
    -   id: check-merge-conflict
    -   id: detect-private-key

-   repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.275
    hooks:
    -   id: ruff
        args: [--fix, --exit-non-zero-on-fix]

-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black

-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
    -   id: mypy
        exclude: ^tests/
        additional_dependencies: [types-requests, types-pyyaml]

# Local hook for license headers
-   repo: local
    hooks:
    -   id: license-headers
        name: license headers
        entry: practices header batch --check
        language: system
        types: [python]
        stages: [commit]
"""

# JavaScript/TypeScript pre-commit configuration
JS_CONFIG = """# JavaScript/TypeScript pre-commit configuration
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-json
    -   id: check-added-large-files
    -   id: check-case-conflict
    -   id: check-merge-conflict
    -   id: detect-private-key

-   repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.43.0
    hooks:
    -   id: eslint
        files: \\.(js|ts|jsx|tsx)$
        types: [file]
        additional_dependencies:
        -   eslint@8.43.0
        -   eslint-config-prettier@8.8.0
        -   eslint-plugin-import@2.27.5
        -   typescript@5.1.5
        -   @typescript-eslint/eslint-plugin@5.61.0
        -   @typescript-eslint/parser@5.61.0

-   repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.0.0
    hooks:
    -   id: prettier
        types_or: [javascript, jsx, ts, tsx, json, css, scss, markdown]

# Local hook for license headers
-   repo: local
    hooks:
    -   id: license-headers
        name: license headers
        entry: practices header batch --check
        language: system
        types: [javascript, jsx, typescript, tsx]
        stages: [commit]
"""


def get_default_config(config: Optional[Dict[str, Any]] = None) -> str:
    """
    Get the default pre-commit configuration.
    
    Args:
        config: Optional configuration overrides
        
    Returns:
        Pre-commit configuration YAML content
    """
    if not config:
        config = {}
    
    project_type = config.get("project_type", "").lower()
    
    if project_type == "python":
        return PYTHON_CONFIG
    elif project_type in ["javascript", "typescript", "js", "ts"]:
        return JS_CONFIG
    else:
        return DEFAULT_CONFIG
