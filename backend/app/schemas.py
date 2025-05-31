from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

# Project schemas
class ProjectStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.DRAFT
    tech_stack: Optional[str] = None
    styling: Optional[str] = None
    canvas_layout: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None

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

    class Config:
        orm_mode = True

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

    class Config:
        orm_mode = True

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

    class Config:
        orm_mode = True
