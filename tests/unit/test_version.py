"""Tests for the version module."""

import pytest

from mcp_server_practices import __version__


def test_version():
    """Test that version is a string."""
    assert isinstance(__version__, str)
    assert __version__ == "0.2.0"
