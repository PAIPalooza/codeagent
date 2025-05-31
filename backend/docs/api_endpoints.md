# CodeAgent API Documentation

## App Generation Endpoints

### Generate App

**Endpoint:** `POST /api/v1/generate-app`

**Description:** Generates an application based on the provided specification. This endpoint validates the input, creates a generation plan using LangChain and Ollama, and stores the project and generation steps in the database.

**Request Body:**
```json
{
  "project_name": "TaskManager",
  "description": "A simple task management application with user authentication",
  "features": ["User authentication", "Task creation", "Task completion"],
  "tech_stack": {
    "frontend": ["React", "Tailwind CSS"],
    "backend": ["FastAPI", "SQLAlchemy"],
    "database": ["PostgreSQL"]
  },
  "styling": "Tailwind CSS with a clean, modern interface"
}
```

**Response:**
```json
{
  "status": "in_progress",
  "project_id": "6039ca77-e6cf-4f32-8e82-97297e3e306d"
}
```

**Status Codes:**
- `200 OK`: App generation started successfully
- `400 Bad Request`: Invalid app specification
- `500 Internal Server Error`: Error during app generation

### Recall Last App

**Endpoint:** `GET /api/v1/recall-last-app`

**Description:** Retrieves the specification of the most recently generated app from memory.

**Response:**
```json
{
  "project_name": "TaskManager",
  "description": "A simple task management application",
  "features": [
    "User authentication",
    "Task CRUD"
  ],
  "tech_stack": {
    "frontend": ["React"],
    "backend": ["FastAPI"]
  },
  "styling": "Minimal and clean"
}
```

**Status Codes:**
- `200 OK`: App specification retrieved successfully
- `404 Not Found`: No app specifications found in memory
- `500 Internal Server Error`: Error retrieving app specification
