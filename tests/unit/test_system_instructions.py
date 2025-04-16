"""
Unit tests for system instructions handling.
"""
import pytest

pytest.skip("Skipping system instructions tests due to MCP package dependency issues", allow_module_level=True)

import os
import pytest
import tempfile
import shutil
from pathlib import Path

# Add pytest_asyncio for handling async tests
import pytest_asyncio

from mcp_server_practices.mcp_server import get_system_instructions


@pytest.fixture
def temp_project_dir():
    """Create a temporary directory to simulate a project root."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up after test
    shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_get_system_instructions_creates_default_file(temp_project_dir):
    """Test that get_system_instructions creates the default file if it doesn't exist."""
    # Get system instructions
    instructions = await get_system_instructions(temp_project_dir)
    
    # Verify system instructions were returned
    assert instructions
    assert "# Practices MCP Server - System Instructions" in instructions
    
    # Verify file was created
    practices_dir = os.path.join(temp_project_dir, ".practices")
    system_instructions_path = os.path.join(practices_dir, "system_instructions.md")
    
    assert os.path.exists(practices_dir)
    assert os.path.exists(system_instructions_path)


@pytest.mark.asyncio
async def test_get_system_instructions_uses_existing_file(temp_project_dir):
    """Test that get_system_instructions uses an existing file."""
    # Create .practices directory
    practices_dir = os.path.join(temp_project_dir, ".practices")
    os.makedirs(practices_dir, exist_ok=True)
    
    # Create custom system instructions file
    system_instructions_path = os.path.join(practices_dir, "system_instructions.md")
    custom_content = "# Custom System Instructions\n\nThis is a custom file."
    
    with open(system_instructions_path, 'w') as f:
        f.write(custom_content)
    
    # Get system instructions
    instructions = await get_system_instructions(temp_project_dir)
    
    # Verify custom content was returned
    assert instructions == custom_content


def test_system_instructions_template_exists():
    """Test that the system instructions template file exists."""
    # Get the location of the mcp_server.py file
    mcp_server_path = Path(__file__).parent.parent.parent / "src" / "mcp_server_practices" / "mcp_server.py"
    template_path = Path(mcp_server_path).parent / "templates" / "system_instructions.md"
    
    assert template_path.exists()
    
    # Read the template file
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Verify it contains expected content
    assert "# Practices MCP Server - System Instructions" in content
    assert "## Available MCP Tools" in content
    assert "## Development Practices Guidelines" in content
