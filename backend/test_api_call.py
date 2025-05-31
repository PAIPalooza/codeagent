"""
Test script to verify direct API calls to the Cody AI Development Platform.
"""

import asyncio
import json
import logging
import os
import sys

from dotenv import load_dotenv
import httpx

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def test_direct_api_call():
    """Test a direct call to the Cody AI Development Platform API."""
    base_url = os.environ.get("AINATIVE_BASE_URL", "https://api.ainative.studio/api/v1")
    api_key = os.environ.get("AINATIVE_API_KEY")
    
    if not api_key or api_key == "your_ainative_api_key_here":
        logger.error("No valid API key found in environment variables")
        return
    
    logger.info(f"API Key: {api_key[:5]}...{api_key[-3:]} (masked)")
    logger.info(f"Base URL: {base_url}")
    
    # Test endpoint: ai/analyze
    endpoint = "ai/analyze"
    url = f"{base_url}/{endpoint}"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "project_name": "API Test Project",
        "description": "A project to test direct API calls",
        "features": ["Test Feature 1", "Test Feature 2"],
        "tech_stack": "Python, FastAPI",
        "generate_code": True
    }
    
    logger.info(f"Making request to: {url}")
    logger.debug(f"Request headers: {headers}")
    logger.debug(f"Request payload: {json.dumps(payload, indent=2)}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, 
                headers=headers, 
                json=payload, 
                timeout=60.0
            )
            
            logger.info(f"Response status code: {response.status_code}")
            logger.debug(f"Response headers: {response.headers}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    logger.info("Response data (truncated):")
                    logger.info(json.dumps(response_data, indent=2)[:500] + "...")
                    return response_data
                except json.JSONDecodeError:
                    logger.error("Failed to decode JSON response")
                    logger.debug(f"Raw response: {response.text[:500]}...")
            else:
                logger.error(f"Request failed with status code: {response.status_code}")
                logger.debug(f"Response text: {response.text[:500]}...")
                
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e}")
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(test_direct_api_call())
