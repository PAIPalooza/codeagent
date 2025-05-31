#!/usr/bin/env python3
"""Test script for AINative tool wrappers.

This script validates that the AINative tool wrappers can be imported and called
with dummy data, returning either a valid response or a structured error object.
"""

import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

import pytest
import pytest_asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the tool wrappers
from tools.code_gen_create_tool import CodeGenCreateTool
from tools.code_gen_refactor_tool import CodeGenRefactorTool
from tools.memory_store_tool import MemoryStoreTool
from tools.memory_search_tool import MemorySearchTool

@pytest.mark.asyncio
async def test_code_gen_create_tool() -> None:
    """Test the CodeGenCreateTool with dummy data."""
    logger.info("Testing CodeGenCreateTool...")
    
    # Create an instance
    try:
        tool = CodeGenCreateTool()
        
        # Call with dummy data
        result = await tool._call(
            project_name="Test Project",
            description="A test project for validating the tool wrapper",
            features=["Login", "Dashboard", "Settings"],
            tech_stack="React + FastAPI + PostgreSQL"
        )
        
        # Check if the result is valid
        if "error" in result and result["error"]:
            logger.warning(f"CodeGenCreateTool returned an error: {result['message']}")
            assert "message" in result, "Error response should contain a message"
        else:
            logger.info("CodeGenCreateTool returned a valid response")
            
        # Log the result structure
        logger.info(f"Response structure: {json.dumps({k: type(v).__name__ for k, v in result.items()}, indent=2)}")
        
    except Exception as e:
        logger.error(f"Error testing CodeGenCreateTool: {e}", exc_info=True)
        pytest.fail(f"Exception occurred: {str(e)}")


@pytest.mark.asyncio
async def test_code_gen_refactor_tool() -> None:
    """Test the CodeGenRefactorTool with dummy data."""
    logger.info("Testing CodeGenRefactorTool...")
    
    # Create an instance
    try:
        tool = CodeGenRefactorTool()
        
        # Sample code to refactor
        code = """
        def add(a, b):
            return a + b
        """
        
        # Call with dummy data
        result = await tool._call(
            code=code,
            instructions="Add type hints to the function",
            file_path="math_utils.py",
            language="python"
        )
        
        # Check if the result is valid
        if "error" in result and result["error"]:
            logger.warning(f"CodeGenRefactorTool returned an error: {result['message']}")
            assert "message" in result, "Error response should contain a message"
        else:
            logger.info("CodeGenRefactorTool returned a valid response")
            
        # Log the result structure
        logger.info(f"Response structure: {json.dumps({k: type(v).__name__ for k, v in result.items()}, indent=2)}")
        
    except Exception as e:
        logger.error(f"Error testing CodeGenRefactorTool: {e}", exc_info=True)
        pytest.fail(f"Exception occurred: {str(e)}")


@pytest.mark.asyncio
async def test_memory_store_tool() -> None:
    """Test the MemoryStoreTool with dummy data."""
    logger.info("Testing MemoryStoreTool...")
    
    # Create an instance
    try:
        tool = MemoryStoreTool()
        
        # Call with dummy data
        result = await tool._call(
            content="This is a test memory content",
            title="Test Memory",
            tags=["test", "memory", "validation"],
            project_id="test-project-123"
        )
        
        # Check if the result is valid
        if "error" in result and result["error"]:
            logger.warning(f"MemoryStoreTool returned an error: {result['message']}")
            assert "message" in result, "Error response should contain a message"
        else:
            logger.info("MemoryStoreTool returned a valid response")
            
        # Log the result structure
        logger.info(f"Response structure: {json.dumps({k: type(v).__name__ for k, v in result.items()}, indent=2)}")
        
    except Exception as e:
        logger.error(f"Error testing MemoryStoreTool: {e}", exc_info=True)
        pytest.fail(f"Exception occurred: {str(e)}")


@pytest.mark.asyncio
async def test_memory_search_tool() -> None:
    """Test the MemorySearchTool with dummy data."""
    logger.info("Testing MemorySearchTool...")
    
    # Create an instance
    try:
        tool = MemorySearchTool()
        
        # Call with dummy data
        result = await tool._call(
            query="test memory",
            project_id="test-project-123",
            tags=["test", "memory"],
            limit=5
        )
        
        # Check if the result is valid
        if "error" in result and result["error"]:
            logger.warning(f"MemorySearchTool returned an error: {result['message']}")
            assert "message" in result, "Error response should contain a message"
        else:
            logger.info("MemorySearchTool returned a valid response")
            
        # Log the result structure
        logger.info(f"Response structure: {json.dumps({k: type(v).__name__ for k, v in result.items()}, indent=2)}")
        
    except Exception as e:
        logger.error(f"Error testing MemorySearchTool: {e}", exc_info=True)
        pytest.fail(f"Exception occurred: {str(e)}")

# Add conftest.py configuration for pytest-asyncio
'''
To configure pytest-asyncio properly, create a conftest.py with:

import pytest

pytest_plugins = ["pytest_asyncio"]

@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
'''

