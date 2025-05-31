from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment variables or use SQLite as default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# Create SQLAlchemy engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        echo=True  # Enable SQL query logging
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,  # Recycle connections after 5 minutes
        pool_size=5,
        max_overflow=10,
    )

# Create a scoped session factory
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

def get_db():
    """Dependency to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import all models here to ensure they are registered with SQLAlchemy
# This must be after the engine is created but before creating tables
from app.models.base import Base
from app.models.project import Project
from app.models.generation_step import GenerationStep
from app.models.log import Log

# Create all tables
def create_tables():
    """Create all database tables"""
    # Import models to ensure they are registered with SQLAlchemy
    from app.models import project, generation_step, log
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
