# CodeAgent

CodeAgent is a powerful tool for generating and managing development environments and applications. It provides a streamlined workflow for setting up projects, managing dependencies, and deploying applications.

## Features

- **Project Generation**: Quickly generate new projects with various tech stacks
- **Development Environment**: Pre-configured development environment with all necessary tools
- **Multi-Stack Support**: Support for multiple technology stacks (React, Vue, Node.js, Python, etc.)
- **Containerization**: Built-in support for Docker and containerized development
- **API-First**: Comprehensive API for integration with other tools and services

## Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Ollama (for local LLM processing)
- AINative API key (for AI-powered code generation)

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the values in `.env` with your configuration

5. Run the backend server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## Development

### Project Structure

```
codeagent/
├── backend/               # Backend application
│   ├── app/               # Main application package
│   ├── tests/             # Test files
│   ├── venv/              # Python virtual environment
│   ├── main.py            # FastAPI application entry point
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
├── frontend/              # Frontend application
│   ├── public/            # Static files
│   ├── src/               # Source files
│   ├── package.json       # Node.js dependencies
│   └── .env               # Frontend environment variables
├── .gitignore             # Git ignore file
└── README.md              # This file
```

## API Documentation

Once the backend is running, you can access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
