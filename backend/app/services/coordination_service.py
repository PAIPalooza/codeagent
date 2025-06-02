"""
Multi-Agent Coordination Service

This service orchestrates multiple specialized agents for complex code generation tasks
using AINative's orchestration APIs.
"""

import logging
import asyncio
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))
from tools.coordination_tool import CoordinationTool

logger = logging.getLogger(__name__)


class CoordinationService:
    """Service for coordinating multiple agents in code generation workflows."""
    
    def __init__(self):
        self.coordination_tool = CoordinationTool()
        
    async def create_generation_workflow(self, project_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a multi-agent workflow for code generation.
        
        Args:
            project_spec: Project specification including features, tech stack, etc.
            
        Returns:
            Dictionary containing workflow_id and status
        """
        try:
            logger.info("Creating multi-agent code generation workflow")
            
            # Build workflow based on tech stack and requirements
            workflow_payload = self._build_workflow_payload(project_spec)
            
            # Create workflow using AINative orchestration
            response = await self.coordination_tool.create_sequence(workflow_payload)
            
            if response.get("success"):
                workflow_id = response.get("data", {}).get("workflow_id")
                logger.info(f"Created workflow: {workflow_id}")
                
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "estimated_duration": response.get("data", {}).get("estimated_duration"),
                    "agents": workflow_payload["agents"],
                    "created_at": datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"Failed to create workflow: {response.get('message')}")
                return response
                
        except Exception as e:
            logger.error(f"Error creating coordination workflow: {str(e)}")
            return {"error": True, "message": str(e)}
    
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a created workflow.
        
        Args:
            workflow_id: ID of the workflow to execute
            
        Returns:
            Dictionary containing execution status
        """
        try:
            logger.info(f"Executing workflow: {workflow_id}")
            
            response = self.coordination_tool.execute_sequence(workflow_id)
            
            if response.get("success"):
                logger.info(f"Started execution of workflow: {workflow_id}")
                return response
            else:
                logger.error(f"Failed to execute workflow: {response.get('message')}")
                return response
                
        except Exception as e:
            logger.error(f"Error executing workflow: {str(e)}")
            return {"error": True, "message": str(e)}
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get the current status of a workflow.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Dictionary containing workflow status and progress
        """
        try:
            response = self.coordination_tool.get_sequence_status(workflow_id)
            
            if response.get("success"):
                return response
            else:
                logger.error(f"Failed to get workflow status: {response.get('message')}")
                return response
                
        except Exception as e:
            logger.error(f"Error getting workflow status: {str(e)}")
            return {"error": True, "message": str(e)}
    
    async def wait_for_completion(self, workflow_id: str, max_wait_time: int = 1800) -> Dict[str, Any]:
        """
        Wait for a workflow to complete.
        
        Args:
            workflow_id: ID of the workflow
            max_wait_time: Maximum time to wait in seconds
            
        Returns:
            Final workflow status
        """
        try:
            logger.info(f"Waiting for workflow completion: {workflow_id}")
            
            response = self.coordination_tool.wait_for_completion(
                workflow_id, 
                max_wait_time=max_wait_time
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error waiting for workflow completion: {str(e)}")
            return {"error": True, "message": str(e)}
    
    def _build_workflow_payload(self, project_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build workflow payload based on project specifications.
        
        Args:
            project_spec: Project specification
            
        Returns:
            Workflow payload for AINative orchestration
        """
        tech_stack = project_spec.get("tech_stack", "React + FastAPI + PostgreSQL")
        features = project_spec.get("features", [])
        styling = project_spec.get("styling", "Tailwind CSS")
        
        # Define agents based on tech stack
        agents = []
        dependencies = {}
        
        # Database Schema Agent (if using database)
        if any(db in tech_stack for db in ["PostgreSQL", "MongoDB", "MySQL"]):
            agents.append({
                "id": "db_schema_agent",
                "type": "database_schema_generation",
                "description": "Generate database schema and models",
                "config": {
                    "database_type": self._extract_database_type(tech_stack),
                    "features": features
                }
            })
        
        # Backend Agent
        backend_type = self._extract_backend_type(tech_stack)
        agents.append({
            "id": "backend_agent", 
            "type": "backend_generation",
            "description": f"Generate {backend_type} backend code",
            "config": {
                "framework": backend_type,
                "features": features,
                "database_integration": len([a for a in agents if a["id"] == "db_schema_agent"]) > 0
            }
        })
        
        # Set backend dependency on database if exists
        if any(a["id"] == "db_schema_agent" for a in agents):
            dependencies["backend_agent"] = ["db_schema_agent"]
        
        # Frontend Agent
        frontend_type = self._extract_frontend_type(tech_stack)
        agents.append({
            "id": "frontend_agent",
            "type": "frontend_generation", 
            "description": f"Generate {frontend_type} frontend code",
            "config": {
                "framework": frontend_type,
                "features": features,
                "styling": styling
            }
        })
        dependencies["frontend_agent"] = ["backend_agent"]
        
        # API Integration Agent
        agents.append({
            "id": "api_integration_agent",
            "type": "api_integration",
            "description": "Connect frontend to backend APIs",
            "config": {
                "frontend_framework": frontend_type,
                "backend_framework": backend_type,
                "features": features
            }
        })
        dependencies["api_integration_agent"] = ["frontend_agent", "backend_agent"]
        
        # Styling Agent
        if styling != "None":
            agents.append({
                "id": "styling_agent",
                "type": "styling_enhancement",
                "description": f"Apply {styling} styling",
                "config": {
                    "styling_framework": styling,
                    "frontend_framework": frontend_type
                }
            })
            dependencies["styling_agent"] = ["frontend_agent"]
        
        # Testing Agent
        agents.append({
            "id": "testing_agent",
            "type": "test_generation",
            "description": "Generate comprehensive tests",
            "config": {
                "test_types": ["unit", "integration"],
                "frameworks": [frontend_type, backend_type]
            }
        })
        dependencies["testing_agent"] = ["api_integration_agent"]
        
        # Packaging Agent
        agents.append({
            "id": "packaging_agent",
            "type": "project_packaging",
            "description": "Package project for deployment",
            "config": {
                "deployment_type": "zip",
                "include_docs": True
            }
        })
        dependencies["packaging_agent"] = ["testing_agent"]
        if styling != "None":
            dependencies["packaging_agent"].append("styling_agent")
        
        return {
            "workflow_name": f"code_generation_{project_spec.get('project_name', 'unnamed')}",
            "description": f"Multi-agent code generation for {tech_stack} project",
            "agents": agents,
            "dependencies": dependencies,
            "timeout": 3600,  # 1 hour timeout
            "metadata": {
                "project_spec": project_spec,
                "created_at": datetime.utcnow().isoformat()
            }
        }
    
    def _extract_database_type(self, tech_stack: str) -> str:
        """Extract database type from tech stack string."""
        if "PostgreSQL" in tech_stack:
            return "postgresql"
        elif "MongoDB" in tech_stack:
            return "mongodb"
        elif "MySQL" in tech_stack:
            return "mysql"
        return "sqlite"
    
    def _extract_backend_type(self, tech_stack: str) -> str:
        """Extract backend framework from tech stack string."""
        if "FastAPI" in tech_stack:
            return "fastapi"
        elif "Django" in tech_stack:
            return "django"
        elif "Node.js" in tech_stack:
            return "express"
        return "fastapi"
    
    def _extract_frontend_type(self, tech_stack: str) -> str:
        """Extract frontend framework from tech stack string."""
        if "React" in tech_stack:
            return "react"
        elif "Vue" in tech_stack:
            return "vue"
        elif "Next.js" in tech_stack:
            return "nextjs"
        return "react"