"""
Code Generation Service

This service provides code generation capabilities for different tech stacks
and templates, implementing the functionality that would come from AINative's
code-generation APIs.
"""

import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import asyncio
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))
from tools.code_gen_refactor_tool import CodeGenRefactorTool
from tools.memory_store_tool import MemoryStoreTool

logger = logging.getLogger(__name__)


class CodeGenerationService:
    """Service for generating code based on templates and specifications."""
    
    def __init__(self):
        self.templates_dir = os.path.join(os.path.dirname(__file__), "../templates")
        os.makedirs(self.templates_dir, exist_ok=True)
        self.refactor_tool = CodeGenRefactorTool()
        self.memory_tool = MemoryStoreTool()
        
    def create_code(self, template: str, file_path: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate new code based on a template.
        
        Args:
            template: Template type (e.g., 'sqlalchemy-model', 'react-component')
            file_path: Target file path for the generated code
            variables: Variables to substitute in the template
            
        Returns:
            Dictionary containing generated code and metadata
        """
        try:
            logger.info(f"Generating code for template: {template}")
            
            # Get template content
            template_content = self._get_template(template)
            
            # Process variables and generate code
            generated_code = self._process_template(template_content, variables)
            
            return {
                "success": True,
                "file_path": file_path,
                "code": generated_code,
                "template": template,
                "variables_used": variables,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            return {
                "error": True,
                "message": str(e),
                "template": template,
                "file_path": file_path
            }
    
    async def refactor_code(self, file_path: str, existing_code: str, instructions: str) -> Dict[str, Any]:
        """
        Refactor existing code based on instructions using AINative API.
        
        Args:
            file_path: Path of the file being refactored
            existing_code: Current code content
            instructions: Refactoring instructions
            
        Returns:
            Dictionary containing refactored code
        """
        try:
            logger.info(f"Refactoring code for file: {file_path} using AINative API")
            
            # Determine language from file extension
            language = self._detect_language(file_path)
            
            # Use AINative refactor tool
            response = await self.refactor_tool._call(
                code=existing_code,
                instructions=instructions,
                file_path=file_path,
                language=language
            )
            
            if response.get("success"):
                refactored_code = response.get("data", {}).get("refactored_code", existing_code)
                
                # Store result in memory for future reference
                await self.memory_tool._call(
                    content=f"Refactored {file_path}: {instructions}",
                    title=f"Code Refactoring: {os.path.basename(file_path)}",
                    tags=["code_refactoring", language, "automated"]
                )
                
                return {
                    "success": True,
                    "file_path": file_path,
                    "code": refactored_code,
                    "original_code": existing_code,
                    "instructions": instructions,
                    "changes_made": response.get("data", {}).get("changes_made", []),
                    "confidence_score": response.get("data", {}).get("confidence_score", 1.0),
                    "refactored_at": datetime.utcnow().isoformat()
                }
            else:
                # Fallback to local refactoring if API fails
                logger.warning("AINative API failed, falling back to local refactoring")
                refactored_code = self._apply_refactoring(existing_code, instructions, file_path)
                
                return {
                    "success": True,
                    "file_path": file_path,
                    "code": refactored_code,
                    "original_code": existing_code,
                    "instructions": instructions,
                    "refactored_at": datetime.utcnow().isoformat(),
                    "fallback_used": True
                }
            
        except Exception as e:
            logger.error(f"Error refactoring code: {str(e)}")
            return {
                "error": True,
                "message": str(e),
                "file_path": file_path
            }
    
    def _get_template(self, template: str) -> str:
        """Get template content for the specified template type."""
        templates = {
            "sqlalchemy-model": self._get_sqlalchemy_model_template(),
            "fastapi-route": self._get_fastapi_route_template(),
            "react-component": self._get_react_component_template(),
            "vue-component": self._get_vue_component_template(),
            "mongoose-model": self._get_mongoose_model_template(),
            "express-route": self._get_express_route_template(),
            "django-model": self._get_django_model_template(),
            "django-rest-route": self._get_django_rest_route_template(),
            "next-page": self._get_next_page_template(),
            "next-api-route": self._get_next_api_route_template(),
            "package-json": self._get_package_json_template(),
            "requirements-txt": self._get_requirements_txt_template(),
        }
        
        if template not in templates:
            raise ValueError(f"Unknown template: {template}")
        
        return templates[template]
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.vue': 'vue',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.sql': 'sql'
        }
        return language_map.get(ext, 'text')
    
    def _process_template(self, template_content: str, variables: Dict[str, Any]) -> str:
        """Process template with variables."""
        try:
            # Simple variable substitution
            result = template_content
            for key, value in variables.items():
                placeholder = f"{{{key}}}"
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                result = result.replace(placeholder, str(value))
            return result
        except Exception as e:
            logger.error(f"Error processing template: {str(e)}")
            return f"# Error processing template: {str(e)}\n"
    
    def _apply_refactoring(self, existing_code: str, instructions: str, file_path: str) -> str:
        """Apply refactoring instructions to existing code."""
        # Simple refactoring based on common instructions
        result = existing_code
        
        if "add tailwind" in instructions.lower() or "tailwindcss" in instructions.lower():
            result = self._add_tailwind_classes(result)
        elif "add bootstrap" in instructions.lower():
            result = self._add_bootstrap_classes(result)
        elif "add error handling" in instructions.lower():
            result = self._add_error_handling(result, file_path)
        elif "add documentation" in instructions.lower():
            result = self._add_documentation(result, file_path)
        
        # Add a comment about the refactoring
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        comment = f"# Refactored on {timestamp}: {instructions}\n"
        result = comment + result
        
        return result
    
    def _add_tailwind_classes(self, code: str) -> str:
        """Add Tailwind CSS classes to components."""
        # Simple replacements for common patterns
        replacements = {
            'className=""': 'className="p-4 bg-white rounded-lg shadow-md"',
            'className="form"': 'className="space-y-4"',
            'className="button"': 'className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"',
            'className="input"': 'className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"'
        }
        
        result = code
        for old, new in replacements.items():
            result = result.replace(old, new)
        
        return result
    
    def _add_bootstrap_classes(self, code: str) -> str:
        """Add Bootstrap classes to components."""
        replacements = {
            'className=""': 'className="card p-3"',
            'className="form"': 'className="form"',
            'className="button"': 'className="btn btn-primary"',
            'className="input"': 'className="form-control"'
        }
        
        result = code
        for old, new in replacements.items():
            result = result.replace(old, new)
        
        return result
    
    def _add_error_handling(self, code: str, file_path: str) -> str:
        """Add basic error handling to code."""
        if file_path.endswith('.py'):
            return f"""try:
{code}
except Exception as e:
    logger.error(f"Error in {file_path}: {{str(e)}}")
    raise
"""
        elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
            return f"""try {{
{code}
}} catch (error) {{
    console.error('Error in {file_path}:', error);
    throw error;
}}
"""
        return code
    
    def _add_documentation(self, code: str, file_path: str) -> str:
        """Add documentation to code."""
        if file_path.endswith('.py'):
            return f'''"""
Generated code for {file_path}
Auto-generated documentation
"""

{code}'''
        elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
            return f'''/**
 * Generated code for {file_path}
 * Auto-generated documentation
 */

{code}'''
        return code
    
    # Template definitions
    def _get_sqlalchemy_model_template(self) -> str:
        return '''"""
{project_name} - Database Models
Generated by CodeAgent
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# TODO: Add models based on features: {features}
# Tech Stack: {tech_stack}
# Styling: {styling}
'''
    
    def _get_fastapi_route_template(self) -> str:
        return '''"""
{project_name} - API Routes
Generated by CodeAgent
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas
from .database import get_db

router = APIRouter()

@router.get("/users/", response_model=List[schemas.User])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users."""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.get("/users/{{user_id}}", response_model=schemas.User)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# TODO: Add routes based on features: {features}
# Tech Stack: {tech_stack}
# Styling: {styling}
'''
    
    def _get_react_component_template(self) -> str:
        return '''import React, {{ useState, useEffect }} from 'react';
import './App.css';

function App() {{
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {{
    // TODO: Fetch data from API
    setLoading(false);
  }}, []);

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">Error: {{error}}</div>;

  return (
    <div className="App">
      <header className="App-header">
        <h1>{project_name}</h1>
        <p>{description}</p>
      </header>
      
      <main className="App-main">
        {{/* TODO: Implement features: {features} */}}
        <div className="feature-list">
          <h2>Features</h2>
          <ul>
            <li>Feature 1: User Interface</li>
            <li>Feature 2: Data Management</li>
            <li>Feature 3: API Integration</li>
          </ul>
        </div>
      </main>
      
      <footer className="App-footer">
        <p>Built with {tech_stack} and {styling}</p>
      </footer>
    </div>
  );
}}

export default App;
'''
    
    def _get_vue_component_template(self) -> str:
        return '''<template>
  <div class="app">
    <header class="app-header">
      <h1>{project_name}</h1>
      <p>{description}</p>
    </header>
    
    <main class="app-main">
      <!-- TODO: Implement features: {features} -->
      <div class="feature-list">
        <h2>Features</h2>
        <ul>
          <li v-for="feature in features" :key="feature">{{ feature }}</li>
        </ul>
      </div>
    </main>
    
    <footer class="app-footer">
      <p>Built with {tech_stack} and {styling}</p>
    </footer>
  </div>
</template>

<script>
export default {{
  name: 'App',
  data() {{
    return {{
      features: [
        'User Interface',
        'Data Management', 
        'API Integration'
      ],
      loading: false,
      error: null
    }}
  }},
  mounted() {{
    // TODO: Initialize app
    console.log('App mounted for {project_name}');
  }}
}}
</script>

<style scoped>
.app {{
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}}

.app-header {{
  background-color: #42b883;
  padding: 20px;
  color: white;
}}

.app-main {{
  padding: 20px;
}}

.app-footer {{
  background-color: #35495e;
  padding: 10px;
  color: white;
  margin-top: 20px;
}}
</style>
'''
    
    def _get_mongoose_model_template(self) -> str:
        return '''/**
 * {project_name} - Database Models
 * Generated by CodeAgent
 */

const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({{
  email: {{
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    trim: true
  }},
  username: {{
    type: String,
    required: true,
    unique: true,
    trim: true
  }},
  password: {{
    type: String,
    required: true
  }},
  isActive: {{
    type: Boolean,
    default: true
  }}
}}, {{
  timestamps: true
}});

const User = mongoose.model('User', userSchema);

module.exports = {{
  User
}};

// TODO: Add models based on features: {features}
// Tech Stack: {tech_stack}
// Styling: {styling}
'''
    
    def _get_express_route_template(self) -> str:
        return '''/**
 * {project_name} - API Routes
 * Generated by CodeAgent
 */

const express = require('express');
const router = express.Router();
const {{ User }} = require('../models/User');

// Get all users
router.get('/users', async (req, res) => {{
  try {{
    const users = await User.find({{ isActive: true }});
    res.json(users);
  }} catch (error) {{
    res.status(500).json({{ error: error.message }});
  }}
}});

// Get user by ID
router.get('/users/:id', async (req, res) => {{
  try {{
    const user = await User.findById(req.params.id);
    if (!user) {{
      return res.status(404).json({{ error: 'User not found' }});
    }}
    res.json(user);
  }} catch (error) {{
    res.status(500).json({{ error: error.message }});
  }}
}});

// Create new user
router.post('/users', async (req, res) => {{
  try {{
    const user = new User(req.body);
    await user.save();
    res.status(201).json(user);
  }} catch (error) {{
    res.status(400).json({{ error: error.message }});
  }}
}});

module.exports = router;

// TODO: Add routes based on features: {features}
// Tech Stack: {tech_stack}
// Styling: {styling}
'''
    
    def _get_django_model_template(self) -> str:
        return '''"""
{project_name} - Database Models
Generated by CodeAgent
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    """Custom user model."""
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'auth_user'

# TODO: Add models based on features: {features}
# Tech Stack: {tech_stack}
# Styling: {styling}
'''
    
    def _get_django_rest_route_template(self) -> str:
        return '''"""
{project_name} - API URLs
Generated by CodeAgent
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),
]

# TODO: Add URLs based on features: {features}
# Tech Stack: {tech_stack}
# Styling: {styling}
'''
    
    def _get_next_page_template(self) -> str:
        return '''import {{ useState, useEffect }} from 'react';
import Head from 'next/head';
import styles from '../styles/Home.module.css';

export default function Home() {{
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {{
    // TODO: Fetch data from API
    setLoading(false);
  }}, []);

  return (
    <div className={{styles.container}}>
      <Head>
        <title>{project_name}</title>
        <meta name="description" content="{description}" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={{styles.main}}>
        <h1 className={{styles.title}}>
          Welcome to {project_name}
        </h1>

        <p className={{styles.description}}>
          {description}
        </p>

        <div className={{styles.grid}}>
          {{/* TODO: Implement features: {features} */}}
          <div className={{styles.card}}>
            <h2>Feature 1</h2>
            <p>First feature implementation</p>
          </div>
          
          <div className={{styles.card}}>
            <h2>Feature 2</h2>
            <p>Second feature implementation</p>
          </div>
        </div>
      </main>

      <footer className={{styles.footer}}>
        <p>Built with {tech_stack} and {styling}</p>
      </footer>
    </div>
  );
}}
'''
    
    def _get_next_api_route_template(self) -> str:
        return '''/**
 * {project_name} - Next.js API Route
 * Generated by CodeAgent
 */

export default function handler(req, res) {{
  const {{ method }} = req;

  switch (method) {{
    case 'GET':
      // TODO: Handle GET request
      res.status(200).json({{ 
        message: 'API endpoint for {project_name}',
        features: {features},
        tech_stack: '{tech_stack}'
      }});
      break;
      
    case 'POST':
      // TODO: Handle POST request
      res.status(201).json({{ message: 'Created successfully' }});
      break;
      
    default:
      res.setHeader('Allow', ['GET', 'POST']);
      res.status(405).end(`Method ${{method}} Not Allowed`);
  }}
}}
'''
    
    def _get_package_json_template(self) -> str:
        tech_stack = "{tech_stack}"
        styling = "{styling}"
        
        if "React" in tech_stack:
            return '''{{
  "name": "{project_name}",
  "version": "0.1.0",
  "private": true,
  "dependencies": {{
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.3.0"''' + (''',"tailwindcss": "^3.2.0"''' if "Tailwind" in styling else ''',"bootstrap": "^5.2.0"''' if "Bootstrap" in styling else '') + '''
  }},
  "scripts": {{
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }},
  "eslintConfig": {{
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  }},
  "browserslist": {{
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }}
}}'''
        elif "Vue" in tech_stack:
            return '''{{
  "name": "{project_name}",
  "version": "0.1.0",
  "private": true,
  "dependencies": {{
    "vue": "^3.2.0",
    "vue-router": "^4.1.0",
    "axios": "^1.3.0"''' + (''',"tailwindcss": "^3.2.0"''' if "Tailwind" in styling else ''',"bootstrap": "^5.2.0"''' if "Bootstrap" in styling else '') + '''
  }},
  "devDependencies": {{
    "@vitejs/plugin-vue": "^4.0.0",
    "vite": "^4.0.0"
  }},
  "scripts": {{
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }}
}}'''
        else:  # Next.js
            return '''{{
  "name": "{project_name}",
  "version": "0.1.0",
  "private": true,
  "dependencies": {{
    "next": "^13.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.3.0"''' + (''',"tailwindcss": "^3.2.0"''' if "Tailwind" in styling else ''',"bootstrap": "^5.2.0"''' if "Bootstrap" in styling else '') + '''
  }},
  "scripts": {{
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  }}
}}'''
    
    def _get_requirements_txt_template(self) -> str:
        return '''# {project_name} - Python Dependencies
# Generated by CodeAgent

fastapi>=0.68.0
uvicorn>=0.15.0
sqlalchemy>=1.4.0
psycopg2-binary>=2.9.0
alembic>=1.7.0
python-dotenv>=0.19.0
pydantic>=1.8.0
python-multipart>=0.0.5
httpx>=0.24.0

# Development dependencies
pytest>=6.2.0
pytest-asyncio>=0.21.0
black>=21.0.0
isort>=5.0.0
flake8>=3.9.0

# Tech Stack: {tech_stack}
# Features: {features}
'''