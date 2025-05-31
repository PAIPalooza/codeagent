#!/usr/bin/env python3
"""
Test script for verifying US1.6: Step Insertion & Status Logging.

This script tests the step insertion functionality of the app generation endpoints
and confirms steps are properly inserted with PENDING status and can be retrieved.
"""

import asyncio
import httpx
import json
import uuid
from pprint import pprint

# Test configuration
BASE_URL = "http://localhost:8000/api/v1"
GENERATE_ENDPOINT = f"{BASE_URL}/generate-app"
STEPS_ENDPOINT = f"{BASE_URL}/project-steps"

# Sample app specification for testing
APP_SPEC = {
    "project_name": "TestStepInsertion",
    "description": "Test project for US1.6 step insertion and status logging",
    "features": ["User authentication", "Data visualization", "API integration"],
    "tech_stack": {
        "frontend": ["React", "TypeScript"],
        "backend": ["FastAPI", "SQLAlchemy"]
    },
    "styling": "Material Design"
}

async def test_generate_app_and_verify_steps():
    """
    Test the app generation endpoint and verify steps are created properly.
    
    This test:
    1. Calls the generate-app endpoint with a test specification
    2. Gets the project_id from the response
    3. Calls project-steps endpoint to verify steps were created with PENDING status
    4. Verifies each step has the correct fields and sequence_order
    """
    print("\n--- Testing US1.6: Step Insertion & Status Logging ---")
    
    # STEP 1: Generate a new app with our test specification
    print("\n1. Generating app with test specification...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                GENERATE_ENDPOINT,
                json=APP_SPEC,
                timeout=60.0  # Increase timeout to 60 seconds
            )
        except httpx.TimeoutException:
            print("ERROR: Request timed out. The server might be processing your request for too long.")
            print("HINT: The first request might take longer due to initialization.")
            print("Try running the test again, or check if the server is running correctly.")
            return False
        
        # Check response status
        if response.status_code != 200:
            print(f"ERROR: Failed to generate app. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        # Get project ID from response
        result = response.json()
        project_id = result.get("project_id")
        status = result.get("status")
        
        print(f"✓ App generation successful")
        print(f"  Project ID: {project_id}")
        print(f"  Status: {status}")
        
        if not project_id:
            print("ERROR: No project_id returned")
            return False
        
        # STEP 2: Verify steps were created for the project
        print("\n2. Verifying generation steps were created...")
        try:
            steps_response = await client.get(
                f"{STEPS_ENDPOINT}/{project_id}",
                timeout=60.0  # Increase timeout to 60 seconds
            )
        except httpx.TimeoutException:
            print("ERROR: Request timed out when fetching steps.")
            print("The server might be processing your request for too long.")
            return False
        
        if steps_response.status_code != 200:
            print(f"ERROR: Failed to retrieve steps. Status: {steps_response.status_code}")
            print(f"Response: {steps_response.text}")
            return False
        
        steps_data = steps_response.json()
        steps = steps_data.get("steps", [])
        
        print(f"✓ Retrieved {len(steps)} generation steps")
        print(f"  Project Name: {steps_data.get('project_name')}")
        print(f"  Project Status: {steps_data.get('project_status')}")
        
        # STEP 3: Verify each step has the correct status and sequence
        print("\n3. Verifying step details...")
        if not steps:
            print("ERROR: No steps found for the project")
            return False
        
        # Verify all steps have PENDING status and correct sequence_order
        all_pending = all(step.get("status") == "PENDING" for step in steps)
        sequence_correct = all(step.get("sequence_order") == i+1 for i, step in enumerate(steps))
        
        if all_pending:
            print("✓ All steps have PENDING status")
        else:
            print("ERROR: Not all steps have PENDING status")
            return False
        
        if sequence_correct:
            print("✓ All steps have correct sequence_order")
        else:
            print("ERROR: Steps have incorrect sequence_order")
            return False
        
        # Print sample step for verification
        print("\nSample step details:")
        pprint(steps[0])
        
        return True

async def main():
    """Run all tests for US1.6"""
    success = await test_generate_app_and_verify_steps()
    
    if success:
        print("\n--- All tests PASSED for US1.6: Step Insertion & Status Logging ---")
    else:
        print("\n--- Some tests FAILED for US1.6: Step Insertion & Status Logging ---")

if __name__ == "__main__":
    asyncio.run(main())
