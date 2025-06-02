import os
import logging
import time
from datetime import datetime
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base, init_app, get_db
from . import models, schemas
from .services.monitoring_service import monitoring_service

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to show all log messages
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# Explicitly set log levels for our app modules
logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

# Ensure SQLAlchemy logs are not too verbose
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Initialize the database and create tables
init_app()

app = FastAPI(
    title="CodeAgent API",
    description="API for CodeAgent - AI-powered code generation platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Request monitoring middleware
@app.middleware("http")
async def monitoring_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Increment request counter
    monitoring_service.increment_request_count()
    
    response = await call_next(request)
    
    # Track errors
    if response.status_code >= 400:
        monitoring_service.increment_error_count()
    
    # Log performance
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Log request
    path = request.url.path
    method = request.method
    logger.info(f"Incoming request: {method} {request.url}")
    
    # Process the request
    response = await call_next(request)
    
    # Log basic response info
    logger.info(f"Response status: {response.status_code}")
    
    # Special handling to inject download_url for project endpoints with specific project ID
    if response.status_code == 200 and path.startswith('/projects/') and len(path.split('/')) > 2 and '/' not in path[10:]:
        try:
            # Check if it's a specific project endpoint (not a collection or subpath)
            project_id = int(path.split('/')[2].split('?')[0])  # Extract ID, remove query params
            logger.info(f"RESPONSE PATCH: Adding download_url for project {project_id}")
            
            # Read the original response body
            original_body = b""
            async for chunk in response.body_iterator:
                original_body += chunk
            
            # Parse the body as JSON if possible
            try:
                import json
                body_dict = json.loads(original_body.decode())
                
                # Only proceed if we have a dict response and no download_url already
                if isinstance(body_dict, dict) and "download_url" not in body_dict:
                    logger.info("download_url missing from response, adding it manually")
                    
                    # Get the project directly from database
                    from sqlalchemy.orm import Session
                    from .database import SessionLocal
                    from .models import Project
                    
                    # Create a session
                    db = SessionLocal()
                    try:
                        # Query the project
                        project = db.query(Project).filter(Project.id == project_id).first()
                        if project and project.download_url:
                            # Add the download_url to the response body
                            body_dict["download_url"] = project.download_url
                            logger.info(f"Patched response with download_url: {project.download_url}")
                    finally:
                        db.close()
                    
                    # Create a new response with the modified body
                    from fastapi.responses import JSONResponse
                    patched_content = json.dumps(body_dict).encode()
                    return Response(
                        content=patched_content,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type="application/json"
                    )
            except Exception as e:
                logger.error(f"Error patching response: {e}")
                # If anything goes wrong, fall back to the original response
                
            # Recreate the stream for the original response
            from starlette.responses import StreamingResponse
            return StreamingResponse(
                content=iter([original_body]),
                status_code=response.status_code, 
                headers=dict(response.headers)
            )
        except (ValueError, IndexError) as e:
            logger.error(f"Error in project ID parsing: {e}")
    
    return response

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Event handlers
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    # Database initialization is already handled by init_app()
    # Additional startup tasks can go here
    pass

# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint for health check"""
    return {
        "message": "Welcome to CodeAgent API",
        "status": "running",
        "version": "0.1.0"
    }


# Import and include routers here
from .routers import projects as projects_router
from .routers import app_generation as app_generation_router
from .routers import auth as auth_router

# Include routers with appropriate prefixes
app.include_router(auth_router.router, tags=["authentication"])
app.include_router(projects_router.router, prefix="/projects", tags=["projects"])
app.include_router(app_generation_router.router, tags=["app-generation"])

# Enhanced health and monitoring endpoints

@app.get("/health", tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check endpoint."""
    try:
        health_data = await monitoring_service.get_comprehensive_health(db)
        status_code = 200
        
        if health_data["status"] == "warning":
            status_code = 200  # Still OK but with warnings
        elif health_data["status"] == "critical":
            status_code = 503  # Service unavailable
        
        return JSONResponse(content=health_data, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            content={
                "status": "critical",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            },
            status_code=503
        )

@app.get("/metrics", response_class=PlainTextResponse, tags=["Monitoring"])
async def prometheus_metrics(db: Session = Depends(get_db)):
    """Prometheus metrics endpoint."""
    try:
        metrics = monitoring_service.get_prometheus_metrics(db)
        return PlainTextResponse(content=metrics, media_type="text/plain")
    except Exception as e:
        logger.error(f"Error generating metrics: {str(e)}")
        return PlainTextResponse(
            content=f"# Error generating metrics: {str(e)}",
            status_code=500
        )

@app.get("/status", tags=["Health"])
async def simple_status():
    """Simple status endpoint for quick health checks."""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": int(monitoring_service.get_uptime().total_seconds())
    }

# Debug endpoint for download_url testing
@app.get("/debug/{project_id}", tags=["Debug"])
async def debug_download_url(project_id: int, db: Session = Depends(get_db)):
    """Debug endpoint for testing download_url serialization"""
    from .models import Project
    from fastapi.responses import JSONResponse
    
    # Get project directly
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Access the download_url directly
    download_url = project.download_url
    
    # Return both a direct value and a dict with the value
    return JSONResponse(content={
        "direct_download_url": download_url,
        "in_dict": {"download_url": download_url},
        "test_str": "This is a test value"
    })

# Error handlers
@app.exception_handler(404)
async def not_found_exception_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "Resource not found"},
    )

@app.exception_handler(500)
async def server_error_exception_handler(request, exc):
    """Handle 500 errors"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal server error occurred"},
    )
