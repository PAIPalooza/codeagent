"""
Ollama integration service for generating app plans.
"""

import json
import logging
import os
from typing import Dict, List, Any
from datetime import datetime

import requests
from requests.exceptions import RequestException, ConnectionError, Timeout

logger = logging.getLogger(__name__)


class OllamaService:
    """Service for interacting with Ollama LLM for app generation planning."""
    
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "vicuna-13b")
        self.temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.2"))
        self.max_tokens = int(os.getenv("OLLAMA_MAX_TOKENS", "1024"))
        
    def _load_planning_prompt(self) -> str:
        """Load the planning prompt template from file."""
        prompt_path = os.path.join(os.path.dirname(__file__), "../../prompts/app_generation_plan.txt")
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Planning prompt template not found at {prompt_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading planning prompt template: {str(e)}")
            raise
    
    def _format_planning_prompt(self, project_name: str, description: str, 
                              features: List[str], tech_stack: str, styling: str) -> str:
        """Format the planning prompt with the provided parameters."""
        template = self._load_planning_prompt()
        
        timestamp = datetime.utcnow().isoformat()
        features_str = ', '.join(features)
        
        return template.format(
            project_name=project_name,
            description=description,
            features=features_str,
            tech_stack=tech_stack,
            styling=styling,
            timestamp=timestamp
        )
    
    def _call_ollama(self, prompt: str) -> str:
        """Make a request to Ollama API."""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            }
            
            logger.info(f"Calling Ollama at {self.base_url}/api/generate")
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama API returned status {response.status_code}: {response.text}")
                raise Exception(f"Ollama API error: {response.status_code}")
            
            result = response.json()
            return result.get("response", "")
            
        except ConnectionError:
            logger.error("Could not connect to Ollama. Is it running?")
            raise Exception("Ollama service is not available. Please ensure Ollama is running.")
        except Timeout:
            logger.error("Ollama request timed out")
            raise Exception("Ollama request timed out. Please try again.")
        except RequestException as e:
            logger.error(f"Ollama request failed: {str(e)}")
            raise Exception(f"Ollama request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error calling Ollama: {str(e)}")
            raise
    
    def generate_app_plan(self, project_name: str, description: str, 
                         features: List[str], tech_stack: str, styling: str) -> List[Dict[str, Any]]:
        """
        Generate an application plan using Ollama.
        
        Args:
            project_name: Name of the project
            description: Project description
            features: List of features to implement
            tech_stack: Technology stack to use
            styling: Styling framework
            
        Returns:
            List of generation steps
            
        Raises:
            Exception: If plan generation fails or returns invalid JSON
        """
        try:
            # Format the prompt
            prompt = self._format_planning_prompt(
                project_name, description, features, tech_stack, styling
            )
            
            logger.info(f"Generating plan for project '{project_name}' with tech stack '{tech_stack}'")
            
            # Call Ollama
            response = self._call_ollama(prompt)
            
            # Clean up the response (remove any markdown formatting)
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            # Parse JSON
            try:
                plan = json.loads(response)
                
                # Validate the plan structure
                if not isinstance(plan, list):
                    raise ValueError("Plan must be a list of steps")
                
                for i, step in enumerate(plan):
                    if not isinstance(step, dict):
                        raise ValueError(f"Step {i} must be a dictionary")
                    if "tool" not in step:
                        raise ValueError(f"Step {i} missing 'tool' field")
                    if "input" not in step:
                        raise ValueError(f"Step {i} missing 'input' field")
                
                logger.info(f"Successfully generated plan with {len(plan)} steps")
                return plan
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in Ollama response: {str(e)}")
                logger.error(f"Raw response: {response}")
                raise Exception(f"Ollama returned invalid JSON: {str(e)}")
            except ValueError as e:
                logger.error(f"Invalid plan structure: {str(e)}")
                raise Exception(f"Invalid plan structure: {str(e)}")
                
        except Exception as e:
            logger.error(f"Failed to generate app plan: {str(e)}")
            # Return a fallback plan if Ollama fails
            return self._get_fallback_plan(project_name, description, features, tech_stack, styling)
    
    def _get_fallback_plan(self, project_name: str, description: str, 
                          features: List[str], tech_stack: str, styling: str) -> List[Dict[str, Any]]:
        """
        Return a basic fallback plan when Ollama is not available.
        
        This ensures the system can still function without Ollama.
        """
        logger.warning("Using fallback plan due to Ollama unavailability")
        
        # Determine templates based on tech stack
        if "Vue" in tech_stack and "Node" in tech_stack:
            # Vue + Node.js + MongoDB
            return [
                {
                    "tool": "codegen_create",
                    "input": {
                        "template": "mongoose-model",
                        "file_path": "backend/models/User.js",
                        "variables": {
                            "project_name": project_name,
                            "description": description,
                            "features": features,
                            "tech_stack": tech_stack,
                            "styling": styling
                        }
                    }
                },
                {
                    "tool": "codegen_create",
                    "input": {
                        "template": "express-route",
                        "file_path": "backend/routes/api.js",
                        "variables": {
                            "project_name": project_name,
                            "description": description,
                            "features": features,
                            "tech_stack": tech_stack,
                            "styling": styling
                        }
                    }
                },
                {
                    "tool": "codegen_create",
                    "input": {
                        "template": "vue-component",
                        "file_path": "frontend/src/App.vue",
                        "variables": {
                            "project_name": project_name,
                            "description": description,
                            "features": features,
                            "tech_stack": tech_stack,
                            "styling": styling
                        }
                    }
                }
            ]
        elif "Next.js" in tech_stack and "Django" in tech_stack:
            # Next.js + Django + MySQL
            return [
                {
                    "tool": "codegen_create",
                    "input": {
                        "template": "django-model",
                        "file_path": "backend/app/models.py",
                        "variables": {
                            "project_name": project_name,
                            "description": description,
                            "features": features,
                            "tech_stack": tech_stack,
                            "styling": styling
                        }
                    }
                },
                {
                    "tool": "codegen_create",
                    "input": {
                        "template": "django-rest-route",
                        "file_path": "backend/app/urls.py",
                        "variables": {
                            "project_name": project_name,
                            "description": description,
                            "features": features,
                            "tech_stack": tech_stack,
                            "styling": styling
                        }
                    }
                },
                {
                    "tool": "codegen_create",
                    "input": {
                        "template": "next-page",
                        "file_path": "frontend/pages/index.jsx",
                        "variables": {
                            "project_name": project_name,
                            "description": description,
                            "features": features,
                            "tech_stack": tech_stack,
                            "styling": styling
                        }
                    }
                }
            ]
        else:
            # Default: React + FastAPI + PostgreSQL
            return [
                {
                    "tool": "codegen_create",
                    "input": {
                        "template": "sqlalchemy-model",
                        "file_path": "backend/app/models.py",
                        "variables": {
                            "project_name": project_name,
                            "description": description,
                            "features": features,
                            "tech_stack": tech_stack,
                            "styling": styling
                        }
                    }
                },
                {
                    "tool": "codegen_create",
                    "input": {
                        "template": "fastapi-route",
                        "file_path": "backend/app/routers/api.py",
                        "variables": {
                            "project_name": project_name,
                            "description": description,
                            "features": features,
                            "tech_stack": tech_stack,
                            "styling": styling
                        }
                    }
                },
                {
                    "tool": "codegen_create",
                    "input": {
                        "template": "react-component",
                        "file_path": "frontend/src/App.jsx",
                        "variables": {
                            "project_name": project_name,
                            "description": description,
                            "features": features,
                            "tech_stack": tech_stack,
                            "styling": styling
                        }
                    }
                }
            ]
    
    def health_check(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False