#!/usr/bin/env python3
"""Test script for database models and relationships.

This script tests the database models, relationships, and cascade behaviors
to ensure that our model structure is working correctly.
"""

import logging
import os
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, db_session, reset_database, get_table_names
from app.models import Project, ProjectStatus, GenerationStep, StepStatus, Log, LogLevel


def test_database_setup():
    """Test database initialization and table creation."""
    logger.info("Testing database setup...")
    
    # Initialize the database
    init_db()
    
    # Reset the database (drops and recreates all tables)
    reset_database()
    
    # Get table names
    tables = get_table_names()
    logger.info(f"Available tables: {tables}")
    
    assert 'projects' in tables, "Projects table not found"
    assert 'generation_steps' in tables, "GenerationStep table not found"
    assert 'logs' in tables, "Log table not found"
    
    logger.info("Database setup test passed!")


def test_model_relationships():
    """Test model relationships and cascade behaviors."""
    logger.info("Testing model relationships...")
    
    # Create a test project with generation steps and logs
    with db_session() as session:
        # Create project
        project = Project(
            name="Test Project",
            description="A test project for model relationships",
            status=ProjectStatus.DRAFT,
            tech_stack="react-fastapi-postgresql",
            styling="tailwind",
            user_id="test-user-123"
        )
        session.add(project)
        session.flush()  # Flush to get the project ID
        
        # Create generation steps for the project
        step1 = GenerationStep(
            project_id=project.id,
            step_name="setup_models",
            status=StepStatus.COMPLETED,
            details={"completed_at": datetime.now().isoformat()}
        )
        
        step2 = GenerationStep(
            project_id=project.id,
            step_name="create_endpoints",
            status=StepStatus.IN_PROGRESS
        )
        
        session.add_all([step1, step2])
        
        # Create logs for the project
        log1 = Log(
            level=LogLevel.INFO,
            message="Project created successfully",
            source="backend",
            project_id=project.id,
            context={"user_id": "test-user-123"}
        )
        
        log2 = Log(
            level=LogLevel.DEBUG,
            message="Setting up project structure",
            source="backend",
            project_id=project.id
        )
        
        session.add_all([log1, log2])
        session.commit()
        
        # Get the project ID for later use
        project_id = project.id
        logger.info(f"Created test project with ID: {project_id}")
    
    # Verify relationships
    with db_session() as session:
        # Get the project with relationships
        project = session.query(Project).filter(Project.id == project_id).first()
        
        # Test project to steps relationship
        assert len(project.generation_steps) == 2, "Project should have 2 generation steps"
        
        # Test project to logs relationship
        assert len(project.logs) == 2, "Project should have 2 logs"
        
        # Test to_dict method with relationships
        project_dict = project.to_dict()
        assert len(project_dict["generation_steps"]) == 2, "to_dict should include generation steps"
        assert len(project_dict["logs"]) == 2, "to_dict should include logs"
        
        logger.info("Relationship tests passed!")
    
    # Test cascade delete behavior
    with db_session() as session:
        # Delete the project
        project = session.query(Project).filter(Project.id == project_id).first()
        session.delete(project)
        session.commit()
        
        # Verify that generation steps are deleted (CASCADE)
        steps = session.query(GenerationStep).filter(
            GenerationStep.project_id == project_id
        ).all()
        assert len(steps) == 0, "Generation steps should be deleted with CASCADE"
        
        # Verify that logs have project_id set to NULL (SET NULL)
        logs = session.query(Log).filter(
            Log.project_id == project_id
        ).all()
        assert len(logs) == 0, "Logs should have project_id set to NULL"
        
        logger.info("Cascade delete tests passed!")


if __name__ == "__main__":
    try:
        # Run the tests
        test_database_setup()
        test_model_relationships()
        
        logger.info("All database tests completed successfully!")
    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
        sys.exit(1)
