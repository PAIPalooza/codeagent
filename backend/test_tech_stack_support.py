#!/usr/bin/env python3
"""
Test script for validating tech stack support.

This script tests the different tech stacks to ensure they generate appropriate plans.
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ollama_service import OllamaService


async def test_tech_stack(service, project_name, description, features, tech_stack, styling):
    """Test a specific tech stack configuration."""
    print(f"\n🧪 Testing {tech_stack}")
    print(f"Project: {project_name}")
    print(f"Features: {', '.join(features)}")
    print(f"Styling: {styling}")
    
    try:
        plan = service.generate_app_plan(
            project_name=project_name,
            description=description,
            features=features,
            tech_stack=tech_stack,
            styling=styling
        )
        
        print(f"✅ Generated plan with {len(plan)} steps:")
        for i, step in enumerate(plan):
            tool = step.get('tool', 'unknown')
            template = step.get('input', {}).get('template', 'unknown')
            file_path = step.get('input', {}).get('file_path', 'unknown')
            print(f"  {i+1}. {tool} -> {template} -> {file_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        return False


async def main():
    """Main test function."""
    print("🚀 Testing Tech Stack Support")
    print("=" * 50)
    
    # Initialize the Ollama service
    service = OllamaService()
    
    # Check if Ollama is available
    if not service.health_check():
        print("⚠️  Ollama is not available. Testing fallback plans only.")
    else:
        print("✅ Ollama is available")
    
    # Test configurations
    test_configs = [
        {
            "project_name": "ReactTodoApp",
            "description": "A todo application with user authentication",
            "features": ["User authentication", "Task CRUD", "Dashboard"],
            "tech_stack": "React + FastAPI + PostgreSQL",
            "styling": "TailwindCSS"
        },
        {
            "project_name": "VueNotesApp",
            "description": "A notes application with user management",
            "features": ["User management", "Note CRUD", "Search functionality"],
            "tech_stack": "Vue + Node.js + MongoDB",
            "styling": "Bootstrap"
        },
        {
            "project_name": "NextBlogApp",
            "description": "A blog application with SSR",
            "features": ["Blog posts", "User comments", "Admin panel"],
            "tech_stack": "Next.js + Django + MySQL",
            "styling": "Plain CSS"
        }
    ]
    
    # Run tests
    results = []
    for config in test_configs:
        success = await test_tech_stack(service, **config)
        results.append((config['tech_stack'], success))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for tech_stack, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {tech_stack}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))