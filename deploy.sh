#!/bin/bash

# CodeAgent Deployment Script
# This script handles the deployment of the CodeAgent application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check if Docker and Docker Compose are installed
check_dependencies() {
    log "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    log "Dependencies check passed"
}

# Create necessary directories
setup_directories() {
    log "Setting up directories..."
    
    mkdir -p backend/logs
    mkdir -p backend/downloads
    mkdir -p backend/temp_projects
    mkdir -p backend/data
    
    log "Directories created"
}

# Check for environment file
check_environment() {
    log "Checking environment configuration..."
    
    if [ ! -f .env ]; then
        warn ".env file not found"
        if [ -f .env.example ]; then
            info "Copying .env.example to .env"
            cp .env.example .env
            warn "Please update .env file with your actual configuration values"
            warn "Especially update: POSTGRES_PASSWORD, JWT_SECRET_KEY, AINATIVE_API_KEY"
        else
            error ".env.example file not found. Please create .env file manually."
            exit 1
        fi
    fi
    
    log "Environment configuration checked"
}

# Build and start services
deploy() {
    log "Starting deployment..."
    
    # Pull latest images
    info "Pulling latest Docker images..."
    docker-compose pull
    
    # Build custom images
    info "Building application images..."
    docker-compose build --no-cache
    
    # Start services
    info "Starting services..."
    docker-compose up -d
    
    # Wait for services to be healthy
    info "Waiting for services to be healthy..."
    sleep 30
    
    # Check service health
    check_health
    
    log "Deployment completed successfully!"
}

# Check service health
check_health() {
    log "Checking service health..."
    
    # Check backend health
    if curl -f http://localhost:8000/health &> /dev/null; then
        log "Backend service is healthy"
    else
        warn "Backend service might not be fully ready yet"
    fi
    
    # Check frontend
    if curl -f http://localhost:80 &> /dev/null; then
        log "Frontend service is healthy"
    else
        warn "Frontend service might not be fully ready yet"
    fi
    
    # Check monitoring services
    if curl -f http://localhost:9090 &> /dev/null; then
        log "Prometheus is healthy"
    else
        warn "Prometheus might not be fully ready yet"
    fi
    
    if curl -f http://localhost:3000 &> /dev/null; then
        log "Grafana is healthy"
    else
        warn "Grafana might not be fully ready yet"
    fi
}

# Show service status
show_status() {
    log "Service Status:"
    docker-compose ps
    
    echo ""
    info "Service URLs:"
    echo "  Frontend:    http://localhost:80"
    echo "  Backend API: http://localhost:8000"
    echo "  API Docs:    http://localhost:8000/docs"
    echo "  Prometheus:  http://localhost:9090"
    echo "  Grafana:     http://localhost:3000 (admin/admin123)"
    echo "  Ollama:      http://localhost:11434"
    echo ""
}

# Stop services
stop() {
    log "Stopping services..."
    docker-compose down
    log "Services stopped"
}

# Clean up everything including volumes
clean() {
    warn "This will remove all containers, networks, and volumes. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        log "Cleaning up everything..."
        docker-compose down -v --remove-orphans
        docker system prune -a -f
        log "Cleanup completed"
    else
        info "Cleanup cancelled"
    fi
}

# Show logs
logs() {
    if [ -n "$1" ]; then
        docker-compose logs -f "$1"
    else
        docker-compose logs -f
    fi
}

# Run database migrations
migrate() {
    log "Running database migrations..."
    docker-compose exec backend alembic upgrade head
    log "Migrations completed"
}

# Create admin user
create_admin() {
    log "Creating admin user..."
    docker-compose exec backend python -c "
from app.database import SessionLocal, init_db
from app.services.auth_service import AuthService
from app.models.user import UserRole

init_db()
db = SessionLocal()
auth_service = AuthService()

result = auth_service.create_user(
    db=db,
    email='admin@codeagent.local',
    username='admin',
    password='admin123',
    full_name='System Administrator'
)

if result.get('success'):
    user = db.query(User).filter(User.email == 'admin@codeagent.local').first()
    user.role = UserRole.ADMIN.value
    user.is_verified = True
    db.commit()
    print('Admin user created successfully')
    print('Email: admin@codeagent.local')
    print('Password: admin123')
else:
    print(f'Failed to create admin user: {result.get(\"message\")}')

db.close()
"
    log "Admin user creation completed"
}

# Backup data
backup() {
    log "Creating backup..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_dir="backup_$timestamp"
    
    mkdir -p "$backup_dir"
    
    # Backup database
    docker-compose exec postgres pg_dump -U codeagent codeagent > "$backup_dir/database.sql"
    
    # Backup application data
    docker cp "$(docker-compose ps -q backend)":/app/data "$backup_dir/"
    docker cp "$(docker-compose ps -q backend)":/app/downloads "$backup_dir/"
    
    # Create archive
    tar -czf "$backup_dir.tar.gz" "$backup_dir"
    rm -rf "$backup_dir"
    
    log "Backup created: $backup_dir.tar.gz"
}

# Main script
case "$1" in
    deploy)
        check_dependencies
        setup_directories
        check_environment
        deploy
        show_status
        ;;
    start)
        docker-compose up -d
        show_status
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 5
        docker-compose up -d
        show_status
        ;;
    status)
        show_status
        ;;
    logs)
        logs "$2"
        ;;
    clean)
        clean
        ;;
    migrate)
        migrate
        ;;
    admin)
        create_admin
        ;;
    backup)
        backup
        ;;
    health)
        check_health
        ;;
    *)
        echo "Usage: $0 {deploy|start|stop|restart|status|logs|clean|migrate|admin|backup|health}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Full deployment (build, start, configure)"
        echo "  start    - Start services"
        echo "  stop     - Stop services"
        echo "  restart  - Restart services"
        echo "  status   - Show service status and URLs"
        echo "  logs     - Show logs (optionally for specific service)"
        echo "  clean    - Remove all containers and volumes"
        echo "  migrate  - Run database migrations"
        echo "  admin    - Create admin user"
        echo "  backup   - Create data backup"
        echo "  health   - Check service health"
        exit 1
        ;;
esac