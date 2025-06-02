#!/usr/bin/env python
"""
Diagnostic script to directly test download_url serialization 
and identify why it's not appearing in API responses.
"""

import os
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
import json
from pathlib import Path

# Add the current directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our models
from app.models.project import Project
from app.database import Base, init_db

def inspect_project(project_id=33):
    """Inspect a project and its download_url directly from the database"""
    # Initialize the database connection
    engine = create_engine("sqlite:///./temp/test_app.db", echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print(f"\n{'='*50}\nINSPECTING PROJECT {project_id}\n{'='*50}")
    
    # 1. Get the project directly with SQLAlchemy
    project = session.query(Project).filter(Project.id == project_id).first()
    if not project:
        print(f"Project {project_id} not found")
        return
    
    # 2. Print direct attribute access
    print("\n--- Direct Attribute Access ---")
    print(f"ID: {project.id}")
    print(f"Name: {project.name}")
    print(f"Status: {project.status}")
    print(f"Download URL (direct attribute): {project.download_url!r}")
    
    # 3. Print raw SQL query
    print("\n--- Raw SQL Query ---")
    from sqlalchemy import text
    result = session.execute(text(f"SELECT download_url FROM projects WHERE id = {project_id}")).fetchone()
    print(f"Download URL (raw SQL): {result[0] if result else None!r}")
    
    # 4. Test dictionary serialization
    print("\n--- Dictionary Serialization ---")
    project_dict = project.to_dict() if hasattr(project, 'to_dict') else {
        'id': project.id, 
        'name': project.name, 
        'status': project.status.value if hasattr(project.status, 'value') else project.status,
        'download_url': project.download_url
    }
    print(f"Download URL in dict: {project_dict.get('download_url')!r}")
    print(f"Full dict: {json.dumps(project_dict, default=str, indent=2)}")
    
    # 5. Test JSON serialization
    print("\n--- JSON Serialization ---")
    try:
        json_str = json.dumps(project_dict, default=str)
        print(f"JSON serialization successful: {json_str}")
        
        # Parse back to verify
        parsed = json.loads(json_str)
        print(f"Download URL after JSON round-trip: {parsed.get('download_url')!r}")
    except Exception as e:
        print(f"JSON serialization error: {e}")
    
    # 6. Inspect database schema
    print("\n--- Database Schema ---")
    inspector = inspect(engine)
    columns = inspector.get_columns('projects')
    for col in columns:
        print(f"Column: {col['name']}, Type: {col['type']}")
    
    print("\n--- End of Inspection ---\n")

if __name__ == "__main__":
    # Use command line arg if provided, otherwise default to 33
    project_id = int(sys.argv[1]) if len(sys.argv) > 1 else 33
    inspect_project(project_id)
