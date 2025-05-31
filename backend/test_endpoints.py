"""
Test script for the app generation endpoints.

This script tests the /api/v1/generate-app and /api/v1/recall-last-app endpoints.
"""

import httpx
import json
import asyncio
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API endpoint
BASE_URL = "http://localhost:8000"

async def test_generate_app():
    """Test the generate-app endpoint"""
    print("Testing POST /api/v1/generate-app endpoint...")
    
    # Sample app specification
    app_spec = {
        "project_name": "TaskManager",
        "description": "A simple task management application with user authentication",
        "features": [
            "User registration and login",
            "Task creation and management",
            "Task filtering and sorting",
            "User profile management"
        ],
        "tech_stack": {
            "frontend": ["React", "Tailwind CSS"],
            "backend": ["FastAPI", "SQLAlchemy"],
            "database": ["PostgreSQL"]
        },
        "styling": "Tailwind CSS with a clean, modern interface"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/generate-app",
                json=app_spec,
                timeout=30.0
            )
            
            if response.status_code == 200:
                print(f"Success! Status code: {response.status_code}")
                print(f"Response: {json.dumps(response.json(), indent=2)}")
                return response.json()
            else:
                print(f"Error! Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return None

async def test_recall_last_app():
    """Test the recall-last-app endpoint"""
    print("\nTesting GET /api/v1/recall-last-app endpoint...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/recall-last-app",
                timeout=10.0
            )
            
            if response.status_code == 200:
                print(f"Success! Status code: {response.status_code}")
                print(f"Response: {json.dumps(response.json(), indent=2)}")
            else:
                print(f"Error! Status code: {response.status_code}")
                print(f"Response: {response.text}")
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

async def main():
    """Run all tests"""
    # Start by generating an app
    result = await test_generate_app()
    
    if result:
        # Wait a moment for the operation to complete
        print("\nWaiting for 2 seconds...")
        await asyncio.sleep(2)
        
        # Then try to recall it
        await test_recall_last_app()

if __name__ == "__main__":
    asyncio.run(main())
