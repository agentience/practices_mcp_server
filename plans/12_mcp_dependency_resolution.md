# MCP Dependency Resolution Plan

## Overview

This document outlines the plan to fix the "No module named 'mcp.tools'" error in the MCP Server Practices package. The issue occurs because of how dependencies are managed when using `uv tool install .`, but the underlying code architecture can also be improved to match the approach used in the tribal project.

## Jira Issues

Before implementation, create the following Jira issues:

### Issue 1: Fix MCP Dependency Import Error
- **Type**: Bug
- **Summary**: Fix "No module named 'mcp.tools'" error in MCP Server Practices
- **Description**: 
  ```
  When installing with `uv tool install .` and running the `practices` executable, the following error occurs:
  
  ```
  % practices
  Traceback (most recent call last):
    File "/Users/troymolander/.local/bin/practices", line 4, in <module>
      from mcp_server_practices.cli import main
    File "/Users/troymolander/.local/share/uv/tools/mcp-server-practices/lib/python3.13/site-packages/mcp_server_practices/cli/__init__.py", line 3, in <module>
      from .commands import main
    File "/Users/troymolander/.local/share/uv/tools/mcp-server-practices/lib/python3.13/site-packages/mcp_server_practices/cli/commands.py", line 15, in <module>
      from mcp_server_practices.integrations.jira import get_issue, update_issue_status
    File "/Users/troymolander/.local/share/uv/tools/mcp-server-practices/lib/python3.13/site-packages/mcp_server_practices/integrations/jira.py", line 8, in <module>
      from mcp.tools import call_tool
  ModuleNotFoundError: No module named 'mcp.tools'
  ```
  
  Analysis shows this is due to issues with how the UV tool handles dependencies in isolated environments.
  ```
- **Priority**: High
- **Assignee**: [TBD]

### Issue 2: Modernize MCP Server Implementation
- **Type**: Improvement 
- **Summary**: Modernize MCP Server implementation to match tribal project pattern
- **Description**:
  ```
  The current MCP Server implementation should be updated to better align with the patterns used in the mcp_server_tribal project. Specifically:
  
  1. Use direct imports from mcp packages
  2. Remove unnecessary abstraction layers
  3. Use the decorator pattern for defining tools where appropriate
  
  This will improve code maintainability and align with best practices.
  ```
- **Priority**: Medium
- **Assignee**: [TBD]
- **Depends On**: Issue 1 (Fix MCP Dependency Import Error)

## Implementation Plan

### Phase 1: Fix Immediate Dependency Issue (Issue 1)

#### 1.1 Update Jira Integration

Update `src/mcp_server_practices/integrations/jira.py` to use direct imports:

```python
#!/usr/bin/env python
"""
Jira integration for the Practices MCP Server.
"""

from typing import Dict, Any, Optional, List

# Direct import from mcp package
from mcp.tools import call_tool

# Rest of the file remains unchanged
```

#### 1.2 Update GitHub Integration

Update `src/mcp_server_practices/integrations/github.py` to use direct imports:

```python
#!/usr/bin/env python
"""
GitHub integration for the Practices MCP Server.
"""

from typing import Dict, Any, Optional, List, Union
import json
import re

# Direct import from mcp package
from mcp.tools import call_tool

# Rest of the file remains unchanged
```

#### 1.3 Update PR Generator

Update `src/mcp_server_practices/pr/generator.py` in the `create_pull_request` function:

```python
def create_pull_request(branch_name: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    # ...
    
    # Import directly
    from mcp.tools import call_tool
    
    # Get repository information from config
    repo_owner = config.get("github", {}).get("owner", "")
    repo_name = config.get("github", {}).get("repo", "")
    
    # Direct call_tool usage
    result = call_tool(
        "github",
        "create_pull_request",
        {
            "owner": repo_owner,
            "repo": repo_name,
            "title": pr_data["title"],
            "body": pr_data["description"],
            "head": branch_name,
            "base": pr_data["base_branch"],
            "draft": config.get("pull_requests", {}).get("create_as_draft", True),
        }
    )
    
    # Rest of the function remains unchanged
```

#### 1.4 Remove utils/mcp_tools.py

This file is no longer needed as we're using direct imports:

```bash
rm src/mcp_server_practices/utils/mcp_tools.py
```

### Phase 2: Modernize MCP Server Implementation (Issue 2)

#### 2.1 Update MCP Server Implementation

Update `src/mcp_server_practices/mcp_server.py` to use the decorator-based approach:

```python
#!/usr/bin/env python
"""
MCP server implementation for development practices.
"""

import asyncio
import sys
from typing import Any, Dict, List, Optional

# Import directly from mcp package
from mcp.server.fastmcp import FastMCP
from mcp.content import TextContent

from mcp_server_practices import __version__
# Other imports remain the same

# Initialize FastMCP
mcp = FastMCP(
    title="Practices",
    description="Development practices tools and resources",
    version=__version__,
)

# Define tools using decorators
@mcp.tool()
async def validate_branch_name(branch_name: str) -> List[TextContent]:
    # Implementation using decorators
    # ...

# Continue with other tool definitions

def main():
    """Start the MCP server."""
    # Use mcp.run() for modern implementation
    mcp.run(transport="stdio")
```

## Testing Strategy

1. **Unit Tests**:
   - Update unit tests for affected files to ensure they work with the new direct import approach
   - Verify all functionality remains the same

2. **Integration Tests**:
   - Verify that the practices command works after installation
   - Test all main functionality through the CLI

3. **Installation Testing**:
   - Test with `uv tool install .` in a clean environment
   - Verify the package works properly when installed from PyPI

## Rollout Plan

1. Create the Jira issues documented above
2. Implement Phase 1 (Fix Immediate Dependency Issue)
   - Create a feature branch `bugfix/PMS-XXX-fix-mcp-dependency-issue` (where XXX is the issue number)
   - Make the necessary changes
   - Test thoroughly
   - Submit PR
   - Merge to develop

3. Implement Phase 2 (Modernize MCP Server Implementation)
   - Create a feature branch `feature/PMS-YYY-modernize-mcp-server` (where YYY is the issue number)
   - Make the necessary changes
   - Test thoroughly
   - Submit PR
   - Merge to develop

4. Release Testing
   - Create a release branch when ready
   - Final testing in an isolated environment
   - Release to PyPI
