# Branch Tool Parameter Fix Implementation Plan

## Bug Description

The `create_branch` tool in the MCP server has a parameter mismatch between its implementation and documentation:

- **Implementation**: Uses `identifier` parameter name in the function signature
- **Documentation**: Uses `ticket_id` parameter name in examples

This mismatch causes an error when trying to call the tool with parameters as shown in the documentation:

```
Error executing tool create_branch: BaseModel.__init__() takes 1 positional argument but 2 were given
```

## Root Cause Analysis

When examining `src/mcp_server_practices/tools/branch_tools.py`, we found that the `create_branch` function is defined as:

```python
async def create_branch(*, branch_type: str, identifier: str, description: Any = None, update_jira: bool = True)
```

But in the system_instructions.md documentation, the example shows:

```python
call_tool("practices", "create_branch", {
    "branch_type": "feature",
    "ticket_id": "PMS-123",  # This doesn't match "identifier" in the function
    "description": "add-validation"
})
```

This mismatch creates an issue with how Pydantic models in the MCP server validate parameters.

## Fix Implementation Plan

### Option A: Update Code to Match Documentation (SELECTED)

1. **Create Jira Bug Ticket**
   - Summary: "Fix parameter mismatch in create_branch tool"
   - Description: "The create_branch tool's implementation uses 'identifier' parameter, but documentation and examples show 'ticket_id'. This causes a BaseModel initialization error when calling the tool with parameters as shown in documentation."
   - Type: Bug
   - Priority: Medium

2. **Create Bugfix Branch**
   - Branch name: `bugfix/PMS-XX-fix-branch-tool-parameters` (replace XX with actual ticket number)

3. **Code Changes**
   
   Update the function signature in `branch_tools.py`:

   ```python
   # Current implementation
   @mcp.tool(
       name="create_branch",
       description="Create a new branch following the branching convention"
   )
   async def create_branch(*, branch_type: str, identifier: str, description: Any = None, update_jira: bool = True) -> List[TextContent]:
   ```

   ```python
   # Updated implementation
   @mcp.tool(
       name="create_branch",
       description="Create a new branch following the branching convention"
   )
   async def create_branch(*, branch_type: str, ticket_id: str, description: Any = None, update_jira: bool = True) -> List[TextContent]:
   ```

   Also update references to `identifier` in the function body:

   ```python
   # Create the branch
   result = create_branch_func(branch_type, ticket_id, description, config)
   
   # If branch creation was successful and it's a feature/bugfix branch, update Jira
   if result["success"] and update_jira and branch_type in ["feature", "bugfix"]:
       jira_result = update_issue_status(ticket_id, "In Progress", config)
       result["jira_update"] = jira_result
   ```

4. **Test Changes**
   - Verify that the create_branch tool works when called with the parameters as shown in documentation
   - Test with different branch types to ensure all functionality works correctly

5. **Complete Workflow**
   - Commit changes with message referencing Jira ticket
   - Run all tests to ensure no regressions
   - Update Jira ticket status to "Done"
   - Merge bugfix branch to develop
   - Delete the bugfix branch after merging

### Option B: Update Documentation to Match Code (NOT SELECTED)

As an alternative, we could have updated all the documentation examples to use `identifier` instead of `ticket_id`, but we chose Option A because:

1. It's easier for users to follow the existing examples in documentation
2. "ticket_id" is a more descriptive parameter name for feature/bugfix branches
3. Making the change in the code is a smaller change with less risk of introducing inconsistencies

## Expected Results

After this fix, users will be able to call the create_branch tool as shown in the documentation without encountering parameter errors. This will ensure a consistent experience between the tool's behavior and its documentation.
