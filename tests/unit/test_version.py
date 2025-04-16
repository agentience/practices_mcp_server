"""Tests for the version module."""

import pytest

from mcp_server_practices import __version__


def test_version():
    """Test that version is a string."""
    assert isinstance(__version__, str)
    # Version has been updated from 0.2.0 to 0.4.0
    assert __version__ == "0.4.0"
