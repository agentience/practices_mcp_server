#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2025 Agentience
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Tests for the file logging functionality in the MCP server.
"""

import os
import tempfile
import logging
import pytest
from pathlib import Path

from mcp_server_practices.mcp_server import setup_file_logging, find_project_root


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up
    try:
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(temp_dir)
    except Exception as e:
        print(f"Failed to clean up temp directory: {e}")


class TestFileLogging:
    """Test cases for file logging functionality."""

    def test_setup_file_logging_default_path(self, temp_dir):
        """Test setting up file logging with default path."""
        # Ensure we're using a fresh logger
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            
        # Configure basic logging first
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s %(message)s',
            datefmt='%m/%d/%y %H:%M:%S'
        )
        
        # Set up logging
        handler = setup_file_logging(
            logging_level=logging.INFO,
            project_root=temp_dir
        )

        # Verify handler was created
        assert handler is not None
        
        # Verify log file was created in .practices directory
        practices_dir = os.path.join(temp_dir, ".practices")
        log_file = os.path.join(practices_dir, "server.log")
        assert os.path.exists(practices_dir)
        assert os.path.exists(log_file)
        
        # Create a logger specifically for this test
        test_logger = logging.getLogger("test_default_path")
        test_logger.setLevel(logging.INFO)
        test_logger.addHandler(handler)
        
        # Write a log message
        test_message = "Test log message for default path - unique ID"
        test_logger.info(test_message)
        
        # Force flush the handler to ensure the message is written
        handler.flush()
        
        # Verify message was written to file
        with open(log_file, 'r') as f:
            content = f.read()
            assert test_message in content
        
        # Clean up - remove handler to release file
        logging.getLogger().removeHandler(handler)
        handler.close()

    def test_setup_file_logging_custom_path(self, temp_dir):
        """Test setting up file logging with custom path."""
        # Ensure we're using a fresh logger
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            
        # Configure basic logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='[%(asctime)s] %(levelname)s %(message)s',
            datefmt='%m/%d/%y %H:%M:%S'
        )
            
        # Create a custom log path
        custom_log_path = os.path.join(temp_dir, "custom", "logs", "server.log")
        
        # Set up logging
        handler = setup_file_logging(
            logging_level=logging.DEBUG,
            log_file_path=custom_log_path
        )
        
        # Verify handler was created
        assert handler is not None
        
        # Verify log file was created at custom path
        assert os.path.exists(custom_log_path)
        
        # Create a logger specifically for this test
        test_logger = logging.getLogger("test_custom_path")
        test_logger.setLevel(logging.DEBUG)
        test_logger.addHandler(handler)
        
        # Write a log message
        test_message = "Custom path test message - unique identifier"
        test_logger.debug(test_message)
        
        # Force flush the handler to ensure the message is written
        handler.flush()
        
        # Verify message was written to file
        with open(custom_log_path, 'r') as f:
            content = f.read()
            assert test_message in content
        
        # Clean up - remove handler to release file
        logging.getLogger().removeHandler(handler)
        handler.close()

    def test_setup_file_logging_error_handling(self, monkeypatch):
        """Test error handling in file logging setup."""
        # Mock os.makedirs to raise an error
        def mock_makedirs(*args, **kwargs):
            raise PermissionError("Permission denied")
        
        monkeypatch.setattr(os, "makedirs", mock_makedirs)
        
        # Set up logging - should handle the error gracefully
        handler = setup_file_logging(
            logging_level=logging.ERROR,
            project_root="/nonexistent/path"
        )
        
        # Verify handler is None due to the error
        assert handler is None

    def test_find_project_root_with_marker(self, temp_dir):
        """Test finding project root with a marker file."""
        # Create a marker file
        marker_path = os.path.join(temp_dir, "pyproject.toml")
        with open(marker_path, 'w') as f:
            f.write("# Test marker file")
        
        # Find project root
        root = find_project_root(temp_dir)
        
        # On macOS, temp_dir might resolve differently, so we should check
        # that the returned path contains the expected path, or is the resolved version
        # of the expected path
        real_temp_dir = os.path.realpath(temp_dir)
        
        # Verify either paths are equal or resolved paths are equal
        assert root == temp_dir or root == real_temp_dir

    def test_find_project_root_no_marker(self, temp_dir):
        """Test finding project root without a marker file."""
        # Find project root from a subdirectory
        subdir = os.path.join(temp_dir, "subdir")
        os.makedirs(subdir, exist_ok=True)
        
        # Find project root - should return the subdir since no markers are found
        root = find_project_root(subdir)
        
        # Without markers, it should return the start path
        assert root == subdir
