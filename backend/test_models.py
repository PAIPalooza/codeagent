import sys
import os
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import models and database
from app.database import init_models, get_db
from app.models.project import Project, ProjectStatus
from app.models.generation_step import GenerationStep, StepStatus
from app.models.log import Log, LogLevel

# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

def test_models():
    # Create test engine and session
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    
    # Initialize models
    Base = init_models()
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create a test session
    db = TestingSessionLocal()
    
    try:
        # Test Project model
        print("Creating test project...")
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
        print(f"Created project with ID: {project.id}")
        
        # Test GenerationStep model
        print("Creating test generation step...")
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
        print(f"Created generation step with ID: {step.id}")
        
        # Test Log model
        print("Creating test log...")
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
        print(f"Created log with ID: {log.id}")
        
        # Query the project with relationships
        print("\nQuerying project with relationships...")
        project = db.query(Project).first()
        print(f"Project: {project.name} (ID: {project.id})")
        print(f"Status: {project.status}")
        print(f"Created at: {project.created_at}")
        
        # Query generation steps for the project
        steps = db.query(GenerationStep).filter(GenerationStep.project_id == project.id).all()
        print(f"\nFound {len(steps)} generation steps:")
        for step in steps:
            print(f"- {step.step_name}: {step.status}")
        
        # Query logs for the project
        logs = db.query(Log).filter(Log.project_id == project.id).all()
        print(f"\nFound {len(logs)} logs:")
        for log in logs:
            print(f"- [{log.level}] {log.message}")
        
        print("\nAll tests passed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        # Clean up
        db.close()
        Base.metadata.drop_all(bind=engine)

if __name__ == "__main__":
    test_models()
