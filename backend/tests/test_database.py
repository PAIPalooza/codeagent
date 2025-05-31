import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import get_db, Base
from app.models.project import Project, ProjectStatus
from app.models.generation_step import GenerationStep, StepStatus
from app.models.log import Log, LogLevel
import os

def test_database_connection():
    """Test database connection and table creation"""
    # Use in-memory SQLite for testing
    TEST_DATABASE_URL = "sqlite:///:memory:"
    
    # Create a test engine
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    
    # Create a test session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a test session
    db = TestingSessionLocal()
    
    try:
        # Test Project model
        project = Project(
            name="Test Project",
            description="A test project",
            status=ProjectStatus.DRAFT,
            tech_stack="fastapi-react",
            styling="tailwind"
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        assert project.id is not None
        assert project.name == "Test Project"
        assert project.status == ProjectStatus.DRAFT
        
        # Test GenerationStep model
        step = GenerationStep(
            project_id=project.id,
            step_name="test_step",
            status=StepStatus.COMPLETED,
            details={"message": "Test step completed"}
        )
        db.add(step)
        db.commit()
        db.refresh(step)
        
        assert step.id is not None
        assert step.project_id == project.id
        assert step.status == StepStatus.COMPLETED
        
        # Test Log model
        log = Log(
            level=LogLevel.INFO,
            message="Test log message",
            source="test",
            project_id=project.id,
            context={"key": "value"}
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        
        assert log.id is not None
        assert log.project_id == project.id
        assert log.level == LogLevel.INFO
        
    finally:
        db.close()
        # Clean up
        Base.metadata.drop_all(bind=engine)

if __name__ == "__main__":
    test_database_connection()
    print("All database tests passed!")
