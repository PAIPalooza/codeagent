"""
Router for app generation endpoints.

This module provides endpoints for generating application code and managing
the generation process, including step execution and status tracking.
"""

import json
import logging
import os
import asyncio
from typing import Dict, Any, List, Optional
from uuid import uuid4
from pathlib import Path

from sse_starlette.sse import EventSourceResponse

import asyncio
import contextlib
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Response
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, ConfigDict
from typing import Generator, Optional, Any, Dict, List

from .. import models
from ..database import get_db
from ..models.generation_step import GenerationStep, StepStatus
from ..models.project import Project, ProjectStatus
from ..models.log import Log, LogLevel
from ..utils.file_writer import make_dirs, write_file, create_zip_archive

# Import AINative tool wrappers
from tools.code_gen_create_tool import CodeGenCreateTool
from tools.code_gen_refactor_tool import CodeGenRefactorTool
from tools.memory_store_tool import MemoryStoreTool
from tools.memory_search_tool import MemorySearchTool

# Import services
from ..services.ollama_service import OllamaService
from ..services.coordination_service import CoordinationService
from ..services.canvas_code_generator import CanvasCodeGenerator

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1",
    tags=["app-generation"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    },
)

# Pydantic models for request/response validation
class AppSpec(BaseModel):
    """App specification model for generation requests."""
    project_name: str = Field(..., description="Name of the project")
    description: str = Field(..., description="Description of the project")
    features: List[str] = Field(..., description="List of features to implement")
    tech_stack: str = Field(..., description="Technology stack to use")
    styling: Optional[str] = Field(None, description="Frontend styling framework")

class ProjectGenerationRequest(BaseModel):
    """Project generation request model for coordination workflows."""
    project_name: str = Field(..., description="Name of the project")
    description: str = Field(..., description="Description of the project")
    features: List[str] = Field(..., description="List of features to implement")
    tech_stack: str = Field(..., description="Technology stack to use")
    styling: Optional[str] = Field(None, description="Frontend styling framework")

class GenerationStepResponse(BaseModel):
    """Response model for generation steps."""
    id: str
    project_id: str
    sequence_order: int
    tool_name: str
    input_payload: Dict[str, Any]
    status: str
    output_payload: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class LogResponse(BaseModel):
    """Response model for log entries."""
    id: str
    level: str
    message: str
    source: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    project_id: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ProjectResponse(BaseModel):
    """Response model for project generation."""
    status: str
    project_id: str
    message: Optional[str] = None
    logs: Optional[List[Dict[str, Any]]] = None

# Map of tool names to their implementation classes
TOOL_MAP = {
    "codegen_create": CodeGenCreateTool,
    "codegen_refactor": CodeGenRefactorTool,
    "memory_store": MemoryStoreTool,
    "memory_search": MemorySearchTool,
}

# Directory for generated project files
TEMP_PROJECTS_DIR = os.environ.get("TEMP_PROJECTS_DIR", "temp_projects")

# Directory for download ZIP files
DOWNLOADS_DIR = os.environ.get("DOWNLOADS_DIR", "downloads")

# Ensure directories exist
make_dirs(TEMP_PROJECTS_DIR)
make_dirs(DOWNLOADS_DIR)

@router.post("/generate-app", response_model=ProjectResponse)
async def generate_app(app_spec: AppSpec, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Generate a new application based on the provided specification.
    
    Args:
        app_spec: Application specification
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Project generation status and ID with initial logs
    """
    try:
        # Validate app specification
        if not app_spec.project_name or not app_spec.description or not app_spec.features or not app_spec.tech_stack:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required fields in app specification"
            )
        
        # Create project record (id will be auto-generated)
        project = Project(
            name=app_spec.project_name,
            description=app_spec.description,
            features=app_spec.features,
            tech_stack=app_spec.tech_stack,
            styling=app_spec.styling,
            status=ProjectStatus.IN_PROGRESS,
        )
        db.add(project)
        
        # Generate plan using Ollama
        try:
            ollama_service = OllamaService()
            plan_steps = ollama_service.generate_app_plan(
                project_name=app_spec.project_name,
                description=app_spec.description,
                features=app_spec.features,
                tech_stack=app_spec.tech_stack,
                styling=app_spec.styling or "Plain CSS"
            )
            
            # Convert plan steps to our format
            steps = []
            for i, step in enumerate(plan_steps):
                steps.append({
                    "sequence_order": i + 1,
                    "step_name": f"step_{i+1}_{step['tool']}",
                    "tool_name": step["tool"],
                    "input_payload": step["input"]
                })
                
            logger.info(f"Generated {len(steps)} steps using Ollama for project '{app_spec.project_name}'")
            
        except Exception as e:
            logger.error(f"Failed to generate plan with Ollama: {str(e)}")
            # Log the error for debugging
            log = Log(
                project_id=None,  # Will be set after project creation
                level=LogLevel.WARNING,
                message=f"Ollama planning failed, using fallback: {str(e)}",
                source="planning"
            )
            
            # Fall back to basic steps
            steps = [
                {
                    "sequence_order": 1,
                    "step_name": "generate_models",
                    "tool_name": "codegen_create",
                    "input_payload": {
                        "template": "sqlalchemy-model" if "React" in app_spec.tech_stack else "basic-model",
                        "file_path": "backend/app/models.py",
                        "variables": {
                            "project_name": app_spec.project_name,
                            "description": app_spec.description,
                            "features": app_spec.features,
                            "tech_stack": app_spec.tech_stack,
                            "styling": app_spec.styling or "Plain CSS"
                        }
                    }
                },
                {
                    "sequence_order": 2,
                    "step_name": "generate_api_routes",
                    "tool_name": "codegen_create",
                    "input_payload": {
                        "template": "fastapi-route" if "FastAPI" in app_spec.tech_stack else "basic-api",
                        "file_path": "backend/app/routers/api.py",
                        "variables": {
                            "project_name": app_spec.project_name,
                            "description": app_spec.description,
                            "features": app_spec.features,
                            "tech_stack": app_spec.tech_stack,
                            "styling": app_spec.styling or "Plain CSS"
                        }
                    }
                }
            ]
        
        # Commit to get the auto-generated project ID
        db.flush()
        
        # Insert generation steps
        for step_data in steps:
            step = GenerationStep(
                project_id=project.id,
                step_name=step_data["step_name"],
                sequence_order=step_data["sequence_order"],
                tool_name=step_data["tool_name"],
                input_payload=step_data["input_payload"],
                status=StepStatus.PENDING
            )
            db.add(step)
        
        # Commit changes
        db.commit()
        
        # Schedule step execution as a background task with error handling
        async def safe_execute_generation_steps(project_id: str):
            try:
                await execute_generation_steps(project_id)
            except Exception as e:
                logger.error(f"Background task failed for project {project_id}: {str(e)}")
                # The error will be logged in the execute_generation_steps function
        
        background_tasks.add_task(safe_execute_generation_steps, project.id)
        
        # Get logs for the project
        logs = db.query(Log).filter(Log.project_id == project.id).order_by(Log.created_at).all()
        
        # Return project ID, status, and logs
        return ProjectResponse(
            status=project.status.value,
            project_id=str(project.id),
            message="Generation started in the background",
            logs=[log.to_dict() for log in logs]
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error generating app: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating app: {str(e)}"
        )

@router.get("/projects/{project_id}/steps", response_model=List[GenerationStepResponse])
async def get_project_steps(project_id: str, db: Session = Depends(get_db)):
    """
    Get all generation steps for a project.
    
    Args:
        project_id: Project ID
        db: Database session
        
    Returns:
        List of generation steps
    """
    try:
        # Check if project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        # Get all steps for the project, ordered by sequence
        steps = (
            db.query(GenerationStep)
            .filter(GenerationStep.project_id == project_id)
            .order_by(GenerationStep.sequence_order)
            .all()
        )
        
        # Convert steps to response model
        return [
            GenerationStepResponse(
                id=str(step.id),
                project_id=str(step.project_id),
                sequence_order=step.sequence_order,
                tool_name=step.tool_name,
                input_payload=step.input_payload,
                status=step.status.value,
                output_payload=step.output_payload,
                error=step.error,
                created_at=step.created_at.isoformat() if step.created_at else None,
                updated_at=step.updated_at.isoformat() if step.updated_at else None
            )
            for step in steps
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project steps: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting project steps: {str(e)}"
        )

@router.post("/projects/{project_id}/execute", response_model=ProjectResponse)
async def execute_pending_steps(project_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Execute all pending generation steps for a project.
    
    Args:
        project_id: Project ID
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Project status
    """
    try:
        # Check if project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        # Check if there are any pending steps
        pending_steps = (
            db.query(GenerationStep)
            .filter(
                GenerationStep.project_id == project_id,
                GenerationStep.status == StepStatus.PENDING
            )
            .count()
        )
        
        if pending_steps == 0:
            return {
                "status": "completed",
                "project_id": str(project_id),
                "message": "No pending steps to execute"
            }
        
        # Schedule step execution as a background task
        background_tasks.add_task(execute_generation_steps, project_id)
        
        return {
            "status": "in_progress",
            "project_id": str(project_id),
            "message": f"Execution of {pending_steps} pending steps scheduled"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing pending steps: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing pending steps: {str(e)}"
        )

async def execute_generation_steps(project_id: str):
    """
    Execute all pending generation steps for a project.
    
    This function is meant to be run as a background task.
    It logs each step of the generation process to provide real-time feedback.
    
    Args:
        project_id: Project ID
    """
    # Create a new database session for this background task with proper cleanup
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Set a timeout for the entire generation process (30 minutes)
        GENERATION_TIMEOUT = 1800  # 30 minutes in seconds
        start_time = datetime.utcnow()
        
        def check_timeout():
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            if elapsed > GENERATION_TIMEOUT:
                raise TimeoutError(f"Generation timed out after {GENERATION_TIMEOUT} seconds")
        
        logger.info(f"Starting execution of generation steps for project {project_id}")
        
        # Create project directory
        project_dir = os.path.join(TEMP_PROJECTS_DIR, str(project_id))
        make_dirs(project_dir)
        
        # Get all pending steps ordered by sequence
        pending_steps = (
            db.query(GenerationStep)
            .filter(
                GenerationStep.project_id == project_id,
                GenerationStep.status == StepStatus.PENDING
            )
            .order_by(GenerationStep.sequence_order)
            .all()
        )
        
        # Log the number of steps to be executed
        log_message = f"Starting execution of {len(pending_steps)} generation steps for project {project_id}"
        logger.info(log_message)
        log = Log(
            project_id=project_id,
            level=LogLevel.INFO,
            message=log_message,
            source="execution_loop"
        )
        db.add(log)
        db.commit()
        
        if not pending_steps:
            logger.info(f"No pending steps found for project {project_id}")
            return
        
        files_written = 0
        
        # Process each pending step
        for step in pending_steps:
            try:
                # Log the start of step execution
                step_start_message = f"Starting step {step.sequence_order}: {step.tool_name}"
                logger.info(f"Processing step {step.id} (sequence: {step.sequence_order}, tool: {step.tool_name})")
                log = Log(
                    project_id=project_id,
                    level=LogLevel.INFO,
                    message=step_start_message,
                    source="execution_loop",
                    context={
                        "step_id": step.id,
                        "sequence_order": step.sequence_order,
                        "tool_name": step.tool_name
                    }
                )
                db.add(log)
                db.commit()
                
                # Update step status to IN_PROGRESS
                step.status = StepStatus.IN_PROGRESS
                db.commit()
                
                # Get tool class
                tool_name = step.tool_name
                if tool_name not in TOOL_MAP:
                    raise ValueError(f"Unknown tool: {tool_name}")
                
                tool_class = TOOL_MAP[tool_name]
                tool = tool_class()
                
                # Call tool with input payload and timeout
                logger.info(f"Executing step {step.sequence_order} ({tool_name}) for project {project_id}")
                
                # Log input payload (safely)
                safe_input = {k: str(v) if not isinstance(v, (str, int, float, bool)) else v 
                           for k, v in step.input_payload.items()}
                
                db.add(Log(
                    project_id=project_id,
                    level=LogLevel.DEBUG,
                    message=f"Calling tool {tool_name} with input",
                    source="execution_loop",
                    context={"tool": tool_name, "input": safe_input}
                ))
                db.commit()
                
                # Execute tool with timeout (5 minutes per tool)
                try:
                    params = step.input_payload.get('variables', step.input_payload)
                    if isinstance(params, str):
                        import json
                        params = json.loads(params.replace("'", '"'))
                    output = await asyncio.wait_for(
                        tool._call(**params),
                        timeout=300  # 5 minutes per tool
                    )
                    check_timeout()  # Check overall timeout
                except asyncio.TimeoutError:
                    raise TimeoutError(f"Tool {tool_name} timed out after 5 minutes")
                
                # Log successful tool execution
                db.add(Log(
                    project_id=project_id,
                    level=LogLevel.DEBUG,
                    message=f"Tool {tool_name} completed successfully",
                    source="execution_loop",
                    context={"tool": tool_name}
                ))
                db.commit()
                
                # Update step with output
                step.output_payload = output
                
                # Check for errors in output
                if output.get("error"):
                    step.status = StepStatus.FAILED
                    step.error = output.get("message", "Unknown error")
                    log_message = f"Step {step.sequence_order} ({tool_name}) failed: {step.error}"
                    
                    # Add log entry
                    log = Log(
                        project_id=project_id,
                        level=LogLevel.ERROR,
                        message=log_message,
                        source="execution_loop",
                        context={
                            "step_id": step.id,
                            "sequence_order": step.sequence_order,
                            "tool_name": tool_name,
                            "error": step.error
                        }
                    )
                    db.add(log)
                    logger.error(log_message)
                    continue  # Skip to next step on error
                
                # Step succeeded
                step.status = StepStatus.COMPLETED
                
                # Check if this step generates a file
                file_path = output.get("file_path")
                code = output.get("code")
                
                if file_path and code:
                    # Create directory if it doesn't exist
                    full_path = os.path.join(project_dir, file_path)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    
                    # Write file
                    with open(full_path, 'w') as f:
                        f.write(code)
                    logger.info(f"Wrote file {file_path}")
                    
                    # Log file creation
                    log = Log(
                        project_id=project_id,
                        level=LogLevel.INFO,
                        message=f"Generated file: {file_path}",
                        source="file_writer",
                        context={
                            "step_id": step.id,
                            "file_path": file_path,
                            "file_size": len(code)
                        }
                    )
                    db.add(log)
                    db.commit()
                    files_written += 1
                    
                    log_message = f"Step {step.sequence_order} ({tool_name}) succeeded: wrote {file_path}"
                else:
                    log_message = f"Step {step.sequence_order} ({tool_name}) completed successfully"
                
                # Log step completion
                log = Log(
                    project_id=project_id,
                    level=LogLevel.INFO,
                    message=log_message,
                    source="execution_loop",
                    context={
                        "step_id": step.id,
                        "sequence_order": step.sequence_order,
                        "tool_name": tool_name
                    }
                )
                db.add(log)
                db.commit()
                
            except Exception as e:
                # Log error
                error_message = f"Error executing tool {tool_name}: {str(e)}"
                logger.error(error_message, exc_info=True)
                
                # Create log entry for the error
                log = Log(
                    project_id=project_id,
                    level=LogLevel.ERROR,
                    message=f"Step {step.sequence_order} ({tool_name}) failed: {str(e)}",
                    source="execution_loop",
                    context={
                        "step_id": step.id,
                        "sequence_order": step.sequence_order,
                        "tool_name": tool_name,
                        "error": str(e)
                    }
                )
                db.add(log)
                
                # Update step status
                step.status = StepStatus.FAILED
                step.error = error_message
                db.commit()
        
        # Check if at least one file was written
        if files_written == 0:
            logger.warning(f"No files were written for project {project_id}")
            
            # Log warning
            log = Log(
                project_id=project_id,
                level=LogLevel.WARNING,
                message=f"No files were written for project {project_id}",
                source="execution_loop",
                context={
                    "project_id": project_id
                }
            )
            db.add(log)
            db.commit()
        else:
            # Log files written
            log = Log(
                project_id=project_id,
                level=LogLevel.INFO,
                message=f"{files_written} files were written for project {project_id}",
                source="execution_loop",
                context={
                    "project_id": project_id,
                    "files_written": files_written
                }
            )
            db.add(log)
            db.commit()
        
        # Update project status based on step statuses
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if project:
            try:
                # Get all steps for the project
                steps = db.query(GenerationStep).filter(
                    GenerationStep.project_id == project_id
                ).all()
                
                any_failed = any(step.status == StepStatus.FAILED for step in steps)
                all_completed = all(step.status == StepStatus.COMPLETED for step in steps)
                
                if all_completed and files_written > 0:
                    project.status = ProjectStatus.COMPLETED
                
                if project.status == ProjectStatus.COMPLETED:
                    log_message = f"Project {project_id} generation completed successfully"
                    logger.info(log_message)
                else:
                    log_message = f"Project {project_id} generation completed with errors"
                    logger.warning(log_message)
                
                log = Log(
                    project_id=project_id,
                    level=LogLevel.INFO if project.status == ProjectStatus.COMPLETED else LogLevel.WARNING,
                    message=log_message,
                    source="execution_loop",
                    context={
                        "project_id": project_id,
                        "status": project.status.value,
                        "total_steps": len(pending_steps),
                        "files_written": files_written
                    }
                )
                db.add(log)
                db.commit()
                logger.info(f"Completed generation for project {project_id}")
                
            except Exception as e:
                # Log the full error with traceback
                import traceback
                error_trace = traceback.format_exc()
                logger.error(f"Error in background task for project {project_id}: {error_trace}")
        
        try:
            # Update project status to failed
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                project.status = ProjectStatus.FAILED
                project.updated_at = datetime.utcnow()
                db.commit()
            
            # Log the error
            log = Log(
                project_id=project_id,
                level=LogLevel.ERROR,
                message=f"Generation failed: {str(e)[:500]}",  # Truncate long messages
                source="execution_loop",
                context={
                    "error_type": type(e).__name__,
                    "error_message": str(e)[:1000],  # Truncate long messages
                    "traceback": error_trace[:2000]    # Truncate long tracebacks
                }
            )
            db.add(log)
            db.commit()
        except Exception as inner_e:
            logger.error(f"Error during error handling: {str(inner_e)}")
    finally:
        # Ensure we always close the database connection
        try:
            db.close()
            next(db_gen, None)  # Ensure the generator is properly closed
        except Exception as close_e:
            logger.error(f"Error closing database connection: {str(close_e)}")
    
    # Start the background task
    asyncio.create_task(execute_steps_async())
    
    return {"message": "Generation started in the background"}


@router.get("/projects/{project_id}/logs", response_model=List[LogResponse])
async def get_project_logs(project_id: str, db: Session = Depends(get_db)):
    """
    Get all logs for a specific project.
    
    Args:
        project_id: Project ID
        db: Database session
        
    Returns:
        List of log entries for the project
    """
    try:
        # Check if project exists
        project = db.query(Project).filter(
            Project.id == project_id
        ).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        # Get logs for the project ordered by creation time
        logs = db.query(Log).filter(
            Log.project_id == project_id
        ).order_by(Log.created_at).all()
        
        # Return logs as list of dictionaries
        return [LogResponse(**log.to_dict()) for log in logs]
    
    except Exception as e:
        logger.error(
            f"Error retrieving logs for project {project_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving logs: {str(e)}"
        )

@router.get("/projects/{project_id}/logs/stream")
async def stream_project_logs(project_id: str, response: Response, db: Session = Depends(get_db)):
    """
    Stream logs for a specific project as server-sent events.
    
    Args:
        project_id: Project ID
        response: FastAPI response object
        db: Database session
        
    Returns:
        Server-sent events stream of log entries
    """
    try:
        # Check if project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        # Set up SSE response headers
        response.headers["Content-Type"] = "text/event-stream"
        response.headers["Cache-Control"] = "no-cache"
        response.headers["Connection"] = "keep-alive"
        
        # Get initial logs
        logs = db.query(Log).filter(Log.project_id == project_id).order_by(Log.created_at).all()
        
        # Function to generate SSE messages
        async def event_generator():
            # Send initial logs
            for log in logs:
                log_data = json.dumps(log.to_dict())
                yield f"data: {log_data}\n\n"
            
            # Continue checking for new logs while project is in progress
            last_log_id = logs[-1].id if logs else 0
            while project.status == ProjectStatus.IN_PROGRESS:
                # Check for new logs
                new_logs = db.query(Log).filter(
                    Log.project_id == project_id,
                    Log.id > last_log_id
                ).order_by(Log.created_at).all()
                
                # Send new logs as events
                for log in new_logs:
                    log_data = json.dumps(log.to_dict())
                    yield f"data: {log_data}\n\n"
                    last_log_id = log.id
                
                # Refresh project status
                db.refresh(project)
                
                # Wait a short time before checking again
                await asyncio.sleep(0.5)
            
            # Send a final message when project is completed
            final_status = {
                "status": project.status.value,
                "project_id": str(project.id)
            }
            yield f"data: {json.dumps(final_status)}\n\n"
            yield "event: close\ndata: Stream closed\n\n"
        
        # Return the event stream
        return EventSourceResponse(event_generator())
    
    except Exception as e:
        logger.error(
            f"Error streaming logs for project {project_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error streaming logs: {str(e)}"
        )


@router.get("/recall-last-app")
async def recall_last_app(db: Session = Depends(get_db)):
    """
    Recall the last generated app specification.
    
    Args:
        db: Database session
        
    Returns:
        App specification of the most recent project
    """
    try:
        # Get the most recent project
        latest_project = (
            db.query(Project)
            .order_by(Project.created_at.desc())
            .first()
        )
        
        if not latest_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No previous app found"
            )
        
        # Return the project specification
        return {
            "project_name": latest_project.name,
            "description": latest_project.description,
            "features": latest_project.features or [],
            "tech_stack": latest_project.tech_stack,
            "styling": latest_project.styling
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recalling last app: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recalling last app: {str(e)}"
        )

@router.get("/downloads/{filename}")
async def download_project(filename: str):
    """
    Download a project ZIP file.
    
    Args:
        filename: Name of the ZIP file to download
        
    Returns:
        The ZIP file as a downloadable response
        
    Raises:
        HTTPException: If the file doesn't exist
    """
    file_path = os.path.join(DOWNLOADS_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {filename} not found"
        )
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/zip"
    )

# Coordination endpoints for multi-agent workflows

@router.post("/coordination/create-workflow")
async def create_coordination_workflow(
    request: ProjectGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Create a multi-agent coordination workflow for code generation.
    
    Args:
        request: Project generation request with specifications
        db: Database session
        
    Returns:
        Dictionary containing workflow_id and status
    """
    try:
        logger.info(f"Creating coordination workflow for project: {request.project_name}")
        
        # Create project record
        project = Project(
            name=request.project_name,
            description=request.description,
            features=request.features,
            tech_stack=request.tech_stack,
            styling=request.styling,
            status=ProjectStatus.COORDINATING
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        # Create coordination service and workflow
        coordination_service = CoordinationService()
        
        project_spec = {
            "project_id": project.id,
            "project_name": request.project_name,
            "description": request.description,
            "features": request.features,
            "tech_stack": request.tech_stack,
            "styling": request.styling
        }
        
        workflow_result = await coordination_service.create_generation_workflow(project_spec)
        
        if workflow_result.get("success"):
            # Update project with workflow ID
            project.coordination_workflow_id = workflow_result["workflow_id"]
            db.commit()
            
            logger.info(f"Created coordination workflow {workflow_result['workflow_id']} for project {project.id}")
            
            return {
                "success": True,
                "project_id": project.id,
                "workflow_id": workflow_result["workflow_id"],
                "estimated_duration": workflow_result.get("estimated_duration"),
                "agents": workflow_result.get("agents", []),
                "message": "Coordination workflow created successfully"
            }
        else:
            project.status = ProjectStatus.FAILED
            db.commit()
            
            logger.error(f"Failed to create coordination workflow: {workflow_result.get('message')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create coordination workflow: {workflow_result.get('message')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating coordination workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating coordination workflow: {str(e)}"
        )

@router.post("/coordination/execute-workflow/{workflow_id}")
async def execute_coordination_workflow(
    workflow_id: str,
    db: Session = Depends(get_db)
):
    """
    Execute a coordination workflow.
    
    Args:
        workflow_id: ID of the workflow to execute
        db: Database session
        
    Returns:
        Dictionary containing execution status
    """
    try:
        logger.info(f"Executing coordination workflow: {workflow_id}")
        
        # Find project by workflow ID
        project = db.query(Project).filter(
            Project.coordination_workflow_id == workflow_id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found for workflow {workflow_id}"
            )
        
        # Update project status
        project.status = ProjectStatus.GENERATING
        db.commit()
        
        # Execute workflow
        coordination_service = CoordinationService()
        result = await coordination_service.execute_workflow(workflow_id)
        
        if result.get("success"):
            logger.info(f"Started execution of workflow: {workflow_id}")
            return {
                "success": True,
                "workflow_id": workflow_id,
                "project_id": project.id,
                "message": "Workflow execution started"
            }
        else:
            project.status = ProjectStatus.FAILED
            db.commit()
            
            logger.error(f"Failed to execute workflow: {result.get('message')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to execute workflow: {result.get('message')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing coordination workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing coordination workflow: {str(e)}"
        )

@router.get("/coordination/workflow/{workflow_id}/status")
async def get_coordination_workflow_status(
    workflow_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the status of a coordination workflow.
    
    Args:
        workflow_id: ID of the workflow
        db: Database session
        
    Returns:
        Dictionary containing workflow status and progress
    """
    try:
        # Find project by workflow ID
        project = db.query(Project).filter(
            Project.coordination_workflow_id == workflow_id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found for workflow {workflow_id}"
            )
        
        # Get workflow status
        coordination_service = CoordinationService()
        result = await coordination_service.get_workflow_status(workflow_id)
        
        if result.get("success"):
            return {
                "success": True,
                "workflow_id": workflow_id,
                "project_id": project.id,
                "status": result.get("data", {}),
                "project_status": project.status.value
            }
        else:
            logger.error(f"Failed to get workflow status: {result.get('message')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get workflow status: {result.get('message')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting coordination workflow status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting coordination workflow status: {str(e)}"
        )

# Canvas code generation endpoints

class CanvasGenerationRequest(BaseModel):
    """Request model for canvas code generation."""
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    canvas_layout: Dict[str, Any] = Field(..., description="Canvas layout with components")
    tech_stack: str = Field(default="React + FastAPI + PostgreSQL", description="Technology stack")
    styling: str = Field(default="Tailwind CSS", description="Styling framework")

@router.post("/canvas/generate-code")
async def generate_code_from_canvas(
    request: CanvasGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate React code from canvas layout.
    
    Args:
        request: Canvas generation request with layout and specifications
        db: Database session
        
    Returns:
        Dictionary containing generated code files
    """
    try:
        logger.info(f"Generating code from canvas for project: {request.name}")
        
        # Create project record
        project = Project(
            name=request.name,
            description=request.description,
            canvas_layout=request.canvas_layout,
            tech_stack=request.tech_stack,
            styling=request.styling,
            status=ProjectStatus.IN_PROGRESS
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        # Generate code using canvas code generator
        canvas_generator = CanvasCodeGenerator()
        
        project_spec = {
            "name": request.name,
            "description": request.description,
            "tech_stack": request.tech_stack,
            "styling": request.styling
        }
        
        result = await canvas_generator.generate_code_from_layout(
            request.canvas_layout, 
            project_spec
        )
        
        if result.get("success"):
            # Update project status
            project.status = ProjectStatus.COMPLETED
            db.commit()
            
            logger.info(f"Successfully generated code for canvas project {project.id}")
            
            return {
                "success": True,
                "project_id": project.id,
                "files": result["files"],
                "analysis": result["analysis"],
                "components_count": result["components_count"],
                "message": "Code generated successfully from canvas layout"
            }
        else:
            project.status = ProjectStatus.FAILED
            db.commit()
            
            logger.error(f"Failed to generate code from canvas: {result.get('message')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate code: {result.get('message')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating code from canvas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating code from canvas: {str(e)}"
        )
