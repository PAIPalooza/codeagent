"""
Canvas Code Generator Service

This service converts visual canvas layouts into React component code,
integrating with the AINative code generation APIs for intelligent code creation.
"""

import logging
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))
from tools.code_gen_create_tool import CodeGenCreateTool
from tools.memory_store_tool import MemoryStoreTool

logger = logging.getLogger(__name__)


class CanvasCodeGenerator:
    """Service for generating React code from visual canvas layouts."""
    
    def __init__(self):
        self.code_gen_tool = CodeGenCreateTool()
        self.memory_tool = MemoryStoreTool()
        
    async def generate_code_from_layout(self, layout: Dict[str, Any], project_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate React component code from canvas layout.
        
        Args:
            layout: Canvas layout with components and their properties
            project_spec: Project specifications (name, description, tech stack, etc.)
            
        Returns:
            Dictionary containing generated code files and metadata
        """
        try:
            logger.info("Generating code from canvas layout")
            
            # Analyze layout to determine structure
            components = layout.get('components', [])
            analysis = self._analyze_layout(components)
            
            # Generate component code using AINative
            generated_files = {}
            
            # Generate main App component
            app_component = await self._generate_app_component(components, project_spec, analysis)
            generated_files['src/App.js'] = app_component
            
            # Generate individual custom components if needed
            custom_components = await self._generate_custom_components(components, project_spec)
            generated_files.update(custom_components)
            
            # Generate CSS styles
            css_styles = await self._generate_styles(components, project_spec, analysis)
            generated_files['src/App.css'] = css_styles
            
            # Generate package.json
            package_json = self._generate_package_json(project_spec)
            generated_files['package.json'] = package_json
            
            # Store layout in memory for future reference
            await self.memory_tool._call(
                content=f"Canvas layout for {project_spec.get('name', 'project')}: {len(components)} components",
                title=f"Canvas Layout: {project_spec.get('name', 'Unnamed Project')}",
                tags=["canvas_layout", "visual_builder", "react"]
            )
            
            return {
                "success": True,
                "files": generated_files,
                "analysis": analysis,
                "components_count": len(components),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating code from layout: {str(e)}")
            return {"error": True, "message": str(e)}
    
    def _analyze_layout(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the canvas layout to understand structure and patterns."""
        analysis = {
            "total_components": len(components),
            "component_types": {},
            "has_navigation": False,
            "has_forms": False,
            "has_data_display": False,
            "layout_complexity": "simple"
        }
        
        # Count component types
        for component in components:
            comp_type = component.get('type', 'unknown')
            analysis["component_types"][comp_type] = analysis["component_types"].get(comp_type, 0) + 1
            
            # Check for specific patterns
            if comp_type in ['navbar', 'sidebar']:
                analysis["has_navigation"] = True
            elif comp_type in ['form', 'input']:
                analysis["has_forms"] = True
            elif comp_type in ['list', 'card', 'image']:
                analysis["has_data_display"] = True
        
        # Determine complexity
        if len(components) > 10:
            analysis["layout_complexity"] = "complex"
        elif len(components) > 5:
            analysis["layout_complexity"] = "moderate"
            
        return analysis
    
    async def _generate_app_component(self, components: List[Dict[str, Any]], 
                                    project_spec: Dict[str, Any], 
                                    analysis: Dict[str, Any]) -> str:
        """Generate the main App.js component."""
        
        # Create a prompt for the AINative code generation
        prompt = f"""
Generate a React App.js component based on the following visual layout:

Project: {project_spec.get('name', 'React App')}
Description: {project_spec.get('description', 'Generated from visual builder')}
Styling: {project_spec.get('styling', 'CSS')}

Components to include ({len(components)} total):
{self._components_to_prompt(components)}

Analysis:
- Has navigation: {analysis['has_navigation']}
- Has forms: {analysis['has_forms']}
- Has data display: {analysis['has_data_display']}
- Complexity: {analysis['layout_complexity']}

Requirements:
1. Create a single App.js component that renders all the components
2. Use functional components with React hooks
3. Include proper state management for forms and interactive elements
4. Add responsive design considerations
5. Include proper accessibility attributes
6. Use semantic HTML elements
7. Make it production-ready with error handling

Generate clean, well-commented React code.
"""
        
        try:
            # Use AINative to generate the code
            response = await self.code_gen_tool._call(
                project_name=project_spec.get('name', 'React App'),
                description=f"Generated from visual builder: {project_spec.get('description', '')}",
                features=[f"component_{comp.get('type', 'unknown')}" for comp in components],
                tech_stack=project_spec.get('tech_stack', 'React'),
                styling=project_spec.get('styling', 'CSS'),
                canvas_layout=components
            )
            
            if response.get("success"):
                return response.get("data", {}).get("code", self._fallback_app_component(components))
            else:
                logger.warning("AINative code generation failed, using fallback")
                return self._fallback_app_component(components)
                
        except Exception as e:
            logger.error(f"Error with AINative code generation: {str(e)}")
            return self._fallback_app_component(components)
    
    def _components_to_prompt(self, components: List[Dict[str, Any]]) -> str:
        """Convert components list to a text prompt."""
        prompt_parts = []
        for i, component in enumerate(components, 1):
            comp_type = component.get('type', 'unknown')
            props = {k: v for k, v in component.items() if k not in ['id', 'type']}
            prompt_parts.append(f"{i}. {comp_type.upper()}: {props}")
        return "\n".join(prompt_parts)
    
    def _fallback_app_component(self, components: List[Dict[str, Any]]) -> str:
        """Generate a fallback App component if AINative fails."""
        component_jsx = []
        imports = ["import React, { useState } from 'react';", "import './App.css';"]
        
        for component in components:
            jsx = self._component_to_jsx(component)
            if jsx:
                component_jsx.append(f"        {jsx}")
        
        return f"""{chr(10).join(imports)}

function App() {{
  const [formData, setFormData] = useState({{}});

  const handleInputChange = (name, value) => {{
    setFormData(prev => ({{ ...prev, [name]: value }}));
  }};

  const handleSubmit = (e) => {{
    e.preventDefault();
    console.log('Form submitted:', formData);
    alert('Form submitted! Check console for data.');
  }};

  return (
    <div className="App">
{chr(10).join(component_jsx)}
    </div>
  );
}}

export default App;"""
    
    def _component_to_jsx(self, component: Dict[str, Any]) -> str:
        """Convert a component object to JSX string."""
        comp_type = component.get('type', '')
        
        if comp_type == 'button':
            text = component.get('text', 'Button')
            return f'<button className="canvas-button" onClick={{() => alert("Button clicked!")}}>{text}</button>'
        
        elif comp_type == 'input':
            placeholder = component.get('placeholder', 'Enter text...')
            input_type = component.get('inputType', 'text')
            name = f"input_{component.get('id', 'field')}"
            return f'<input type="{input_type}" placeholder="{placeholder}" className="canvas-input" onChange={{(e) => handleInputChange("{name}", e.target.value)}} />'
        
        elif comp_type == 'text':
            text = component.get('text', 'Sample Text')
            return f'<div className="canvas-text">{text}</div>'
        
        elif comp_type == 'image':
            src = component.get('src', 'https://via.placeholder.com/150x100')
            alt = component.get('alt', 'Image')
            return f'<img src="{src}" alt="{alt}" className="canvas-image" />'
        
        elif comp_type == 'card':
            title = component.get('title', 'Card Title')
            content = component.get('content', 'Card content')
            return f'''<div className="canvas-card">
          <h3>{title}</h3>
          <p>{content}</p>
        </div>'''
        
        elif comp_type == 'list':
            items = component.get('items', ['Item 1', 'Item 2', 'Item 3'])
            list_items = [f'<li key="{i}">{item}</li>' for i, item in enumerate(items)]
            return f'''<ul className="canvas-list">
          {chr(10).join([f"          {item}" for item in list_items])}
        </ul>'''
        
        elif comp_type == 'form':
            return '''<form className="canvas-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Name:</label>
            <input type="text" placeholder="Enter name" onChange={(e) => handleInputChange("name", e.target.value)} />
          </div>
          <div className="form-group">
            <label>Email:</label>
            <input type="email" placeholder="Enter email" onChange={(e) => handleInputChange("email", e.target.value)} />
          </div>
          <button type="submit">Submit</button>
        </form>'''
        
        elif comp_type == 'navbar':
            brand = component.get('brand', 'Brand')
            return f'''<nav className="canvas-navbar">
          <div className="nav-brand">{brand}</div>
          <div className="nav-links">
            <a href="#home">Home</a>
            <a href="#about">About</a>
            <a href="#contact">Contact</a>
          </div>
        </nav>'''
        
        elif comp_type == 'footer':
            text = component.get('text', '© 2024 Your App. All rights reserved.')
            return f'<footer className="canvas-footer"><p>{text}</p></footer>'
        
        elif comp_type == 'sidebar':
            return '''<aside className="canvas-sidebar">
          <ul>
            <li><a href="#dashboard">Dashboard</a></li>
            <li><a href="#profile">Profile</a></li>
            <li><a href="#settings">Settings</a></li>
          </ul>
        </aside>'''
        
        return f'<!-- Unknown component type: {comp_type} -->'
    
    async def _generate_custom_components(self, components: List[Dict[str, Any]], 
                                        project_spec: Dict[str, Any]) -> Dict[str, str]:
        """Generate custom component files for complex components."""
        # For now, we'll keep everything in App.js
        # In the future, we could extract complex components into separate files
        return {}
    
    async def _generate_styles(self, components: List[Dict[str, Any]], 
                             project_spec: Dict[str, Any], 
                             analysis: Dict[str, Any]) -> str:
        """Generate CSS styles for the components."""
        
        styling_framework = project_spec.get('styling', 'CSS')
        
        if styling_framework == 'Tailwind CSS':
            return self._generate_tailwind_styles()
        elif styling_framework == 'Bootstrap':
            return self._generate_bootstrap_styles()
        else:
            return self._generate_custom_css(analysis)
    
    def _generate_tailwind_styles(self) -> str:
        """Generate Tailwind CSS styles."""
        return """/* Tailwind CSS imports */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom component styles using Tailwind classes */
.App {
  @apply min-h-screen bg-gray-50 p-4;
}

.canvas-button {
  @apply px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors;
}

.canvas-input {
  @apply w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500;
}

.canvas-text {
  @apply text-gray-800 mb-2;
}

.canvas-image {
  @apply max-w-full h-auto rounded;
}

.canvas-card {
  @apply bg-white rounded-lg shadow-md p-6 mb-4;
}

.canvas-list {
  @apply bg-white rounded border divide-y;
}

.canvas-list li {
  @apply px-4 py-2;
}

.canvas-form {
  @apply bg-white rounded-lg shadow-md p-6 space-y-4;
}

.form-group {
  @apply space-y-1;
}

.form-group label {
  @apply block text-sm font-medium text-gray-700;
}

.canvas-navbar {
  @apply bg-gray-800 text-white px-6 py-4 flex justify-between items-center rounded;
}

.nav-brand {
  @apply text-xl font-bold;
}

.nav-links {
  @apply flex space-x-4;
}

.nav-links a {
  @apply text-gray-300 hover:text-white transition-colors;
}

.canvas-footer {
  @apply bg-gray-800 text-white text-center py-4 rounded;
}

.canvas-sidebar {
  @apply bg-gray-100 rounded p-4;
}

.canvas-sidebar ul {
  @apply space-y-2;
}

.canvas-sidebar a {
  @apply block px-3 py-2 text-gray-700 hover:bg-gray-200 rounded;
}"""
    
    def _generate_bootstrap_styles(self) -> str:
        """Generate Bootstrap CSS styles."""
        return """/* Bootstrap imports */
@import 'bootstrap/dist/css/bootstrap.min.css';

/* Custom styles for canvas components */
.App {
  min-height: 100vh;
  background-color: #f8f9fa;
  padding: 1rem;
}

.canvas-button {
  /* Bootstrap classes applied via className */
}

.canvas-input {
  /* Bootstrap classes applied via className */
}

.canvas-card {
  margin-bottom: 1rem;
}

.canvas-navbar {
  margin-bottom: 1rem;
}

.canvas-footer {
  margin-top: 2rem;
}

.canvas-sidebar {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
  padding: 1rem;
}

.canvas-sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.canvas-sidebar li {
  margin-bottom: 0.5rem;
}

.canvas-sidebar a {
  display: block;
  color: #333;
  text-decoration: none;
  padding: 0.5rem;
  border-radius: 0.25rem;
  transition: background-color 0.2s;
}

.canvas-sidebar a:hover {
  background-color: #e9ecef;
}"""
    
    def _generate_custom_css(self, analysis: Dict[str, Any]) -> str:
        """Generate custom CSS styles."""
        return """.App {
  text-align: center;
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20px;
}

.canvas-button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin: 5px;
  transition: background-color 0.2s;
}

.canvas-button:hover {
  background-color: #0056b3;
}

.canvas-input {
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  margin: 5px;
  min-width: 200px;
}

.canvas-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.canvas-text {
  margin: 10px;
  color: #333;
}

.canvas-image {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  margin: 10px;
}

.canvas-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 20px;
  margin: 15px;
  text-align: left;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.canvas-card h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.canvas-card p {
  margin: 0;
  color: #666;
  line-height: 1.5;
}

.canvas-list {
  background: white;
  border-radius: 4px;
  border: 1px solid #dee2e6;
  margin: 15px auto;
  max-width: 400px;
  text-align: left;
  list-style: none;
  padding: 0;
}

.canvas-list li {
  padding: 12px 16px;
  border-bottom: 1px solid #dee2e6;
}

.canvas-list li:last-child {
  border-bottom: none;
}

.canvas-form {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 20px;
  margin: 15px auto;
  max-width: 400px;
  text-align: left;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
}

.canvas-navbar {
  background: #343a40;
  color: white;
  padding: 15px 30px;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.nav-brand {
  font-weight: bold;
  font-size: 1.2rem;
}

.nav-links {
  display: flex;
  gap: 20px;
}

.nav-links a {
  color: white;
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.nav-links a:hover {
  background-color: rgba(255,255,255,0.1);
}

.canvas-footer {
  background: #343a40;
  color: white;
  text-align: center;
  padding: 20px;
  border-radius: 4px;
  margin-top: 40px;
}

.canvas-footer p {
  margin: 0;
}

.canvas-sidebar {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 20px;
  max-width: 250px;
  margin: 15px auto;
  text-align: left;
}

.canvas-sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.canvas-sidebar li {
  margin-bottom: 8px;
}

.canvas-sidebar a {
  display: block;
  color: #333;
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.canvas-sidebar a:hover {
  background-color: #e9ecef;
}"""
    
    def _generate_package_json(self, project_spec: Dict[str, Any]) -> str:
        """Generate package.json for the project."""
        project_name = project_spec.get('name', 'canvas-project').lower().replace(' ', '-')
        styling = project_spec.get('styling', 'CSS')
        
        dependencies = {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "react-scripts": "5.0.1"
        }
        
        if styling == 'Tailwind CSS':
            dependencies.update({
                "tailwindcss": "^3.3.0",
                "autoprefixer": "^10.4.14",
                "postcss": "^8.4.24"
            })
        elif styling == 'Bootstrap':
            dependencies["bootstrap"] = "^5.3.0"
        
        package_json = {
            "name": project_name,
            "version": "0.1.0",
            "private": True,
            "dependencies": dependencies,
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "eslintConfig": {
                "extends": [
                    "react-app",
                    "react-app/jest"
                ]
            },
            "browserslist": {
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
            }
        }
        
        import json
        return json.dumps(package_json, indent=2)