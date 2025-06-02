import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from dotenv import load_dotenv

# Import database and models
from app.database import get_db, create_tables, init_db, init_app
from app.models.project import Project as ProjectModel, ProjectStatus
from app.models.generation_step import GenerationStep as GenerationStepModel
from app.models.log import Log as LogModel, LogLevel

# Import routers
from app.routers.app_generation import router as app_generation_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CodeAgent API",
    description="API for generating and managing code projects",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(app_generation_router)

# Initialize database and create tables on startup
@app.on_event("startup")
def on_startup():
    try:
        # First initialize the database connection
        init_db()
        # Then initialize the app and create tables
        init_app()
        logger.info("Database initialized and tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

# Pydantic models for request/response validation
class ProjectBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    tech_stack: Optional[str] = None
    styling: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class HealthCheckResponse(BaseModel):
    status: str
    database: str
    environment: str

# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Check the health of the API and its dependencies"""
    db_status = "ok"
    try:
        db = next(get_db())
        db.execute("SELECT 1")
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "error"
    
    return {
        "status": "healthy",
        "database": db_status,
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# Project endpoints
@app.post("/projects/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate, db = Depends(get_db)):
    """Create a new project"""
    try:
        # Create project in database
        db_project = ProjectModel(
            name=project.name,
            description=project.description,
            tech_stack=project.tech_stack,
            styling=project.styling,
            status=ProjectStatus.DRAFT
        )
        
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        # Log the project creation
        log = LogModel(
            level=LogLevel.INFO,
            message=f"Project '{project.name}' created",
            source="api",
            context={"project_id": db_project.id, "action": "create"}
        )
        db.add(log)
        db.commit()
        
        return db_project
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating project"
        )

@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db = Depends(get_db)):
    """Get a project by ID"""
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT") == "development"
    )
