#!/usr/bin/env python
"""
Direct test script to diagnose download_url serialization issue
Uses direct SQLAlchemy queries and JSON serialization without FastAPI
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.declarative import DeclarativeMeta

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Database setup
DB_URL = "sqlite:///./temp/test_app.db"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Helper function to serialize SQLAlchemy models to dict
def serialize_model(model: Any) -> Dict[str, Any]:
    """Serialize SQLAlchemy model to dict"""
    result = {}
    for column in model.__table__.columns:
        value = getattr(model, column.name)
        if isinstance(value, datetime):
            value = value.isoformat()
        result[column.name] = value
    return result

def inspect_table(table_name: str) -> None:
    """Inspect table schema"""
    inspector = inspect(engine)
    
    # Check if table exists
    if table_name not in inspector.get_table_names():
        logger.error(f"Table '{table_name}' does not exist in database")
        return
    
    # Get table columns
    columns = inspector.get_columns(table_name)
    logger.info(f"Table '{table_name}' has {len(columns)} columns:")
    
    for column in columns:
        logger.info(f"  - {column['name']}: {column['type']} (nullable: {column['nullable']})")

def direct_query(project_id: int) -> Dict[str, Any]:
    """Query project directly using raw SQL
    
    Args:
        project_id: The ID of the project to query
        
    Returns:
        Dict containing the project data with all fields including download_url
    """
    from sqlalchemy import text
    
    with engine.connect() as conn:
        # First, get table columns to ensure download_url exists
        inspector = inspect(engine)
        columns = [col["name"] for col in inspector.get_columns("projects")]
        logger.info(f"Columns in projects table: {columns}")
        
        try:
            # Execute query using SQLAlchemy text() function and proper parameter binding
            query = text("SELECT * FROM projects WHERE id = :project_id")
            result = conn.execute(query, {"project_id": project_id}).fetchone()
            
            if not result:
                logger.error(f"Project {project_id} not found")
                return {}
            
            # Convert to dict - proper SQLAlchemy result handling
            result_dict = {}
            for column in columns:
                try:
                    # Access values by column name
                    value = result[column]
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    result_dict[column] = value
                except Exception as e:
                    logger.error(f"Error accessing column {column}: {e}")
            
            # Explicitly check for download_url
            if 'download_url' in result_dict:
                logger.info(f"download_url found: {result_dict['download_url']!r}")
            else:
                logger.warning("download_url NOT found in result")
                
            logger.info(f"Raw query result: {result_dict}")
            return result_dict
            
        except Exception as e:
            logger.error(f"SQL query error: {e}")
            return {}

def orm_query(project_id: int) -> Dict[str, Any]:
    """Query project using SQLAlchemy ORM"""
    # Import models dynamically
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app.models import Project
    
    # Create session
    db = SessionLocal()
    try:
        # Query project
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            logger.error(f"Project {project_id} not found")
            return {}
        
        # Check download_url directly
        download_url_value = project.download_url
        logger.info(f"Direct ORM access download_url: {download_url_value!r}")
        
        # Try to access all attributes
        result = serialize_model(project)
        logger.info(f"ORM serialized result: {result}")
        
        # Explicitly try convert to JSON
        json_str = json.dumps(result)
        logger.info(f"JSON string length: {len(json_str)}")
        
        return result
    finally:
        db.close()

def main():
    """Main function"""
    # Check if project_id is provided
    if len(sys.argv) < 2:
        project_id = 33  # Default project ID
    else:
        project_id = int(sys.argv[1])
    
    logger.info(f"Testing project with ID: {project_id}")
    
    # Inspect table schema
    inspect_table("projects")
    
    # Direct SQL query
    logger.info("=== DIRECT SQL QUERY ===")
    sql_result = direct_query(project_id)
    logger.info(f"SQL download_url: {sql_result.get('download_url')}")
    
    # ORM query
    logger.info("\n=== ORM QUERY ===")
    orm_result = orm_query(project_id)
    logger.info(f"ORM download_url: {orm_result.get('download_url')}")
    
    # Verify field exists in both results
    has_sql_field = 'download_url' in sql_result
    has_orm_field = 'download_url' in orm_result
    logger.info(f"Field exists in SQL result: {has_sql_field}")
    logger.info(f"Field exists in ORM result: {has_orm_field}")
    
    # Write results to file for inspection
    with open("test_results.json", "w") as f:
        json.dump({
            "sql_result": sql_result,
            "orm_result": orm_result
        }, f, indent=2)
    
    logger.info("Results written to test_results.json")

if __name__ == "__main__":
    main()
