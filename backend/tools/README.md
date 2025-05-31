# AINative Tool Wrappers

This directory contains Python wrapper classes around AINative API endpoints for code generation, refactoring, and memory management.

## Overview

These tools provide a consistent interface for interacting with AINative's API endpoints, handling authentication, error management, and response formatting. Each tool extends the `AINativeBaseTool` abstract base class.

## Configuration

The tools require the following environment variables to be set:

- `AINATIVE_API_KEY`: Your AINative API authentication key
- `AINATIVE_BASE_URL`: The base URL for the AINative API (e.g., `https://api.ainative.com/v1`)

## Available Tools

### CodeGenCreateTool

Wrapper for the `code-generation/create` endpoint.

#### Methods

- `_call(project_name, description, features, tech_stack, styling=None, canvas_layout=None, **kwargs)`: 
  Generate new code based on project specifications.

#### Example

```python
tool = CodeGenCreateTool()
result = await tool._call(
    project_name="My App",
    description="A Todo application",
    features=["User authentication", "Task CRUD operations"],
    tech_stack="React + FastAPI + PostgreSQL"
)
```

### CodeGenRefactorTool

Wrapper for the `code-generation/refactor` endpoint.

#### Methods

- `_call(code, instructions, file_path=None, language=None, **kwargs)`: 
  Refactor existing code based on provided instructions.

#### Example

```python
tool = CodeGenRefactorTool()
result = await tool._call(
    code="def add(a, b):\n    return a + b",
    instructions="Add type hints",
    file_path="math_utils.py",
    language="python"
)
```

### MemoryStoreTool

Wrapper for the `agent/memory` endpoint.

#### Methods

- `_call(content, title, tags, project_id=None, memory_id=None, action="create", **kwargs)`: 
  Store or update information in the agent memory system.

#### Example

```python
tool = MemoryStoreTool()
result = await tool._call(
    content="Project requirements include user authentication",
    title="Project Requirements",
    tags=["requirements", "authentication"],
    project_id="project-123"
)
```

### MemorySearchTool

Wrapper for the `agent/memory/search` endpoint.

#### Methods

- `_call(query, project_id=None, tags=None, limit=10, **kwargs)`: 
  Search for information in the agent memory system.

#### Example

```python
tool = MemorySearchTool()
result = await tool._call(
    query="authentication requirements",
    project_id="project-123",
    tags=["requirements"],
    limit=5
)
```

## Error Handling

All tools return a structured error object if the request fails:

```json
{
    "error": true,
    "message": "Error description",
    "details": { ... }  // Optional additional error details
}
```

## Testing

The tools can be tested using the `test_ainative_tools.py` script in the root directory:

```bash
python test_ainative_tools.py
```
