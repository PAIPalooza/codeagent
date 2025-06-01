import logging
import json
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from .. import models, schemas
from ..database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",  # No prefix here since we're mounting at /projects in main.py
    tags=["projects"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project"""
    db_project = models.Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    # Convert SQLAlchemy model to Pydantic model for proper serialization
    return schemas.Project(**db_project.to_dict())

@router.get("/", response_model=List[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all projects"""
    projects = db.query(models.Project).offset(skip).limit(limit).all()
    # Convert SQLAlchemy models to Pydantic models using to_dict() for proper serialization
    return [schemas.Project(**project.to_dict()) for project in projects]

@router.get("/{project_id}", response_class=JSONResponse)
def read_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project by ID"""
    # Get the project from the database
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        logger.warning(f"Project with ID {project_id} not found")
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Log information for debugging
    logger.info(f"SQLAlchemy model download_url attribute: {db_project.download_url!r}")
    
    # Direct database access and manual JSON serialization to completely bypass Pydantic
    # Based on the successful test_direct_api.py approach
    serialized_data = {
        "id": db_project.id,
        "name": db_project.name,
        "description": db_project.description,
        "status": db_project.status.value,  # Manually handle enum
        "tech_stack": db_project.tech_stack,
        "styling": db_project.styling,
        "user_id": db_project.user_id,
        # Explicitly include download_url
        "download_url": db_project.download_url,
        # Convert datetime objects manually
        "created_at": db_project.created_at.isoformat() if db_project.created_at else None,
        "updated_at": db_project.updated_at.isoformat() if db_project.updated_at else None,
    }
    
    # Log the serialized data
    logger.info(f"DIRECT JSON RESPONSE: {serialized_data}")
    logger.info(f"download_url value: {serialized_data.get('download_url')!r}")
    
    # Return direct JSONResponse (skip FastAPI's serialization entirely)
    return JSONResponse(content=serialized_data)


@router.get("/{project_id}/debug", response_class=JSONResponse)
def debug_download_url(project_id: int, db: Session = Depends(get_db)):
    """Debug endpoint to test download_url serialization"""
    # Get the project from the database
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get information directly from the database
    download_url = db_project.download_url
    
    # Return only the download_url field for testing
    return {"download_url": download_url, "test": "This is a test value"}


@router.put("/{project_id}", response_model=schemas.Project)
def update_project(
    project_id: int, project: schemas.ProjectUpdate, db: Session = Depends(get_db)
):
    """Update a project"""
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    # Convert SQLAlchemy model to Pydantic model for proper serialization
    return schemas.Project(**db_project.to_dict())

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project"""
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
    return None
