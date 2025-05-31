import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, init_models
from . import models, schemas

# Initialize the database and create tables
Base = init_models()

app = FastAPI(
    title="CodeAgent API",
    description="API for CodeAgent - AI-powered code generation platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Event handlers
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    # Ensure the database is created and tables exist
    Base.metadata.create_all(bind=engine)

# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint for health check"""
    return {
        "message": "Welcome to CodeAgent API",
        "status": "running",
        "version": "0.1.0"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "API is running",
        "database": "connected" if engine.connect() else "disconnected"
    }

# Import and include routers here
from .routers import projects as projects_router
from .routers import app_generation as app_generation_router

# Include routers
app.include_router(projects_router.router)
app.include_router(app_generation_router.router)

# Error handlers
@app.exception_handler(404)
async def not_found_exception_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": "The requested resource was not found"},
    )

@app.exception_handler(500)
async def server_error_exception_handler(request, exc):
    """Handle 500 errors"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal server error occurred"},
    )
