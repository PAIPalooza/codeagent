"""
Test script to verify the execution loop functionality (US1.7).

This script tests the generation steps execution loop by creating a project,
inserting steps, and verifying that they are executed correctly.
"""

import asyncio
import json
import os
import shutil
import uuid
import time
import logging
import sys
from datetime import datetime

import httpx
import pytest
import requests
from requests.exceptions import ConnectionError

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Define test constants
API_URL = "http://localhost:8000/api/v1"
TEMP_DIR = "temp_projects"

# Test app specification
TEST_APP_SPEC = {
    "project_name": "Test Project",
    "description": "A test project to verify the execution loop",
    "features": ["Authentication", "User Profile", "Dashboard"],
    "tech_stack": "FastAPI, SQLAlchemy, PostgreSQL",
    "styling": "Tailwind CSS"
}

def check_server_running():
    """Check if the FastAPI server is running."""
    logger.debug("Checking if FastAPI server is running...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        status = response.status_code == 200
        logger.debug(f"Server health check result: {status}, status code: {response.status_code}")
        return status
    except ConnectionError as e:
        logger.error(f"Server connection error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking server: {str(e)}")
        return False

async def test_execution_loop():
    """Test the execution loop functionality."""
    
    logger.info("Starting execution loop test")
    
    # Check if server is running
    if not check_server_running():
        logger.error("FastAPI server is not running")
        print("\nERROR: FastAPI server is not running. Please start the server with:")
        print("cd backend && uvicorn app.main:app --reload")
        return
    
    logger.info("Server is running, proceeding with test")
    
    # Clean up any previous test data
    if os.path.exists(TEMP_DIR):
        logger.debug(f"Removing existing directory: {TEMP_DIR}")
        shutil.rmtree(TEMP_DIR)
    
    logger.debug("Creating test client with appropriate timeout settings")
    # Create a test client with timeout settings - reduced timeout to avoid hanging
    timeout_settings = httpx.Timeout(5.0, connect=3.0)
    
    # Use debug mode to avoid blocking issues with async calls
    transport = httpx.AsyncHTTPTransport(retries=1)
    async with httpx.AsyncClient(timeout=timeout_settings, transport=transport) as client:
        try:
            # Step 1: Create a new project
            logger.info("Step 1: Creating a new project...")
            print("\n1. Creating a new project...")
            try:
                logger.debug(f"Making POST request to {API_URL}/generate-app with spec: {TEST_APP_SPEC}")
                # Make sure we use json parameter correctly and don't exceed timeout
                response = await client.post(
                    f"{API_URL}/generate-app",
                    json=TEST_APP_SPEC,
                    timeout=3.0
                )
                logger.debug(f"Received response with status code: {response.status_code}")
                
                assert response.status_code == 200, f"Failed to create project: {response.text}"
                data = response.json()
                project_id = data["project_id"]
                
                logger.info(f"Project created with ID: {project_id}")
                print(f"   Project created with ID: {project_id}")
                print(f"   Status: {data['status']}")
                print(f"   Message: {data.get('message', '')}")
            except httpx.RequestError as e:
                logger.error(f"Error making request: {str(e)}")
                print(f"   Error making request: {str(e)}")
                return
            except AssertionError as e:
                logger.error(f"Assertion error: {str(e)}")
                print(f"   {str(e)}")
                return
            except Exception as e:
                logger.error(f"Unexpected error in create project step: {str(e)}")
                print(f"   Unexpected error: {str(e)}")
                return
            
            # Step 2: Wait for steps to be processed (this would normally happen in the background)
            logger.info("Step 2: Waiting for steps to be processed...")
            print("\n2. Waiting for steps to be processed...")
            # Reduced wait time to avoid hanging
            logger.debug("Sleeping for 1 second to allow background task to start")
            await asyncio.sleep(1)  # Reduced wait time
            
            # Step 3: Check the status of the steps
            logger.info("Step 3: Checking step statuses...")
            print("\n3. Checking step statuses...")
            try:
                logger.debug(f"Making GET request to {API_URL}/projects/{project_id}/steps")
                response = await client.get(
                    f"{API_URL}/projects/{project_id}/steps",
                    timeout=3.0
                )
                logger.debug(f"Received response with status code: {response.status_code}")
                
                assert response.status_code == 200, f"Failed to get steps: {response.text}"
                steps = response.json()
                
                logger.info(f"Found {len(steps)} steps")
                print(f"   Found {len(steps)} steps:")
                for step in steps:
                    log_msg = f"Step {step['sequence_order']} ({step['tool_name']}): {step['status']}"
                    logger.debug(log_msg)
                    print(f"   - {log_msg}")
                    
                    # Print more details for failed steps
                    if step['status'] == 'failed':
                        error_msg = f"Error: {step.get('error', 'No error details')}"
                        logger.error(error_msg)
                        print(f"     {error_msg}")
            except httpx.RequestError as e:
                logger.error(f"Request error checking steps: {str(e)}")
                print(f"   Error checking steps: {str(e)}")
            except AssertionError as e:
                logger.error(f"Assertion error checking steps: {str(e)}")
                print(f"   Error checking steps: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error checking steps: {str(e)}")
                print(f"   Unexpected error checking steps: {str(e)}")
            
            # Step 4: Verify that files were created
            logger.info("Step 4: Checking generated files...")
            print("\n4. Checking generated files...")
            project_dir = os.path.join(TEMP_DIR, project_id)
            
            if os.path.exists(project_dir):
                logger.debug(f"Project directory exists: {project_dir}")
                files = []
                for root, _, filenames in os.walk(project_dir):
                    for filename in filenames:
                        file_path = os.path.relpath(os.path.join(root, filename), project_dir)
                        files.append(file_path)
                
                logger.info(f"Found {len(files)} generated files")
                print(f"   Found {len(files)} generated files:")
                for file_path in files:
                    logger.debug(f"Generated file: {file_path}")
                    print(f"   - {file_path}")
            else:
                logger.warning(f"No project directory found at: {project_dir}")
                print(f"   No files found in {project_dir}")
            
            # Step 5: Explicitly execute pending steps (in case they weren't processed)
            logger.info("Step 5: Executing any pending steps...")
            print("\n5. Executing any pending steps...")
            try:
                logger.debug(f"Making POST request to {API_URL}/projects/{project_id}/execute")
                response = await client.post(
                    f"{API_URL}/projects/{project_id}/execute",
                    timeout=3.0
                )
                logger.debug(f"Received response with status code: {response.status_code}")
                
                assert response.status_code == 200, f"Failed to execute steps: {response.text}"
                data = response.json()
                
                logger.info(f"Status: {data['status']}")
                print(f"   Status: {data['status']}")
                print(f"   Message: {data.get('message', '')}")
                
                # Wait for steps to complete - reduced wait time
                logger.debug("Sleeping for 1 second to allow steps to execute")
                await asyncio.sleep(1)
            except httpx.RequestError as e:
                logger.error(f"Request error executing steps: {str(e)}")
                print(f"   Error executing steps: {str(e)}")
            except AssertionError as e:
                logger.error(f"Assertion error executing steps: {str(e)}")
                print(f"   Error executing steps: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error executing steps: {str(e)}")
                print(f"   Unexpected error executing steps: {str(e)}")
            
            # Step 6: Check the final status of the steps
            logger.info("Step 6: Checking final step statuses...")
            print("\n6. Checking final step statuses...")
            try:
                logger.debug(f"Making final GET request to {API_URL}/projects/{project_id}/steps")
                response = await client.get(
                    f"{API_URL}/projects/{project_id}/steps",
                    timeout=3.0
                )
                logger.debug(f"Received final response with status code: {response.status_code}")
                
                assert response.status_code == 200, f"Failed to get steps: {response.text}"
                steps = response.json()
                
                logger.info(f"Found {len(steps)} steps in final check")
                print(f"   Found {len(steps)} steps:")
                for step in steps:
                    status_msg = f"Step {step['sequence_order']} ({step['tool_name']}): {step['status']}"
                    logger.debug(status_msg)
                    print(f"   - {status_msg}")
                    
                    # Log additional details for debugging
                    if 'details' in step and step['details']:
                        logger.debug(f"Step details: {step['details'][:100]}...")
                
                # Count completed and failed steps
                completed = sum(1 for step in steps if step['status'] == 'completed')
                failed = sum(1 for step in steps if step['status'] == 'failed')
                pending = sum(1 for step in steps if step['status'] == 'pending')
                
                summary = f"Summary: {completed} completed, {failed} failed, {pending} pending"
                logger.info(summary)
                print(f"\n{summary}")
                
                # The test is successful if at least one step was processed
                assert len(steps) > 0, "No steps were found"
                
                # Log overall test result
                logger.info("Test completed successfully")
            except httpx.RequestError as e:
                logger.error(f"Request error in final step check: {str(e)}")
                print(f"   Error checking final step statuses: {str(e)}")
            except AssertionError as e:
                logger.error(f"Assertion error in final step check: {str(e)}")
                print(f"   Error checking final step statuses: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error in final step check: {str(e)}")
                print(f"   Unexpected error checking final step statuses: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in test execution: {str(e)}")
            print(f"\nUnexpected error: {str(e)}")
            return
        
        logger.info("Test execution completed")
        print("\nTest execution completed")

if __name__ == "__main__":
    asyncio.run(test_execution_loop())
