from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

# Project schemas
class ProjectStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SUCCESS = "success"  # Successfully completed with download ZIP available
    FAILED = "failed"

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.DRAFT  # Use enum but ensure JSON serializability
    tech_stack: Optional[str] = None
    styling: Optional[str] = None
    canvas_layout: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    # Define download_url once with Field metadata
    download_url: Optional[str] = Field(
        None, 
        description="URL to download the generated project as a ZIP file"
    )
    
    # Custom serializer method to handle enums
    def model_dump(self, **kwargs):
        # Override to ensure download_url is included
        kwargs.setdefault("exclude_none", False)
        data = super().model_dump(**kwargs)
        # Handle enum serialization
        if "status" in data and hasattr(data["status"], "value"):
            data["status"] = data["status"].value
        return data

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None

class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    generation_steps: List[Dict[str, Any]] = []
    logs: List[Dict[str, Any]] = []

    # Updated to Pydantic v2 syntax for model configuration
    model_config = ConfigDict(
        from_attributes=True,  # Replaces orm_mode
        populate_by_name=True,
        exclude_none=False,  # Don't exclude None values
        # Explicit JSON encoders for known non-JSON serializable types
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
            ProjectStatus: lambda v: v.value if hasattr(v, 'value') else str(v)
        },
        # Example schema 
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "My Project",
                "description": "A test project",
                "status": "in_progress",
                "tech_stack": "React + FastAPI + PostgreSQL",
                "styling": "tailwind",
                "canvas_layout": None,
                "user_id": None,
                "download_url": "/api/v1/downloads/my_project.zip",
                "created_at": "2025-06-01T00:00:00",
                "updated_at": "2025-06-01T00:05:00",
                "generation_steps": [],
                "logs": []
            }
        }
    )
    
    # Custom serializer method to handle enums and ensure download_url is included
    def model_dump(self, **kwargs):
        # Ensure None values are included
        kwargs.setdefault("exclude_none", False) 
        
        # Get the data from parent
        data = super().model_dump(**kwargs)
        
        # Handle enum serialization
        if "status" in data and hasattr(data["status"], "value"):
            data["status"] = data["status"].value
            
        # Ensure download_url is included
        if hasattr(self, "download_url") and self.download_url is not None:
            data["download_url"] = self.download_url
            
        return data

# Generation Step schemas
class StepStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class GenerationStepBase(BaseModel):
    project_id: int
    step_name: str
    status: StepStatus = StepStatus.PENDING
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class GenerationStepCreate(GenerationStepBase):
    pass

class GenerationStepUpdate(GenerationStepBase):
    status: Optional[StepStatus] = None
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class GenerationStep(GenerationStepBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,  # Replaces orm_mode
        populate_by_name=True
    )

# Log schemas
class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class LogBase(BaseModel):
    level: LogLevel
    message: str
    source: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    project_id: Optional[int] = None

class LogCreate(LogBase):
    pass

class Log(LogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,  # Replaces orm_mode
        populate_by_name=True
    )
