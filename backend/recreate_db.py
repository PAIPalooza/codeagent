"""
Script to recreate database tables.

This script drops all tables and recreates them with the current models.
Only use in development environments where data loss is acceptable.
"""

from app.database import engine, init_models
from app.models.project import Project
from app.models.generation_step import GenerationStep
from app.models.log import Log

def recreate_tables():
    """Drop all tables and recreate them with the current model definitions."""
    Base = init_models()
    
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Database tables recreated successfully!")

if __name__ == "__main__":
    recreate_tables()
