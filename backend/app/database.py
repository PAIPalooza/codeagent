"""Database connection and session management module.

This module sets up the SQLAlchemy engine, session factory, and base model class.
It also provides utility functions for database operations and initialization.
"""

from contextlib import contextmanager
from typing import Iterator, List, Optional, Generator, Any, Dict
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base, Session
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL from environment variables or use SQLite as default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./temp/test_app.db")

# Create base class for models
Base = declarative_base()

# Engine and session factory will be initialized in init_db()
engine: Optional[Engine] = None
SessionLocal: Optional[scoped_session] = None


def init_db(db_url: Optional[str] = None, echo: bool = True) -> Engine:
    """Initialize the database connection and session factory.
    
    Args:
        db_url: Database connection URL. If None, uses DATABASE_URL from environment.
        echo: Whether to echo SQL statements to stdout.
        
    Returns:
        The SQLAlchemy engine instance.
    """
    global engine, SessionLocal
    
    # Use provided db_url or fall back to environment variable
    url = db_url or DATABASE_URL
    logger.info(f"Initializing database connection to: {url}")
    
    # Create SQLAlchemy engine with appropriate configuration
    if url.startswith("sqlite"):
        # SQLite specific configuration
        engine = create_engine(
            url, 
            connect_args={"check_same_thread": False},
            echo=echo  # Enable SQL query logging
        )
    else:
        # PostgreSQL configuration
        engine = create_engine(
            url,
            pool_pre_ping=True,
            pool_recycle=300,  # Recycle connections after 5 minutes
            pool_size=5,
            max_overflow=10,
            echo=echo
        )
    
    # Create a scoped session factory
    SessionLocal = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )
    
    return engine


def get_db() -> Generator[Session, None, None]:
    """Dependency to get DB session for FastAPI.
    
    Yields:
        A SQLAlchemy session that will be automatically closed.
    """
    if SessionLocal is None:
        init_db()
        
    db = SessionLocal()  # type: ignore
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session() -> Iterator[Session]:
    """Context manager for database sessions.
    
    Usage:
        with db_session() as session:
            session.query(Model).all()
    
    Yields:
        A SQLAlchemy session that will be automatically closed and rolled back on exception.
    """
    if SessionLocal is None:
        init_db()
        
    session = SessionLocal()  # type: ignore
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_tables() -> None:
    """Create all database tables.
    
    This should be called after importing all models to ensure they are registered with SQLAlchemy.
    """
    if engine is None:
        init_db()
    
    # Import all models to ensure they are registered with SQLAlchemy
    # This avoids circular imports by importing only when needed
    from app.models import __all__  # noqa: F401
    
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)  # type: ignore
    logger.info("Database tables created successfully")


def get_table_names() -> List[str]:
    """Get a list of all table names in the database.
    
    Returns:
        List of table names as strings.
    """
    if engine is None:
        init_db()
        
    inspector = inspect(engine)  # type: ignore
    return inspector.get_table_names()


def drop_tables() -> None:
    """Drop all tables in the database.
    
    Warning: This will delete all data in the database.
    """
    if engine is None:
        init_db()
        
    logger.warning("Dropping all database tables!")
    Base.metadata.drop_all(bind=engine)  # type: ignore
    logger.info("All database tables dropped")


def reset_database() -> None:
    """Reset the database by dropping and recreating all tables.
    
    Warning: This will delete all data in the database.
    """
    drop_tables()
    create_tables()

# Initialize database and tables during application startup
def init_app() -> None:
    """Initialize the database and create tables during application startup.
    
    This should be called once during application startup from the main FastAPI app.
    Example:
        ```python
        from fastapi import FastAPI
        from app.database import init_app
        
        app = FastAPI()
        
        @app.on_event("startup")
        def startup_db_client():
            init_app()
        ```
    """
    logger.info("Initializing database connection...")
    init_db()
    logger.info("Creating database tables if they don't exist...")
    create_tables()
    logger.info("Database initialization completed successfully")
    
    # Log table information
    tables = get_table_names()
    logger.info(f"Available tables: {', '.join(tables)}")

