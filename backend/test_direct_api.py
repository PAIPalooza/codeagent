#!/usr/bin/env python
"""
Diagnostic script that creates a minimal FastAPI app with no middleware
to directly test the download_url serialization.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create a minimal FastAPI app with NO middleware
app = FastAPI(title="Test Direct API", docs_url="/test-docs")

# Import our database and models
from app.database import init_db, init_app, get_db
from app.models.project import Project

# Initialize database
init_db()
init_app()

# Custom response models for testing
class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    download_url: Optional[str] = None  # Explicitly include download_url
    
    class Config:
        from_attributes = True

@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    logger.info("Test API server starting up")

@app.get("/")
async def root():
    return {"status": "ok", "message": "Test API server is running"}

@app.get("/test1/{project_id}", response_model=ProjectResponse)
async def test_pydantic(project_id: int):
    """Test with Pydantic model response"""
    # Get database session
    db = next(get_db())
    
    # Get project from database
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Log what we found
    logger.info(f"Project found: {project.id}, download_url: {project.download_url!r}")
    
    # Return using Pydantic model
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        download_url=project.download_url
    )

@app.get("/test2/{project_id}")
async def test_direct_dict(project_id: int):
    """Test with direct dictionary response"""
    # Get database session
    db = next(get_db())
    
    # Get project from database
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Log what we found
    logger.info(f"Project found: {project.id}, download_url: {project.download_url!r}")
    
    # Return direct dictionary
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "download_url": project.download_url
    }

@app.get("/test3/{project_id}")
async def test_raw_response(project_id: int):
    """Test with completely raw response bypassing everything"""
    # Get database session
    db = next(get_db())
    
    # Get project from database
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Log what we found
    logger.info(f"Project found: {project.id}, download_url: {project.download_url!r}")
    
    # Create response data
    data = {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "download_url": project.download_url,
        "_test": "test3_raw_response"
    }
    
    # Serialize manually
    json_content = json.dumps(data)
    logger.info(f"Raw JSON response: {json_content}")
    
    # Use starlette.responses directly
    from starlette.responses import Response
    return Response(
        content=json_content,
        media_type="application/json"
    )

if __name__ == "__main__":
    uvicorn.run("test_direct_api:app", host="0.0.0.0", port=8001, reload=True)
