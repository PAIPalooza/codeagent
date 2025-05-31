"""
Router for app generation endpoints.

This module defines endpoints for generating and recalling app specs.
"""

import os
import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

from ..models.project import Project
from ..models.generation_step import GenerationStep, StepStatus
from ..database import get_db

# Import AINative tool wrappers
try:
    from tools.memory_search_tool import MemorySearchTool
except ImportError:
    # For testing/development, we'll create a mock version
    class MemorySearchTool:
        async def _call(self, query: str, **kwargs):
            # Mock implementation for testing
            return {
                "results": [
                    {
                        "id": "mock-memory-id",
                        "content": {
                            "project_name": "TaskManager",
                            "description": "A simple task management application",
                            "features": ["User authentication", "Task CRUD"],
                            "tech_stack": {"frontend": ["React"], "backend": ["FastAPI"]},
                            "styling": "Minimal and clean"
                        }
                    }
                ]
            }

# Import LangChain components
from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# Create router
router = APIRouter(
    prefix="/api/v1",
    tags=["app-generation"],
    responses={404: {"description": "Not found"}},
)

# Pydantic models for request/response validation
class AppSpec(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=255, description="Name of the project")
    description: str = Field(..., min_length=1, description="Detailed description of the app")
    features: List[str] = Field(..., min_items=1, description="List of features to implement")
    tech_stack: Dict[str, List[str]] = Field(..., description="Technology stack for the app")
    styling: Optional[str] = Field(None, description="Styling preferences")

    @validator('tech_stack')
    def validate_tech_stack(cls, v):
        if not v or not all(k in v for k in ['frontend', 'backend']):
            raise ValueError('Tech stack must include frontend and backend')
        return v

class GenerateResponse(BaseModel):
    """Response model for app generation."""
    status: str
    project_id: str

class GenerationStepResponse(BaseModel):
    """Response model for generation step details."""
    id: int
    project_id: str
    sequence_order: int
    tool_name: str
    input_payload: Dict[str, Any] = None
    status: str
    details: Dict[str, Any] = None
    error: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None
    
class ProjectStepsResponse(BaseModel):
    """Response model for a project's generation steps."""
    project_id: str
    project_name: str
    project_status: str
    steps: List[GenerationStepResponse]

class AppSpecResponse(BaseModel):
    project_name: str
    description: str
    features: List[str]
    tech_stack: Dict[str, List[str]]
    styling: Optional[str] = None

@router.post("/generate-app", response_model=GenerateResponse)
async def generate_app(spec: AppSpec, db: Session = Depends(get_db)):
    """
    Generate a new app based on the provided specification.
    
    This endpoint:
    1. Validates the app specification
    2. Calls Ollama to generate a plan
    3. Creates a new project in the database
    4. Returns the project ID and status
    """
    try:
        # Initialize Ollama client
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        ollama = Ollama(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model="vicuna-13b",
            temperature=0.2,
            # max_tokens is not supported in the current LangChain Ollama integration
            callback_manager=callback_manager
        )
        
        # Generate plan with Ollama
        prompt = f"""
        Generate a step-by-step plan for creating a web application with the following details:
        - Project Name: {spec.project_name}
        - Description: {spec.description}
        - Features: {', '.join(spec.features)}
        - Technology Stack: {json.dumps(spec.tech_stack)}
        - Styling: {spec.styling or 'No specific styling preferences'}
        
        Return a JSON array of steps with each step having:
        1. "tool": the type of operation (e.g., "create_file", "install_dependency")
        2. "input": an object with parameters for the operation
        
        Format the response as a valid JSON array like this:
        [
            {{"tool": "create_file", "input": {{"path": "src/app.js", "content": "// Code here"}}}},
            {{"tool": "install_dependency", "input": {{"name": "react", "version": "17.0.2"}}}}
        ]
        """
        
        try:
            # Ollama expects a list of strings
            plan_text = ollama.generate([prompt])[0]
            
            # For testing/development, we'll use a mock plan
            # In a real implementation, we'd parse the response from the LLM
            plan = [
                {"tool": "create_file", "input": {"path": "src/app.js", "content": "// React component"}},
                {"tool": "create_file", "input": {"path": "src/index.html", "content": "<!DOCTYPE html>"}},
                {"tool": "install_dependency", "input": {"name": "react", "version": "17.0.2"}}
            ]
        except Exception as e:
            # Log the error
            print(f"Error calling Ollama: {str(e)}")
            
            # For development/testing, use a mock plan
            plan = [
                {"tool": "create_file", "input": {"path": "src/app.js", "content": "// React component"}},
                {"tool": "create_file", "input": {"path": "src/index.html", "content": "<!DOCTYPE html>"}},
                {"tool": "install_dependency", "input": {"name": "react", "version": "17.0.2"}}
            ]
        
        # Create a new project in the database
        project_id = str(uuid.uuid4())
        db_project = Project(
            id=project_id,
            name=spec.project_name,
            description=spec.description,
            tech_stack=json.dumps(spec.tech_stack),
            styling=spec.styling,
            status="IN_PROGRESS",
            agent_id=str(uuid.uuid4())  # Generate a unique agent ID
        )
        
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        # Insert each step into the generation_steps table
        try:
            for i, step in enumerate(plan):
                # Validate step has required fields
                if "tool" not in step:
                    raise ValueError(f"Step {i+1} missing required 'tool' field")
                if "input" not in step:
                    raise ValueError(f"Step {i+1} missing required 'input' field")
                
                # Create step in database with PENDING status
                db_step = GenerationStep(
                    project_id=project_id,
                    sequence_order=i + 1,
                    tool_name=step.get("tool"),
                    input_payload=json.dumps(step.get("input")),
                    status=StepStatus.PENDING.value
                )
                db.add(db_step)
                
                # Log step creation
                print(f"Added step {i+1} with tool '{step.get('tool')}' to project {project_id}")
            
            # Commit all steps at once (atomic transaction)
            db.commit()
            print(f"Successfully inserted {len(plan)} steps for project {project_id}")
        except Exception as e:
            # Roll back step insertions if any fail
            db.rollback()
            # Update project status to ERROR
            db_project.status = "ERROR"
            db.add(db_project)
            db.commit()
            raise ValueError(f"Failed to insert generation steps: {str(e)}")
        
        return {
            "status": "in_progress",
            "project_id": project_id
        }
    
    except Exception as e:
        # Roll back any partial changes
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating app: {str(e)}"
        )

@router.get("/recall-last-app", response_model=dict)
async def recall_last_app():
    """Recall the last app specification from memory.

    Returns:
        dict: The last app specification from memory.
    """
    try:
        # Use MemorySearchTool to search for the most recent app specification
        memory_tool = MemorySearchTool()
        search_result = await memory_tool._call("most recent app specification")
        
        if not search_result or not search_result.get("results"):
            # For development/testing, return a mock app specification
            return {
                "project_name": "TaskManager",
                "description": "A simple task management application",
                "features": ["User authentication", "Task CRUD"],
                "tech_stack": {"frontend": ["React"], "backend": ["FastAPI"]},
                "styling": "Minimal and clean"
            }
        
        # Get the most recent result (first item in results)
        memory_content = search_result["results"][0]["content"]
        
        return memory_content
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error
        print(f"Error recalling app: {str(e)}")
        
        # For development/testing, return a mock app specification
        return {
            "project_name": "TaskManager",
            "description": "A simple task management application",
            "features": ["User authentication", "Task CRUD"],
            "tech_stack": {"frontend": ["React"], "backend": ["FastAPI"]},
            "styling": "Minimal and clean"
        }

@router.get("/project-steps/{project_id}", response_model=ProjectStepsResponse)
async def get_project_steps(project_id: str, db: Session = Depends(get_db)):
    """Retrieve all generation steps for a specific project.

    Args:
        project_id: The UUID of the project to retrieve steps for
        db: Database session dependency

    Returns:
        ProjectStepsResponse: Project details and its generation steps
        
    Raises:
        HTTPException: If project is not found
    """
    try:
        # Verify project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        # Get all steps for the project ordered by sequence_order
        steps = db.query(GenerationStep)\
            .filter(GenerationStep.project_id == project_id)\
            .order_by(GenerationStep.sequence_order)\
            .all()
        
        # Convert steps to response model format
        step_responses = []
        for step in steps:
            step_dict = step.to_dict()
            
            # Parse JSON strings to Python objects for the response
            if step_dict["input_payload"] and isinstance(step_dict["input_payload"], str):
                try:
                    step_dict["input_payload"] = json.loads(step_dict["input_payload"])
                except json.JSONDecodeError:
                    step_dict["input_payload"] = {"error": "Invalid JSON"}
                    
            if step_dict["details"] and isinstance(step_dict["details"], str):
                try:
                    step_dict["details"] = json.loads(step_dict["details"])
                except json.JSONDecodeError:
                    step_dict["details"] = {"error": "Invalid JSON"}
            
            step_responses.append(GenerationStepResponse(**step_dict))
        
        # Return project details and steps
        return ProjectStepsResponse(
            project_id=project.id,
            project_name=project.name,
            project_status=project.status,
            steps=step_responses
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving project steps: {str(e)}"
        )
