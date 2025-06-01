#!/usr/bin/env python3
"""
Test script for status logging and streaming endpoints in CodeAgent.

This script tests the new endpoints for status logging and streaming functionality
as implemented for US1.9: Status Logging & Streaming.
"""

import requests
import json
import sys
import time
import os
import sseclient

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

def test_generate_app_with_logs():
    """Test the /generate-app endpoint with logs in response."""
    print("Testing /generate-app endpoint with logs...")
    
    # Sample app specification
    app_spec = {
        "project_name": "test_logging_project",
        "description": "A test project for logging",
        "features": ["Authentication", "User Profile", "Dashboard"],
        "tech_stack": "react-fastapi",
        "styling": "tailwind"
    }
    
    try:
        # Send request to generate app
        response = requests.post(f"{BASE_URL}/generate-app", json=app_spec, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        # Check if we got logs in the response
        assert 'logs' in result, "No logs in response"
        assert isinstance(result['logs'], list), "Logs should be a list"
        print(f"✓ Successfully received {len(result['logs'])} initial logs")
        
        return result['project_id']
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return None

def test_get_project_logs(project_id):
    """Test the /projects/{project_id}/logs endpoint."""
    if not project_id:
        print("Skipping get project logs test - no project ID")
        return
        
    print(f"\nTesting /projects/{project_id}/logs endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/projects/{project_id}/logs", timeout=10)
        response.raise_for_status()
        
        logs = response.json()
        print(f"Retrieved {len(logs)} log entries")
        
        # Print the first few logs if available
        for i, log in enumerate(logs[:3]):
            print(f"Log {i+1}: {log.get('message')}")
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error getting project logs: {e}")
        return False

def test_stream_project_logs(project_id):
    """Test the /projects/{project_id}/logs/stream endpoint with SSE."""
    if not project_id:
        print("Skipping stream logs test - no project ID")
        return
        
    print(f"\nTesting /projects/{project_id}/logs/stream endpoint...")
    
    try:
        # Make the SSE request
        response = requests.get(
            f"{BASE_URL}/projects/{project_id}/logs/stream",
            stream=True,
            headers={'Accept': 'text/event-stream'},
            timeout=30
        )
        response.raise_for_status()
        
        # Create an SSE client
        client = sseclient.SSEClient(response)
        
        print("Connected to SSE stream. Waiting for events... (press Ctrl+C to stop)")
        
        # Process events
        try:
            for event in client.events():
                try:
                    data = json.loads(event.data)
                    print(f"\nNew event: {event.event if hasattr(event, 'event') else 'message'}")
                    print(f"Data: {json.dumps(data, indent=2)}")
                    
                    # Check if this is a close event
                    if hasattr(event, 'event') and event.event == 'close':
                        print("Received close event, ending stream")
                        break
                        
                except json.JSONDecodeError:
                    print(f"Received non-JSON data: {event.data}")
                
                # Small delay to prevent high CPU usage
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nStopped by user")
        except Exception as e:
            print(f"Error processing SSE stream: {e}")
        finally:
            client.close()
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to SSE stream: {e}")
        return False

def main():
    """Run all tests."""
    print("=== Starting Status Logging Tests ===\n")
    
    # Test 1: Generate app and get initial logs
    project_id = test_generate_app_with_logs()
    
    if not project_id:
        print("\n✗ Failed to start project generation")
        return
    
    # Give the backend a moment to start processing
    print("\nWaiting a moment for backend to start processing...")
    time.sleep(2)
    
    # Test 2: Get project logs
    test_get_project_logs(project_id)
    
    # Test 3: Stream logs with SSE
    test_stream_project_logs(project_id)
    
    print("\n=== Tests completed ===")

if __name__ == "__main__":
    main()
