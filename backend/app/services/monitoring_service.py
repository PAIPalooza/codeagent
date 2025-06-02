"""
Monitoring and Health Check Service

This service provides comprehensive monitoring capabilities including:
- Application health checks
- Performance metrics
- Resource usage monitoring
- Error tracking
- Custom metrics for business logic
"""

import logging
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import asyncio
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..database import get_db, engine
from ..models.project import Project, ProjectStatus
from ..models.user import User

logger = logging.getLogger(__name__)


@dataclass
class HealthMetrics:
    """Health metrics data structure."""
    timestamp: datetime
    status: str  # healthy, warning, critical
    response_time_ms: float
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    active_connections: int
    total_projects: int
    active_users: int
    error_rate_percent: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class ServiceHealth:
    """Service health status."""
    service: str
    status: str  # up, down, degraded
    response_time_ms: Optional[float]
    last_check: datetime
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['last_check'] = self.last_check.isoformat()
        return data


class MonitoringService:
    """Service for monitoring application health and performance."""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.error_count = 0
        self.request_count = 0
        self.last_health_check = None
        
    def get_uptime(self) -> timedelta:
        """Get application uptime."""
        return datetime.utcnow() - self.start_time
    
    def increment_request_count(self):
        """Increment total request counter."""
        self.request_count += 1
    
    def increment_error_count(self):
        """Increment error counter."""
        self.error_count += 1
    
    def get_error_rate(self) -> float:
        """Calculate error rate percentage."""
        if self.request_count == 0:
            return 0.0
        return (self.error_count / self.request_count) * 100
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system resource metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Network connections
            connections = len(psutil.net_connections())
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": disk_percent,
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "active_connections": connections,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {str(e)}")
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "disk_percent": 0,
                "active_connections": 0,
                "error": str(e)
            }
    
    async def check_database_health(self) -> ServiceHealth:
        """Check database connectivity and performance."""
        start_time = time.time()
        
        try:
            # Test database connection with a simple query
            from ..database import SessionLocal
            db = SessionLocal()
            db.execute(text("SELECT 1")).fetchone()
            db.close()
            
            response_time = (time.time() - start_time) * 1000
            
            return ServiceHealth(
                service="database",
                status="up",
                response_time_ms=response_time,
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return ServiceHealth(
                service="database",
                status="down",
                response_time_ms=None,
                last_check=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def check_ainative_health(self) -> ServiceHealth:
        """Check AINative API connectivity."""
        start_time = time.time()
        
        try:
            import os
            api_key = os.getenv("AINATIVE_API_KEY")
            base_url = os.getenv("AINATIVE_BASE_URL", "https://api.ainative.studio/api/v1")
            
            if not api_key:
                return ServiceHealth(
                    service="ainative",
                    status="degraded",
                    response_time_ms=None,
                    last_check=datetime.utcnow(),
                    error_message="API key not configured"
                )
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{base_url}/health", headers=headers)
                
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return ServiceHealth(
                    service="ainative",
                    status="up",
                    response_time_ms=response_time,
                    last_check=datetime.utcnow()
                )
            else:
                return ServiceHealth(
                    service="ainative",
                    status="degraded",
                    response_time_ms=response_time,
                    last_check=datetime.utcnow(),
                    error_message=f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            logger.error(f"AINative health check failed: {str(e)}")
            return ServiceHealth(
                service="ainative",
                status="down",
                response_time_ms=None,
                last_check=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def check_ollama_health(self) -> ServiceHealth:
        """Check Ollama service connectivity."""
        start_time = time.time()
        
        try:
            import os
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{ollama_url}/api/tags")
                
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return ServiceHealth(
                    service="ollama",
                    status="up",
                    response_time_ms=response_time,
                    last_check=datetime.utcnow()
                )
            else:
                return ServiceHealth(
                    service="ollama",
                    status="degraded",
                    response_time_ms=response_time,
                    last_check=datetime.utcnow(),
                    error_message=f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            logger.warning(f"Ollama health check failed: {str(e)}")
            return ServiceHealth(
                service="ollama",
                status="down",
                response_time_ms=None,
                last_check=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def get_application_metrics(self, db: Session) -> Dict[str, Any]:
        """Get application-specific metrics."""
        try:
            # Total projects
            total_projects = db.query(Project).count()
            
            # Active projects (in progress or generating)
            active_projects = db.query(Project).filter(
                Project.status.in_([
                    ProjectStatus.IN_PROGRESS,
                    ProjectStatus.GENERATING,
                    ProjectStatus.COORDINATING
                ])
            ).count()
            
            # Completed projects
            completed_projects = db.query(Project).filter(
                Project.status == ProjectStatus.SUCCESS
            ).count()
            
            # Failed projects
            failed_projects = db.query(Project).filter(
                Project.status == ProjectStatus.FAILED
            ).count()
            
            # Total users
            total_users = db.query(User).count()
            
            # Active users (logged in within last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            active_users = db.query(User).filter(
                User.last_login > yesterday
            ).count() if hasattr(User, 'last_login') else 0
            
            # Recent projects (created in last hour)
            recent_cutoff = datetime.utcnow() - timedelta(hours=1)
            recent_projects = db.query(Project).filter(
                Project.created_at > recent_cutoff
            ).count()
            
            return {
                "total_projects": total_projects,
                "active_projects": active_projects,
                "completed_projects": completed_projects,
                "failed_projects": failed_projects,
                "success_rate_percent": round((completed_projects / max(total_projects, 1)) * 100, 2),
                "total_users": total_users,
                "active_users": active_users,
                "recent_projects_1h": recent_projects,
                "uptime_seconds": int(self.get_uptime().total_seconds()),
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "error_rate_percent": round(self.get_error_rate(), 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting application metrics: {str(e)}")
            return {
                "total_projects": 0,
                "active_projects": 0,
                "completed_projects": 0,
                "failed_projects": 0,
                "success_rate_percent": 0,
                "total_users": 0,
                "active_users": 0,
                "recent_projects_1h": 0,
                "uptime_seconds": int(self.get_uptime().total_seconds()),
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "error_rate_percent": round(self.get_error_rate(), 2),
                "error": str(e)
            }
    
    async def get_comprehensive_health(self, db: Session) -> Dict[str, Any]:
        """Get comprehensive health status of all services."""
        start_time = time.time()
        
        # Get system metrics
        system_metrics = self.get_system_metrics()
        
        # Get application metrics
        app_metrics = await self.get_application_metrics(db)
        
        # Check service health
        health_checks = await asyncio.gather(
            self.check_database_health(),
            self.check_ainative_health(),
            self.check_ollama_health(),
            return_exceptions=True
        )
        
        # Process health check results
        services = {}
        overall_status = "healthy"
        
        for check in health_checks:
            if isinstance(check, ServiceHealth):
                services[check.service] = check.to_dict()
                if check.status == "down":
                    overall_status = "critical"
                elif check.status == "degraded" and overall_status == "healthy":
                    overall_status = "warning"
            else:
                # Handle exceptions
                logger.error(f"Health check exception: {check}")
        
        # Determine overall status based on system metrics
        if system_metrics.get("cpu_percent", 0) > 80:
            overall_status = "warning" if overall_status == "healthy" else overall_status
        if system_metrics.get("memory_percent", 0) > 85:
            overall_status = "warning" if overall_status == "healthy" else overall_status
        if system_metrics.get("disk_percent", 0) > 90:
            overall_status = "critical"
        
        response_time = (time.time() - start_time) * 1000
        
        health_data = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "response_time_ms": round(response_time, 2),
            "system": system_metrics,
            "application": app_metrics,
            "services": services,
            "uptime": {
                "seconds": int(self.get_uptime().total_seconds()),
                "human": str(self.get_uptime()).split('.')[0]  # Remove microseconds
            }
        }
        
        self.last_health_check = health_data
        return health_data
    
    def get_prometheus_metrics(self, db: Session) -> str:
        """Generate Prometheus-compatible metrics."""
        try:
            system_metrics = self.get_system_metrics()
            app_metrics = asyncio.run(self.get_application_metrics(db))
            
            metrics = []
            
            # System metrics
            metrics.append(f"# HELP codeagent_cpu_percent CPU usage percentage")
            metrics.append(f"# TYPE codeagent_cpu_percent gauge")
            metrics.append(f"codeagent_cpu_percent {system_metrics.get('cpu_percent', 0)}")
            
            metrics.append(f"# HELP codeagent_memory_percent Memory usage percentage")
            metrics.append(f"# TYPE codeagent_memory_percent gauge")
            metrics.append(f"codeagent_memory_percent {system_metrics.get('memory_percent', 0)}")
            
            metrics.append(f"# HELP codeagent_disk_percent Disk usage percentage")
            metrics.append(f"# TYPE codeagent_disk_percent gauge")
            metrics.append(f"codeagent_disk_percent {system_metrics.get('disk_percent', 0)}")
            
            # Application metrics
            metrics.append(f"# HELP codeagent_total_projects Total number of projects")
            metrics.append(f"# TYPE codeagent_total_projects counter")
            metrics.append(f"codeagent_total_projects {app_metrics.get('total_projects', 0)}")
            
            metrics.append(f"# HELP codeagent_active_projects Number of active projects")
            metrics.append(f"# TYPE codeagent_active_projects gauge")
            metrics.append(f"codeagent_active_projects {app_metrics.get('active_projects', 0)}")
            
            metrics.append(f"# HELP codeagent_total_users Total number of users")
            metrics.append(f"# TYPE codeagent_total_users counter")
            metrics.append(f"codeagent_total_users {app_metrics.get('total_users', 0)}")
            
            metrics.append(f"# HELP codeagent_error_rate_percent Error rate percentage")
            metrics.append(f"# TYPE codeagent_error_rate_percent gauge")
            metrics.append(f"codeagent_error_rate_percent {app_metrics.get('error_rate_percent', 0)}")
            
            metrics.append(f"# HELP codeagent_uptime_seconds Application uptime in seconds")
            metrics.append(f"# TYPE codeagent_uptime_seconds counter")
            metrics.append(f"codeagent_uptime_seconds {app_metrics.get('uptime_seconds', 0)}")
            
            return "\n".join(metrics)
            
        except Exception as e:
            logger.error(f"Error generating Prometheus metrics: {str(e)}")
            return f"# Error generating metrics: {str(e)}"


# Global monitoring service instance
monitoring_service = MonitoringService()