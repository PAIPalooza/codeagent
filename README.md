# CodeAgent - AI-Powered Development Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

CodeAgent is a comprehensive AI-powered development platform that enables rapid application creation through intelligent code generation, visual UI builders, and multi-agent coordination systems.

## 🚀 Features

### ✨ Core Capabilities
- **AI Code Generation**: Generate complete applications using AINative Studio APIs
- **Visual UI Builder**: Drag-and-drop interface for creating React components
- **Multi-Agent Coordination**: Orchestrate specialized agents for complex code generation
- **Real-time Streaming**: Live project generation status with Server-Sent Events
- **Multiple Tech Stacks**: Support for React, Vue, Next.js with various backends
- **Smart Planning**: Ollama-powered intelligent project planning

### 🎨 Visual Builder
- 10+ draggable UI components (Button, Input, Card, Form, Navigation, etc.)
- Real-time property editing
- Responsive design support
- Code generation from visual layouts
- Multiple styling frameworks (Tailwind CSS, Bootstrap, Custom CSS)

### 🔐 Authentication & Security
- JWT-based authentication system
- User registration and login
- Role-based access control (User, Premium, Admin)
- GitHub OAuth integration
- Secure password handling with bcrypt

### 🐳 Production Ready
- Complete Docker containerization
- Kubernetes deployment ready
- Comprehensive monitoring with Prometheus & Grafana
- Log aggregation with Loki
- Health checks and metrics
- Auto-scaling capabilities

### 📊 Monitoring & Analytics
- Real-time system metrics
- Application performance monitoring
- Error tracking and alerting
- Custom business metrics
- Grafana dashboards

## 🏗️ Architecture

CodeAgent follows a modern microservices architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │   PostgreSQL    │
│   (Port 80)     │────│   (Port 8000)   │────│   (Port 5432)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │  AINative APIs  │    │   Redis Cache   │
         │              │  (External)     │    │   (Port 6379)   │
         │              └─────────────────┘    └─────────────────┘
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Grafana       │    │   Prometheus    │    │     Ollama      │
│   (Port 3000)   │    │   (Port 9090)   │    │   (Port 11434)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- 4GB+ RAM recommended

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/codeagent.git
cd codeagent
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
nano .env
```

Required environment variables:
```env
# Database
POSTGRES_PASSWORD=changeme123
JWT_SECRET_KEY=your-super-secret-key-here

# AINative API (required for AI features)
AINATIVE_API_KEY=your-ainative-api-key
AINATIVE_BASE_URL=https://api.ainative.studio/api/v1
```

### 3. Deploy with Docker
```bash
# Full deployment (build, start, configure)
./deploy.sh deploy

# Or start individual services
./deploy.sh start
```

### 4. Access the Application
- **Frontend**: http://localhost:80
- **API Documentation**: http://localhost:8000/docs
- **Monitoring (Grafana)**: http://localhost:3000 (admin/admin123)
- **Metrics (Prometheus)**: http://localhost:9090

### 5. Create Admin User
```bash
./deploy.sh admin
```

## 📚 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user profile
- `PUT /api/v1/auth/me` - Update user profile

### Project Generation
- `POST /api/v1/generate-app` - Generate application from specifications
- `POST /api/v1/canvas/generate-code` - Generate code from visual canvas
- `GET /api/v1/projects/{id}` - Get project details
- `GET /api/v1/projects/{id}/logs` - Stream project logs

### Multi-Agent Coordination
- `POST /api/v1/coordination/create-workflow` - Create coordination workflow
- `POST /api/v1/coordination/execute-workflow/{id}` - Execute workflow
- `GET /api/v1/coordination/workflow/{id}/status` - Get workflow status

### Monitoring
- `GET /health` - Comprehensive health check
- `GET /metrics` - Prometheus metrics
- `GET /status` - Simple status check

## 🛠️ Development

### Local Development Setup

#### Backend Development
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🔧 Configuration

### Tech Stack Support

#### Frontend Frameworks
- **React**: Modern React with hooks and functional components
- **Vue.js**: Vue 3 with Composition API
- **Next.js**: Full-stack React framework with SSR

#### Backend Frameworks
- **FastAPI**: High-performance Python API framework
- **Django**: Full-featured Python web framework
- **Express.js**: Node.js web application framework

#### Databases
- **PostgreSQL**: Production-ready relational database
- **MongoDB**: NoSQL document database
- **MySQL**: Popular relational database

#### Styling Options
- **Tailwind CSS**: Utility-first CSS framework
- **Bootstrap**: Popular CSS framework
- **Custom CSS**: Traditional CSS styling

## 📊 Monitoring

### Health Checks
CodeAgent provides comprehensive health monitoring:

- **System Metrics**: CPU, Memory, Disk usage
- **Application Metrics**: Projects, Users, Error rates
- **Service Health**: Database, AINative API, Ollama connectivity
- **Performance Metrics**: Response times, throughput

### Grafana Dashboards
Access pre-built dashboards at http://localhost:3000:

1. **System Overview**: Resource usage and performance
2. **Application Metrics**: Business metrics and KPIs
3. **Error Tracking**: Error rates and failure analysis
4. **Service Health**: Service status and availability

### Prometheus Metrics
Custom metrics available at `/metrics`:
- `codeagent_total_projects`
- `codeagent_active_users`
- `codeagent_error_rate_percent`
- `codeagent_cpu_percent`
- `codeagent_memory_percent`

## 🚢 Deployment

### Production Deployment
```bash
# Clone repository
git clone https://github.com/your-org/codeagent.git
cd codeagent

# Configure environment
cp .env.example .env
# Edit .env with production values

# Deploy with monitoring
./deploy.sh deploy

# Check status
./deploy.sh status
```

### Deployment Commands
```bash
./deploy.sh deploy   # Full deployment
./deploy.sh start    # Start services
./deploy.sh stop     # Stop services
./deploy.sh status   # Show service status
./deploy.sh logs     # Show logs
./deploy.sh health   # Check service health
./deploy.sh backup   # Create data backup
```

## 🧪 Testing

### Test Coverage
```bash
# Run backend tests with coverage
cd backend
pytest --cov=app --cov-report=html

# Run frontend tests
cd frontend
npm test -- --coverage
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run quality checks
6. Submit a pull request

### Code Standards
- Python: Black formatting, PEP8 compliance
- JavaScript: ESLint, Prettier formatting
- Tests: Minimum 80% coverage required
- Documentation: Update relevant docs

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **Documentation**: Check this README and API docs at `/docs`
- **Issues**: GitHub Issues for bugs and feature requests
- **Discussions**: GitHub Discussions for questions

### Troubleshooting

#### Common Issues

**Database Connection Failed**
```bash
# Check database status
./deploy.sh status

# Check logs
./deploy.sh logs postgres
```

**AINative API Errors**
```bash
# Verify API key in .env
grep AINATIVE_API_KEY .env

# Test API connectivity
curl -H "Authorization: Bearer $AINATIVE_API_KEY" \
     https://api.ainative.studio/api/v1/health
```

**Frontend Build Failures**
```bash
# Clear node modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 🔮 Roadmap

### Short Term (v1.1)
- [ ] Real-time collaboration features
- [ ] Advanced code refactoring tools
- [ ] Plugin system for custom generators
- [ ] Enhanced GitHub integration

### Medium Term (v1.5)
- [ ] AI-powered code review
- [ ] Advanced debugging tools
- [ ] Cloud deployment automation
- [ ] Multi-language support

### Long Term (v2.0)
- [ ] Natural language to code generation
- [ ] Advanced AI agents ecosystem
- [ ] Enterprise features and SSO
- [ ] Marketplace for templates and plugins

---

**Built with ❤️ by the CodeAgent Team**

*Empowering developers with AI-powered code generation and intelligent development tools.*