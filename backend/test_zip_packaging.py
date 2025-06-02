#!/usr/bin/env python3
"""
Test script for ZIP packaging functionality (US1.8).

This script verifies that:
1. The project files are properly zipped after execution
2. The project record is updated with the download URL and status
3. The download endpoint returns the ZIP file correctly
"""

import os
import time
import zipfile
import tempfile
import httpx
import asyncio
import logging
import shutil
import json

# Import ProjectStatus enum for status checking
from app.models.project import ProjectStatus

from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import models - adjust import path if needed
from app.models.project import Project, ProjectStatus

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to see all logs
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_zip_packaging.log')
    ]
)
logger = logging.getLogger(__name__)

# Enable HTTP request/response logging
logging.getLogger('httpcore').setLevel(logging.DEBUG)
logging.getLogger('httpx').setLevel(logging.DEBUG)
logging.getLogger('urllib3').setLevel(logging.DEBUG)

# API URL
BASE_URL = "http://localhost:8000"
HEALTH_CHECK_ENDPOINT = f"{BASE_URL}/health"
GENERATE_APP_ENDPOINT = f"{BASE_URL}/api/v1/generate-app"
# Project endpoints are at /projects
PROJECT_ENDPOINT = f"{BASE_URL}/projects/"  # Will append project ID

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API routes are defined directly in main.py without a prefix


async def create_generation_steps(client, project_id):
    """Create test generation steps for a project."""
    try:
        # Define test steps
        steps = [
            {
                "project_id": project_id,
                "sequence_order": 1,
                "tool_name": "codegen_create",
                "input_payload": {"file_path": "src/App.js", "content": "console.log('Hello World');"},
                "status": "pending"
            },
            {
                "project_id": project_id,
                "sequence_order": 2,
                "tool_name": "codegen_create",
                "input_payload": {"file_path": "src/index.js", "content": "import App from './App';"},
                "status": "pending"
            }
        ]
        
        # Create each step via API
        for step in steps:
            response = await client.post(
                f"{BASE_URL}/projects/{project_id}/steps", 
                json=step
            )
            
            if response.status_code != 201:
                logger.error(f"Failed to create step: {response.status_code} - {response.text}")
                return False
        
        logger.info(f"Successfully created {len(steps)} generation steps for project {project_id}")
        return True
    except Exception as e:
        logger.error(f"Error creating generation steps: {str(e)}")
        return False


async def test_zip_packaging():
    """Test the ZIP packaging functionality."""
    async with httpx.AsyncClient() as client:
        # Step 1: Verify server is running
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code != 200:
                logger.error(f"Server health check failed: {response.status_code} - {response.text}")
                return False
            
            health_data = response.json()
            logger.info(f"Server health check passed: {health_data}")
            
            # Validate health data structure
            if not isinstance(health_data, dict) or 'status' not in health_data:
                logger.error(f"Invalid health response format: {health_data}")
                return False
        except Exception as e:
            logger.error(f"Server connection error: {str(e)}")
            return False

        # Step 2: Create a test project
        try:
            # Create project using the app generation endpoint
            project_data = {
                "project_name": f"test_project_{int(time.time())}",
                "description": "Test project for ZIP packaging",
                "features": ["user authentication", "file upload"],
                "tech_stack": "React + FastAPI + PostgreSQL",
                "styling": "tailwind"
            }
            
            # Create the project via the generate-app endpoint
            response = await client.post(
                f"{BASE_URL}/api/v1/generate-app",
                json=project_data
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to create project: {response.status_code} - {response.text}")
                return False
            
            logger.info(f"Project generation started with status code {response.status_code}")
            
            result = response.json()
            project_id = result.get("project_id")
            
            if not project_id:
                logger.error("Project ID not found in response")
                return False
                
            logger.info(f"Project generation started with ID: {project_id}")
            
            # Instead of creating steps manually, the generate-app endpoint should have created them
            # We'll verify the project was created and then proceed with execution
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            return False

        # Step 3: The generate-app endpoint should have triggered execution automatically
        # We'll just wait for the project to complete
        logger.info("Waiting for project generation to complete...")

        # Step 4: Wait for processing to complete (poll project status)
        max_attempts = 30  # Increased timeout for generation
        attempt = 0
        download_url = None
        
        while attempt < max_attempts:
            try:
                # Get project status using the projects endpoint
                project_url = f"{PROJECT_ENDPOINT}{project_id}"
                response = await client.get(project_url)
                
                project = response.json()
                logger.info(f"Project data: {json.dumps(project, indent=2, default=str)}")
                logger.info(f"Project status: {project.get('status')}")
                logger.info(f"Project download_url in response: {project.get('download_url')}")
                
                # Log all fields in the project response
                logger.info("All fields in project response:")
                for key, value in project.items():
                    logger.info(f"  {key}: {value}")
                
                if project.get('status') == ProjectStatus.SUCCESS.value and project.get('download_url'):
                    download_url = project.get('download_url')
                    logger.info(f"Project completed with download URL: {download_url}")
                    break
                    
                    logger.warning(f"Unexpected project status: {status_value}")
                    logger.warning(f"Project data: {project_data}")
                    
                # Wait before next attempt
                attempt += 1
                await asyncio.sleep(2)  # Wait 2 seconds before next check
                
            except Exception as e:
                logger.error(f"Error checking project status: {str(e)}")
                await asyncio.sleep(2)
                attempt += 1
        
        if not download_url:
            logger.error(f"Project did not complete within the timeout period")
            return False, {"error": "Project did not complete within the timeout period"}
        
        # Step 5: Download the ZIP file
        try:
            # Extract the filename from the download URL
            zip_filename = os.path.basename(download_url)
            
            # Make sure the download URL is correct format
            # Per app_generation.py, the download URL starts with /api/v1/downloads/
            if not download_url or not download_url.startswith("/api/v1/downloads/"):
                logger.error(f"Download URL format is incorrect: {download_url}")
                return False
            
            # Request the ZIP file
            download_response = await client.get(f"{BASE_URL}{download_url}", timeout=30)
            
            if download_response.status_code != 200:
                logger.error(f"Failed to download ZIP: {download_response.status_code} - {download_response.text}")
                return False
                
            if download_response.headers.get("content-type") != "application/zip":
                logger.error(f"Response is not a ZIP file: {download_response.headers.get('content-type')}")
                return False
            
            # Save the ZIP file locally
            download_dir = Path("test_downloads")
            download_dir.mkdir(exist_ok=True)
            local_zip_path = download_dir / zip_filename
            
            with open(local_zip_path, "wb") as f:
                f.write(download_response.content)
            
            logger.info(f"Downloaded ZIP file to {local_zip_path}")
            
            # Verify the ZIP file is valid
            if not zipfile.is_zipfile(local_zip_path):
                logger.error(f"Downloaded file is not a valid ZIP file")
                return False
            
            # Extract the ZIP to verify contents
            extract_dir = download_dir / f"extracted_{project_data['name']}"
            extract_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(local_zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Check if at least one file was extracted
            extracted_files = list(extract_dir.glob("**/*"))
            if not extracted_files:
                logger.error("ZIP file did not contain any files")
                return False
            
            logger.info(f"Successfully extracted {len(extracted_files)} files from ZIP")
            
            # Clean up
            if local_zip_path.exists():
                local_zip_path.unlink()
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            
            logger.info("Test completed successfully - All acceptance criteria met!")
            # All checks passed
            return True
            
        except Exception as e:
            logger.error(f"Error downloading or processing ZIP file: {str(e)}")
            return False


if __name__ == "__main__":
    logger.info("Starting ZIP packaging test...")
    result = asyncio.run(test_zip_packaging())
    if result:
        logger.info("✅ All tests passed. US1.8 acceptance criteria verified.")
    else:
        logger.error("❌ Tests failed. Check logs for details.")
