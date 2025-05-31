**Product Requirements Document (PRD)**
**Proof of Concept: Browser-Based App Generator (Lovable-/Bolt.New-Style) Using AINative Studio, LangChain & Ollama**

---

## 1. Executive Summary

This PRD defines the requirements for a proof-of-concept (POC) “Browser-Based App Generator” that leverages three core technologies:

1. **AINative Studio’s Agent APIs**
   – Acts as the “backend brain,” offering code-generation, memory, semantic search, and orchestration endpoints.
2. **LangChain**
   – Serves as the orchestration layer (“agent framework”) that unifies Ollama’s LLM reasoning with AINative’s tools.
3. **Ollama**
   – Functions as the local LLM (“reasoning engine”) responsible for interpreting user prompts, planning code generation, and summarizing outputs.

The objective is to deliver a simple browser UI where a non-technical user can specify high-level app requirements—such as “A to-do list app with user authentication, a PostgreSQL backend, and a responsive React frontend”—and have the system automatically generate a minimal working code scaffold (HTML/CSS/JS or React + basic backend). The POC will demonstrate end-to-end integration:

1. **User Input (Browser)** →
2. **LangChain “Generator Agent” (Node/Python backend)** uses **Ollama** to plan and calls **AINative** tools (code generation, file operations, memory store/search) →
3. **Return Generated Code** as a downloadable ZIP or GitHub repo link →
4. **Optional Memory Recall** (e.g., “Show me my last generated app”).

By following this architecture, the POC will validate that a lightweight, browser-driven app builder—akin to Lovable or Bolt.New—can be built using AINative’s code-generation and memory capabilities, orchestrated by LangChain, with Ollama steering the reasoning.

---

## 2. Objectives & Success Criteria

### 2.1 Primary Objectives

1. **Browser-Based UI for App Specification**

   * Provide a simple web form where users input:

     * App Name and Description
     * Core Features (e.g., “User signup/login,” “Task CRUD,” “Dashboard view”)
     * Preferred Tech Stack (e.g., “React + FastAPI + PostgreSQL,” “Vue + Node.js + MongoDB”)
     * Styling Framework (e.g., TailwindCSS, Bootstrap)
   * Display a “Generate App” button that triggers the backend orchestration.

2. **LangChain “Generator Agent”**

   * Accept the user’s high-level requirements as a single prompt.
   * Use **Ollama** to:

     1. Break down requirements into discrete code-generation tasks (e.g., “Create React component for login,” “Define PostgreSQL schema for users,” “Write FastAPI route for CRUD operations on tasks”).
     2. Sequence the tasks into an ordered “plan” (JSON).
   * For each planned task, call AINative’s code-generation endpoints (e.g., `/api/v1/code-generation/create`, `/api/v1/code-generation/refactor`) to receive scaffold files.
   * Collate the generated files into a coherent folder structure, zip them, and return a download link.

3. **AINative Code-Generation & Memory**

   * Wrap these AINative endpoints as LangChain “tools”:

     1. `CodeGenCreateTool` → `POST /api/v1/code-generation/create`
     2. `CodeGenRefactorTool` → `POST /api/v1/code-generation/refactor`
     3. `MemoryStoreTool` → `POST /api/v1/agent/memory` (store user requirements and final project meta)
     4. `MemorySearchTool` → `POST /api/v1/agent/memory/search` (recall past app specs)
   * Ensure each code snippet returned from AINative is syntactically valid and placed into the correct directory (e.g., `src/components/Login.jsx`, `backend/routes/tasks.py`, `database/models.py`).

4. **Ollama Reasoning Engine**

   * Use a local LLM (e.g., `vicuna-13b` or `llama-2-13b`) for:

     * **Planning**: Given a single “app specification” prompt, output a structured JSON “plan” enumerating each code-generation subtask with inputs.
     * **Summarization**: After each AINative call, optionally summarize the generated code (for logging or user feedback).
   * Configure Ollama with low temperature (0.2) to encourage deterministic output.

5. **Basic Memory Recall**

   * On initial “Generate App” request, store the user’s spec (project name, feature list, tech stack) in AINative’s memory.
   * Provide a “Recall Last App” feature in the browser that queries memory for the most recent “app spec” and pre-fills the form (or displays the past generation result).

### 2.2 Success Criteria

* **Working Browser Demo**

  * A user can navigate to a minimal web page, fill out an “App Spec” form, click “Generate App,” and within 60–90 seconds receive a ZIP or GitHub link containing:

    1. A basic frontend scaffold (React or Vue files)
    2. A minimal backend scaffold (FastAPI or Node.js Express)
    3. Database schema files (e.g., SQLAlchemy models or Mongoose schemas)
    4. Basic styling wrappers (TailwindCSS or Bootstrap classes)
  * The generated project is structurally correct (e.g., `frontend/`, `backend/`, `README.md`, `package.json`, `requirements.txt`).

* **Tool Invocation Verified**

  * Demonstrate at least **three** AINative code-generation endpoints in action:

    1. `POST /api/v1/code-generation/create` for initial file scaffolding
    2. `POST /api/v1/code-generation/refactor` to adjust or enhance scaffolded code (e.g., adding form validation)
    3. `POST /api/v1/agent/memory` to store app spec and `POST /api/v1/agent/memory/search` to recall it

* **Ollama “Plan” Correctness**

  * The JSON plan generated by Ollama must:

    * Enumerate all major features (login, CRUD, dashboard).
    * Specify for each feature:

      * **Tool** (e.g., `codegen_create`, `codegen_refactor`)
      * **Input** (e.g., “Generate React component for user login form with TailwindCSS styling”)
    * Follow a logical order (e.g., schema first, backend routes next, then frontend forms).

* **Memory Recall Workflows**

  * If the user clicks “Recall Last App,” the browser fetches from a `/recall` endpoint which:

    1. Calls `POST /api/v1/agent/memory/search` with the query “last generated app spec”
    2. Returns the stored spec (feature list, tech stack)
  * The recall form is pre-populated with the previous spec, and user can click “Generate Again” to regenerate (iteration).

* **Documentation & Code Structure**

  * Provide a `README.md` or Notion page describing:

    1. How to install and run the POC (Ollama, Python dependencies, AINative API key).
    2. How the browser UI communicates with the backend (AJAX/WebSocket).
    3. How to extend the POC (adding new code-generation tools or tech stacks).

---

## 3. Scope

### 3.1 In-Scope (POC Minimum Viable Features)

1. **Browser UI**

   * **App Spec Form**

     * Inputs:

       * **Project Name** (text)
       * **Description** (multiline text)
       * **Feature Checklist** (multi-select dropdown or free-text)
       * **Tech Stack Selector** (dropdown: “React + FastAPI + PostgreSQL” or “Vue + Node.js + MongoDB”)
       * **Styling Framework** (dropdown: “TailwindCSS,” “Bootstrap,” “Plain CSS”)
     * Buttons:

       * **Generate App** (submits spec to backend)
       * **Recall Last App** (fetches from memory)
   * **Status & Feedback Area**

     * Shows agent’s logs (e.g., “Planning…,” “Generating React components…,” “Bundling files…,” “Complete!”).
     * Last step should show a **Download ZIP** link or a **GitHub Repo** link.

2. **Backend Orchestration (LangChain + Ollama)**

   * Accept a single HTTP POST (`/generate-app`) with JSON body:

     ```json
     {
       "project_name": "MyTodoApp",
       "description": "A to-do list with user auth, tasks, and a dashboard",
       "features": ["User login/signup", "Task CRUD", "Dashboard view"],
       "tech_stack": "React + FastAPI + PostgreSQL",
       "styling": "TailwindCSS"
     }
     ```
   * **LangChain Agent**:

     1. Invoke **Ollama** with a “planning prompt” to output a JSON array of discrete code-generation tasks.
     2. For each task in the plan, call the corresponding AINative “tool” to generate code snippets or files.
     3. Assemble all returned files into a directory structure:

        ```
        MyTodoApp/
        ├── frontend/
        │   ├── package.json
        │   ├── src/
        │   │   ├── App.jsx
        │   │   ├── components/
        │   │   │   ├── Login.jsx
        │   │   │   ├── TaskList.jsx
        │   │   │   └── Dashboard.jsx
        │   └── tailwind.config.js
        ├── backend/
        │   ├── requirements.txt
        │   ├── app/
        │   │   ├── main.py
        │   │   ├── routes/
        │   │   │   ├── auth.py
        │   │   │   ├── tasks.py
        │   │   │   └── dashboard.py
        │   │   └── models.py
        │   └── alembic.ini
        └── README.md
        ```
     4. Create a `README.md` that includes:

        * Project name and description
        * Tech stack details
        * Quickstart instructions (`cd frontend && npm install && npm start`, `cd backend && pip install -r requirements.txt && uvicorn main:app --reload`)
     5. Zip the entire folder (`MyTodoApp.zip`) or push it to a temporary GitHub repo (using a bare-bones GitHub API integration if desired).

3. **AINative “Tool” Wrappers**

   * **CodeGenCreateTool**

     * Wraps `POST /api/v1/code-generation/create`
     * Input JSON example:

       ```json
       {
         "template": "react-component",
         "file_path": "frontend/src/components/Login.jsx",
         "variables": {
           "component_name": "Login",
           "styling": "TailwindCSS"
         }
       }
       ```
     * Output:

       ```json
       {
         "file_path": "frontend/src/components/Login.jsx",
         "code": "import React from 'react';\nexport default function Login() { ... }"
       }
       ```
   * **CodeGenRefactorTool**

     * Wraps `POST /api/v1/code-generation/refactor`
     * Input example:

       ```json
       {
         "file_path": "frontend/src/components/Login.jsx",
         "existing_code": "<existing code string>",
         "instructions": "Add TailwindCSS classes to center the form."
       }
       ```
     * Output:

       ```json
       {
         "file_path": "frontend/src/components/Login.jsx",
         "code": "import React from 'react';\nexport default function Login() { return (<div className='flex items-center justify-center h-screen'> ...</div>); }"
       }
       ```
   * **MemoryStoreTool**

     * Wraps `POST /api/v1/agent/memory`
     * Stores the full user spec and final generation summary.
   * **MemorySearchTool**

     * Wraps `POST /api/v1/agent/memory/search`
     * Retrieves past specs for “Recall Last App” feature.

4. **Ollama Planning & Summarization**

   * Initialize Ollama via LangChain’s `Ollama` wrapper:

     ```python
     from langchain.llms import Ollama
     ollama = Ollama(base_url="http://localhost:11434", model="vicuna-13b", temperature=0.2, max_tokens=1024)
     ```
   * **Planning Prompt Template** (in `prompts/app_generation_plan.txt`):

     ```
     You are an AI planning agent. Given the following app specification:
       - Project Name: {project_name}
       - Description: {description}
       - Features: {features}  (comma-separated)
       - Tech Stack: {tech_stack}
       - Styling: {styling}

     Produce a JSON array of generation steps. Each step must be an object with:
       {
         "tool": "<tool_name>",
         "input": { ... }
       }
     Valid tools: codegen_create, codegen_refactor, memory_store.
     The sequence should logically begin with database schema generation, then backend routes, then frontend components, styling, and finally README. Do not output anything but valid JSON.

     Example output:
     [
       {
         "tool": "codegen_create",
         "input": {
           "template": "sqlalchemy-model",
           "file_path": "backend/app/models.py",
           "variables": { "model_name": "User", "fields": ["id:int:primary", "username:str:unique", "password:str"], "db": "PostgreSQL" }
         }
       },
       {
         "tool": "codegen_create",
         "input": {
           "template": "fastapi-route",
           "file_path": "backend/app/routes/auth.py",
           "variables": { "router_name": "auth_router", "path": "/auth", "methods": ["POST /signup", "POST /login"] }
         }
       },
       ...
       {
         "tool": "memory_store",
         "input": {
           "agent_id": "{agent_id}",
           "content": "Generated MyTodoApp: User model, auth routes, tasks CRUD, React components.",
           "metadata": { "project": "{project_name}", "timestamp": "{timestamp}" }
         }
       }
     ]
     ```

5. **Memory Recall Endpoint**

   * **HTTP GET `/recall-last-app`**

     1. Backend calls `POST /api/v1/agent/memory/search` with:

        ```json
        { "query": "latest app spec" }
        ```
     2. Retrieve top-scoring memory record:

        ```json
        {
          "memory_id": "m789",
          "content": "Spec: Project=MyTodoApp; Features=[User login, Task CRUD]; Tech Stack=React+FastAPI; Styling=TailwindCSS",
          "metadata": { "project": "MyTodoApp", "timestamp": "2025-05-31T10:00:00Z" }
        }
        ```
     3. Return that `content` to the browser to pre-fill the “App Spec Form.”

### 3.2 Out-of-Scope (Beyond POC)

1. **Advanced Multi-Agent Coordination**

   * No explicit use of AINative’s `/agent/coordination` endpoints or spawning specialized “CodeWriterAgent,” “StylingAgent,” or “ReviewerAgent.”
2. **Quantum-Enhanced Code Generation**

   * No calls to `/api/v1/quantum/*` or QNN flows.
3. **Rich Web UI Components**

   * No drag-and-drop interface or complex IDE integration. A simple HTML/CSS/JS form is sufficient.
4. **Production-Grade Deployment & Authentication**

   * No user sign-in or RBAC. The POC runs on a local dev server with a single user.
5. **Full Testing & CI/CD Pipelines**

   * Basic unit tests for tool wrappers; no end-to-end integration tests on staging or production.

---

## 4. User Personas & Use Cases

### 4.1 Primary Persona: Non-Technical Maker / Startup Founder

* **Profile**:
  – Limited coding expertise; familiar with high-level concepts (e.g., “I need a to-do app”).
  – Wants to quickly prototype a web application to validate an idea.
* **Needs**:

  1. Fill out a simple form with app requirements.
  2. Receive a basic, working code scaffold without manual coding.
  3. Iterate by tweaking features (e.g., “Add user roles,” “Use MongoDB instead”).
* **Goals**:
  – Obtain a deployable codebase within minutes to show to stakeholders.
  – Experiment with different tech stacks or styling frameworks by selecting from dropdowns.

### 4.2 Secondary Persona: Developer / Technical Evangelist

* **Profile**:
  – Comfortable reading code; interested in evaluating behind-the-scenes AI orchestration.
* **Needs**:

  1. Understand how AINative’s code-generation strokes combine to produce a coherent project.
  2. Inspect the generated files, modify them locally, and redeploy.
  3. Learn how to extend the system (e.g., add a new tech stack or code template).
* **Goals**:
  – Validate feasibility for building a more advanced “app builder platform.”
  – Provide feedback on improving prompts, tool wrappers, and folder structure.

### 4.3 Use Case: “Generate a Notes App in 3 Minutes”

1. **Trigger** (Browser):
   – User navigates to `http://localhost:8000` and sees an “App Generator” form.
   – They fill in:

   * **Project Name:** `QuickNotes`
   * **Description:** `A simple notes app with user auth and note CRUD.`
   * **Features:** `User login/signup`, `Create/Edit/Delete notes`, `List notes by user`
   * **Tech Stack:** `React + FastAPI + PostgreSQL`
   * **Styling:** `Bootstrap`
     – User clicks **Generate App**.

2. **Backend Workflow** (`/generate-app`):

   1. **Store User Spec** via `MemoryStoreTool` to AINative.
   2. **Ollama Planning**: Send planning prompt with `project_name=QuickNotes`, `features=[…]`, etc.
   3. **Ollama Outputs Plan** (JSON), for example:

      ```json
      [
        {
          "tool": "codegen_create",
          "input": {
            "template": "sqlalchemy-model",
            "file_path": "backend/app/models.py",
            "variables": { "model_name": "User", "fields": ["id:int:primary", "email:str:unique", "password:str"], "db": "PostgreSQL" }
          }
        },
        {
          "tool": "codegen_create",
          "input": {
            "template": "sqlalchemy-model",
            "file_path": "backend/app/models.py",
            "variables": { "model_name": "Note", "fields": ["id:int:primary", "user_id:int:foreign:User.id", "content:str", "created_at:datetime"], "db": "PostgreSQL" }
          }
        },
        {
          "tool": "codegen_create",
          "input": {
            "template": "fastapi-route",
            "file_path": "backend/app/routes/auth.py",
            "variables": { "router_name": "auth_router", "path": "/auth", "methods": ["POST /signup", "POST /login"] }
          }
        },
        {
          "tool": "codegen_create",
          "input": {
            "template": "fastapi-route",
            "file_path": "backend/app/routes/notes.py",
            "variables": { "router_name": "notes_router", "path": "/notes", "methods": ["GET /", "POST /", "PUT /{note_id}", "DELETE /{note_id}"] }
          }
        },
        {
          "tool": "codegen_create",
          "input": {
            "template": "react-component",
            "file_path": "frontend/src/components/Login.jsx",
            "variables": { "component_name": "Login", "styling": "Bootstrap" }
          }
        },
        {
          "tool": "codegen_create",
          "input": {
            "template": "react-component",
            "file_path": "frontend/src/components/NotesList.jsx",
            "variables": { "component_name": "NotesList", "styling": "Bootstrap" }
          }
        },
        {
          "tool": "codegen_create",
          "input": {
            "template": "react-component",
            "file_path": "frontend/src/components/NoteEditor.jsx",
            "variables": { "component_name": "NoteEditor", "styling": "Bootstrap" }
          }
        },
        {
          "tool": "codegen_refactor",
          "input": {
            "file_path": "frontend/src/App.jsx",
            "existing_code": "// initial scaffold code",
            "instructions": "Wire up routing between Login, NotesList, and NoteEditor using React Router"
          }
        },
        {
          "tool": "codegen_create",
          "input": {
            "template": "tailwind-config", // if styling=TailwindCSS; in this case, skip 
            "file_path": "frontend/tailwind.config.js",
            "variables": {}
          }
        },
        {
          "tool": "memory_store",
          "input": {
            "agent_id": "agent-xyz",
            "content": "Generated QuickNotes: 2 SQLAlchemy models (User, Note), 2 FastAPI routes, 3 React components, React Router integration, Bootstrap styling.",
            "metadata": { "project": "QuickNotes", "timestamp": "2025-05-31T12:00:00Z" }
          }
        }
      ]
      ```
   4. **LangChain Executes Each Step**:

      * For each `codegen_create` or `codegen_refactor`, invoke AINative and save returned code to the appropriate file path.
      * For final `memory_store`, store summary.
   5. **Assemble Files & ZIP**:

      * Create a temporary folder `QuickNotes/` with subfolders `frontend/` and `backend/`, place files accordingly.
      * Generate `package.json`, `requirements.txt`, and `README.md` via additional Ollama calls or static templates.
      * Zip the folder as `QuickNotes.zip`.

3. **Browser UI Response**

   * The backend responds with:

     ```json
     {
       "download_url": "http://localhost:8000/downloads/QuickNotes.zip",
       "github_url": null
     }
     ```
   * Browser displays a “Download Your App” link.
   * If user clicks “Recall Last App,” browser calls `/recall-last-app`, gets the stored content stanza, and pre-fills the form fields.

---

## 5. Functional Requirements

### 5.1 Web UI Requirements

| **ID**                                                                             | **Requirement**   | **Details**   |
| ---------------------------------------------------------------------------------- | ----------------- | ------------- |
| UI-001                                                                             | **App Spec Form** | - **Fields:** |
| · Project Name (single line text)                                                  |                   |               |
| · Description (multiline text)                                                     |                   |               |
| · Features (multiselect or free-text list)                                         |                   |               |
| · Tech Stack (dropdown: “React + FastAPI + PostgreSQL,” “Vue + Node.js + MongoDB”) |                   |               |
| · Styling (dropdown: “TailwindCSS,” “Bootstrap,” “Plain CSS”)                      |                   |               |

* **Buttons:**
  · “Generate App” (triggers `/generate-app`)
  · “Recall Last App” (fetches from `/recall-last-app`) |
  \| UI-002   | **Status & Logs Panel**                                                                                                                                     | - Shows real-time status updates from the backend (e.g., “Planning…,” “Generating models…,” “Generating frontend…,” “Bundling files…,” “Complete!”).
* Use simple polling (AJAX) or WebSocket/SSE for streaming logs.                                                                                                               |
  \| UI-003   | **Download / GitHub Link**                                                                                                                                  | - After generation, display a button/link:
  · “Download ZIP” (links to `/downloads/<project>.zip`)
  · Optional: “View on GitHub” (links to a temp or user’s repo if integrated)                                                                                                                                            |
  \| UI-004   | **Recall Last App Pre-fill**                                                                                                                                 | - On clicking “Recall Last App,” make a GET `/recall-last-app` call.
* Backend returns a JSON with the stored spec (project\_name, description, features, tech\_stack, styling).
* Pre-fill the form fields accordingly.                                                                                                                                                                                                                                 |

### 5.2 Backend – Orchestration & APIs

#### 5.2.1 HTTP Endpoints

| **Endpoint**                                                                                                          | **Method**                               | **Input JSON** | **Output JSON / Behavior**                               |
| --------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- | -------------- | -------------------------------------------------------- |
| **`/generate-app`**                                                                                                   | POST                                     | \`{            |                                                          |
| "project\_name": string,                                                                                              |                                          |                |                                                          |
| "description": string,                                                                                                |                                          |                |                                                          |
| "features": \[string],                                                                                                |                                          |                |                                                          |
| "tech\_stack": string,                                                                                                |                                          |                |                                                          |
| "styling": string                                                                                                     |                                          |                |                                                          |
| }\`                                                                                                                   | – Initiates LangChain “Generator Agent.” |                |                                                          |
| – Stores user spec via MemoryStoreTool.                                                                               |                                          |                |                                                          |
| – Calls Ollama to produce a JSON “plan.”                                                                              |                                          |                |                                                          |
| – Iteratively executes each step in the plan (calling AINative code-generation tools, writing files to disk).         |                                          |                |                                                          |
| – Zips the complete project folder.                                                                                   |                                          |                |                                                          |
| – Returns `{ "status": "success", "download_url": string, "github_url": null }` or appropriate error JSON if failure. |                                          |                |                                                          |
| **`/recall-last-app`**                                                                                                | GET                                      | None           | – Calls `MemorySearchTool` with query “latest app spec.” |
| – Returns \`{                                                                                                         |                                          |                |                                                          |
| "project\_name": string,                                                                                              |                                          |                |                                                          |
| "description": string,                                                                                                |                                          |                |                                                          |
| "features": \[string],                                                                                                |                                          |                |                                                          |
| "tech\_stack": string,                                                                                                |                                          |                |                                                          |
| "styling": string                                                                                                     |                                          |                |                                                          |
| }`if found; else`{ "error": "No previous spec found." }\`                                                             |                                          |                |                                                          |
| **`/downloads/<name>.zip`**                                                                                           | GET                                      | None           | – Serves the `name.zip` file from a temporary directory. |

#### 5.2.2 LangChain Agent Flow

1. **Receive `/generate-app` Request**

   * Deserialize JSON into a Python `dict`.
   * Immediately call `MemoryStoreTool` to store the raw spec:

     ```python
     MemoryStoreTool().run(
         agent_id=agent_id,
         content=json.dumps({
           "project_name": project_name,
           "description": description,
           "features": features,
           "tech_stack": tech_stack,
           "styling": styling
         }),
         metadata={ "step": "spec_submitted", "timestamp": now_iso }
     )
     ```

2. **Construct Planning Prompt**

   * Load template from `prompts/app_generation_plan.txt`.
   * Format with user inputs and a generated `agent_id`.
   * Example after formatting:

     ```
     You are an AI planning agent. Given the following app specification:
       - Project Name: QuickNotes
       - Description: A simple notes app with user auth and note CRUD.
       - Features: User login/signup, Create/Edit/Delete notes, List notes by user
       - Tech Stack: React + FastAPI + PostgreSQL
       - Styling: Bootstrap

     Produce a JSON array of generation steps. Each step must be an object with:
       {
         "tool": "<tool_name>",
         "input": { ... }
       }
     Valid tools: codegen_create, codegen_refactor, memory_store.
     The sequence should logically begin with database schema generation, then backend routes, then frontend components, styling, and finally README. Do not output anything but valid JSON.
     …
     ```

3. **Call Ollama for Plan**

   ```python
   plan_text = ollama.generate(planning_prompt)
   try:
       plan_steps = json.loads(plan_text)
   except JSONDecodeError:
       # Handle malformed JSON (retry or abort)
   ```

4. **Execute Each Plan Step**
   For each step in `plan_steps` (a list of dicts):

   * Retrieve `tool_name = step["tool"]` and `inputs = step["input"]`.
   * Map `tool_name` to a LangChain tool instance:

     ```python
     tool_map = {
         "codegen_create": CodeGenCreateTool(base_url, api_key),
         "codegen_refactor": CodeGenRefactorTool(base_url, api_key),
         "memory_store": MemoryStoreTool(base_url, api_key)
     }
     tool = tool_map.get(tool_name)
     if not tool:
         # Log error & possibly abort
     observation = tool._call(**inputs)
     ```
   * **File Writing**: For any step that returns `{ "file_path": "...", "code": "..." }`, write `code` to a local disk path under a unique temporary folder (e.g., `/tmp/<agent_id>/<file_path>`).
   * **Logging**: After each tool call, append a log entry (“Generated file X”, “Refactored file Y”) to an in-memory array for streaming back to the browser.

5. **Project Assembly**

   * After all code snippets are written, create essential manifest files:

     * **`frontend/package.json` (for React/Vue)**
     * **`frontend/webpack.config.js` or `vite.config.js` (if needed)**
     * **`backend/requirements.txt`** or **`backend/package.json`**
     * A root `README.md` summarizing the project.
   * Optionally call another `codegen_create` step to scaffold these manifest files, using a static Ollama prompt or AINative code-generation template.

6. **Zip & Serve**

   * Run a local zip command (e.g., `zip -r QuickNotes.zip QuickNotes/`) to compress the entire folder.
   * Move `QuickNotes.zip` to a `/downloads/` directory where the web server can serve it.

7. **Final Memory Storage**

   * Call `MemoryStoreTool` one last time:

     ```python
     MemoryStoreTool()._call(
         agent_id=agent_id,
         content=f"Completed generation of {project_name} at {timestamp}. Files: {list_of_files}.",
         metadata={ "step": "generation_complete", "project": project_name }
     )
     ```

8. **Return Response**

   * Return JSON:

     ```json
     {
       "status": "success",
       "download_url": "http://localhost:8000/downloads/QuickNotes.zip",
       "github_url": null
     }
     ```
   * If any step fails (e.g., malformed JSON, AINative API error), return:

     ```json
     { "status": "error", "message": "Detailed error message here." }
     ```

### 5.3 Tool-Specific Requirements

| **Tool Name**                                                                                       | **Wrapped Endpoint**                    | **Input Schema**      | **Output Schema** |
| --------------------------------------------------------------------------------------------------- | --------------------------------------- | --------------------- | ----------------- |
| **CodeGenCreateTool**                                                                               | `POST /api/v1/code-generation/create`   | \`{                   |                   |
| "template": string,          # e.g., "react-component", "fastapi-route", "sqlalchemy-model"         |                                         |                       |                   |
| "file\_path": string,         # e.g., "frontend/src/components/Login.jsx"                           |                                         |                       |                   |
| "variables": { ... }         # Key-value pairs specific to template (e.g., component\_name, fields) |                                         |                       |                   |
| }\`                                                                                                 | \`{                                     |                       |                   |
| "file\_path": string,         # same as input                                                       |                                         |                       |                   |
| "code": string               # generated code                                                       |                                         |                       |                   |
| }\`                                                                                                 |                                         |                       |                   |
| **CodeGenRefactorTool**                                                                             | `POST /api/v1/code-generation/refactor` | \`{                   |                   |
| "file\_path": string,                                                                               |                                         |                       |                   |
| "existing\_code": string,                                                                           |                                         |                       |                   |
| "instructions": string                                                                              |                                         |                       |                   |
| }\`                                                                                                 | \`{                                     |                       |                   |
| "file\_path": string,                                                                               |                                         |                       |                   |
| "code": string                                                                                      |                                         |                       |                   |
| }\`                                                                                                 |                                         |                       |                   |
| **MemoryStoreTool**                                                                                 | `POST /api/v1/agent/memory`             | \`{                   |                   |
| "agent\_id": string,                                                                                |                                         |                       |                   |
| "content": string,                                                                                  |                                         |                       |                   |
| "metadata": { ... }                                                                                 |                                         |                       |                   |
| }\`                                                                                                 | `{ "memory_id": string }`               |                       |                   |
| **MemorySearchTool**                                                                                | `POST /api/v1/agent/memory/search`      | `{ "query": string }` | \`{               |
| "results": \[                                                                                       |                                         |                       |                   |

```
{  
  "memory_id": string,  
  "content": string,  
  "score": float,  
  "metadata": { ... }  
}  
```

]
}\` |

---

## 6. Non-Functional Requirements

| **Category**                                                                                       | **Requirement**                                                                                                                         |
| -------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **Performance**                                                                                    | – Total time from “Generate App” click to “Download ZIP ready” should be ≤ 90 seconds for a small (≤ 20 file) app.                      |
| – Ollama planning call must return a valid JSON plan within ≤ 10 seconds.                          |                                                                                                                                         |
| – Each AINative code-generation call should complete within ≤ 5–10 seconds.                        |                                                                                                                                         |
| **Reliability**                                                                                    | – Tool wrappers handle timeouts (≤ 15 seconds) and retry up to 2× on transient (5xx) errors.                                            |
| – If a step fails, abort the generation and return a clear error.                                  |                                                                                                                                         |
| – Periodic health checks (e.g., `GET /health` for Ollama and “ping” AINative) at startup.          |                                                                                                                                         |
| **Scalability**                                                                                    | – POC runs on a single server, but code should be structured so that adding more agent instances (e.g., via Docker) is straightforward. |
| – Limit memory retention to the last 5 specs to avoid unbounded growth.                            |                                                                                                                                         |
| **Maintainability**                                                                                | – Each tool wrapper and prompt template exists in its own file/directory.                                                               |
| – Shared logic (e.g., API key injection, base URL resolution) centralized in `tools/base_tool.py`. |                                                                                                                                         |
| – Clear docstrings and comments in Python code.                                                    |                                                                                                                                         |
| – README.md fully details setup, usage, and extension instructions.                                |                                                                                                                                         |
| **Security**                                                                                       | – AINative API key stored in environment variable (`AINATIVE_API_KEY`).                                                                 |
| – Do not log sensitive data (e.g., full user passwords if any).                                    |                                                                                                                                         |
| – Sanitize user inputs (e.g., reject invalid file paths).                                          |                                                                                                                                         |
| – Serve the `/downloads` directory statically over HTTP without directory listing.                 |                                                                                                                                         |
| **Usability**                                                                                      | – Browser UI is clean, with clear labels/instructions.                                                                                  |
| – Status panel updates in near real-time (streamed via AJAX or SSE).                               |                                                                                                                                         |
| – Errors displayed prominently (e.g., “Failed to generate code: …”).                               |                                                                                                                                         |
| – “Recall Last App” pre-populates fields with a single click.                                      |                                                                                                                                         |
| **Documentation**                                                                                  | – README.md contains:                                                                                                                   |

1. Prerequisites (Python 3.9+, Ollama, Node/npm for frontend if needed, AINative API key)
2. Installation steps (`pip install -r requirements.txt`)
3. How to run Ollama (`ollama serve vicuna-13b`)
4. How to start the backend server (`uvicorn main:app --reload`)
5. How to access the browser UI (`http://localhost:8000`)
6. How to add new “templates” or tech stacks (editing prompt templates).   |

---

## 7. System Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           Browser UI (React/Vue)                         │
│                                                                            │
│   • App Spec Form  ────────(AJAX POST /generate-app)─────▶  • Status Panel  │
│   • “Recall Last App” ────▶ (AJAX GET /recall-last-app)                   │
│   • Download Link Display  ◀───(Response from /generate-app)──             │
└──────────────────────────────────────────────────────────────────────────┘
            ↑                                                      ↑
            │                                                      │
 (1) AJAX POST /generate-app                                (2) AJAX GET /recall-last-app
            │                                                      │
┌──────────────────────────────────────────────────────────────────────────┐
│                 Backend Orchestration Service (Python/FastAPI)         │
│                                                                          │
│  • **POST /generate-app** → LangChain “Generator Agent” → Ollama         │
│    – Plan generation (Ollama)                                            │
│    – Tool invocations (AINative codegen & memory)                        │
│    – File assembly & zipping                                             │
│    – Memory store final summary                                           │
│                                                                          │
│  • **GET /recall-last-app** → MemorySearchTool (AINative) → return spec  │
│                                                                          │
│  • **Static Files** (/downloads/<project>.zip)                           │
└──────────────────────────────────────────────────────────────────────────┘
            ↑                                                     
            │                                                     
 (3) HTTP/REST calls to AINative Tools                             (4) HTTP/REST calls to AINative Memory
      – /api/v1/code-generation/create                                      – /api/v1/agent/memory
      – /api/v1/code-generation/refactor                                    – /api/v1/agent/memory/search
      – /api/v1/agent/memory                                                  
      – /api/v1/agent/memory/search                                         
┌──────────────────────────────────────────────────────────────────────────┐
│                    AINative Studio Backend APIs (Hosted)                 │
│                                                                          │
│  • Agent Memory (store, search)                                          │
│  • Code Generation (create, refactor)                                    │
│  • (Optional future: coordination, quantum, etc.)                        │
└──────────────────────────────────────────────────────────────────────────┘
            
┌──────────────────────────────────────────────────────────────────────────┐
│                                  Ollama LLM                              │
│  • Runs locally (e.g., `ollama serve vicuna-13b`)                          │
│  • Exposes HTTP endpoint (default `http://localhost:11434`)               │
│  • Serves as LangChain’s `llm` for planning and summarization              │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Technical Stack & Dependencies

| **Component**                                                 | **Version / Details**                                                                                             |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Backend Language/Framework**                                | Python 3.9+ + FastAPI (or Flask) – for HTTP endpoints (`/generate-app`, `/recall-last-app`, static file serving). |
| **Frontend Framework**                                        | React v18 (or Vue 3) – simple page with form, status panel, and download link.                                    |
| **LangChain**                                                 | `langchain>=0.0.300` – for agent orchestration, tool integration, and Ollama wrapper.                             |
| **Ollama**                                                    | Local server (e.g., `vicuna-13b` or `llama-2-13b`) – run via `ollama serve vicuna-13b`.                           |
| **Requests**                                                  | `requests>=2.28.0` – for AINative API calls in Python tool wrappers.                                              |
| **AINative API Key**                                          | Environment variable: `AINATIVE_API_KEY` (set to the user’s AINative Studio key).                                 |
| **Memory Store/Search**                                       | Use AINative’s `/api/v1/agent/memory` and `/api/v1/agent/memory/search`.                                          |
| **Code Generation**                                           | Use AINative’s `/api/v1/code-generation/create` and `/api/v1/code-generation/refactor`.                           |
| **File Management**                                           | Python’s `os`, `shutil`, and `zipfile` modules for writing and zipping project directories.                       |
| **Static File Serving**                                       | FastAPI’s `StaticFiles` or equivalent to serve `/downloads` folder.                                               |
| **Logging**                                                   | Python’s `logging` module (level `INFO`), with streaming logs forwarded to the browser via WebSocket or SSE.      |
| **Env Management**                                            | Use `python-dotenv` or direct environment variables for:                                                          |
| – `AINATIVE_API_KEY`                                          |                                                                                                                   |
| – `AINATIVE_BASE_URL` (default `https://api.ainative.studio`) |                                                                                                                   |
| – `OLLAMA_BASE_URL` (default `http://localhost:11434`)        |                                                                                                                   |
| **File Structure**                                            |                                                                                                                   |

```
app-generator-poc/
├── backend/
│   ├── main.py
│   ├── tools/
│   │   ├── base_tool.py
│   │   ├── codegen_create_tool.py
│   │   ├── codegen_refactor_tool.py
│   │   ├── memory_store_tool.py
│   │   └── memory_search_tool.py
│   ├── prompts/
│   │   └── app_generation_plan.txt
│   ├── utils/
│   │   └── file_writer.py
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── SpecForm.jsx
│   │   │   └── StatusPanel.jsx
│   └── package.json
└── README.md
```

\| **Build Tools**             | – Node.js v16+ / npm or yarn for frontend (`create-react-app` or `vite`).
– Python’s `pip` for backend.                                                                                                       |

---

## 9. Detailed Implementation Plan & Milestones

### 9.1 Phase 1 (Day 1): Environment Setup & Basic Tool Wrappers

1. **Install & Verify Ollama**

   * Ensure Ollama is installed on developer machine.
   * Run:

     ```bash
     ollama serve vicuna-13b
     ```
   * Confirm `http://localhost:11434/v1/models` returns desired model info.

2. **Initialize Python Backend Project**

   * Create `backend/` directory.
   * Initialize `pipenv` or `venv` and install:

     ```bash
     pip install fastapi uvicorn langchain requests python-dotenv
     ```
   * Create `backend/tools/base_tool.py` with shared HTTP helper (see Section 5.3).

3. **Implement AINative Tool Wrappers**

   * **`codegen_create_tool.py`**: Wraps `POST /api/v1/code-generation/create`.
   * **`codegen_refactor_tool.py`**: Wraps `POST /api/v1/code-generation/refactor`.
   * **`memory_store_tool.py`**: Wraps `POST /api/v1/agent/memory`.
   * **`memory_search_tool.py`**: Wraps `POST /api/v1/agent/memory/search`.
   * Test each tool by writing small scripts (e.g., call `codegen_create` with a simple “hello world” template) to confirm connectivity.

4. **Write Prompt Template**

   * In `backend/prompts/app_generation_plan.txt`, create the planning prompt (see Section 5.2.2).

5. **Basic File Writing Utility**

   * Create `backend/utils/file_writer.py` with functions to:

     * Create folders recursively (`os.makedirs(path, exist_ok=True)`).
     * Write code string to a file (UTF-8).
     * Copy static template files if needed (e.g., `README_template.md`).

6. **Initial README.md**

   * Document how to set `AINATIVE_API_KEY` and `OLLAMA_BASE_URL`.
   * Include a “Hello World” example that invokes a code-generation tool and writes a file to disk.

---

### 9.2 Phase 2 (Days 2–3): LangChain Agent & Ollama Integration

1. **Set Up FastAPI Server**

   * Create `backend/main.py`:

     ```python
     from fastapi import FastAPI, HTTPException
     from fastapi.responses import JSONResponse, FileResponse
     from fastapi.staticfiles import StaticFiles
     import os, uuid, shutil, zipfile, json, datetime

     from langchain.llms import Ollama
     from langchain.agents import initialize_agent, AgentType
     from tools.codegen_create_tool import CodeGenCreateTool
     from tools.codegen_refactor_tool import CodeGenRefactorTool
     from tools.memory_store_tool import MemoryStoreTool
     from tools.memory_search_tool import MemorySearchTool
     from utils.file_writer import write_file, make_dirs

     app = FastAPI()

     # Serve static ZIPs from /downloads
     if not os.path.isdir("downloads"):
         os.makedirs("downloads")
     app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

     # Initialize LLM & tools (global)
     ollama = Ollama(base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), model="vicuna-13b", temperature=0.2, max_tokens=1024)
     tools = [CodeGenCreateTool(), CodeGenRefactorTool(), MemoryStoreTool(), MemorySearchTool()]

     @app.post("/generate-app")
     async def generate_app(spec: dict):
         # Validate required fields
         required = ["project_name", "description", "features", "tech_stack", "styling"]
         if not all(k in spec for k in required):
             raise HTTPException(status_code=400, detail="Missing required spec fields")
         project_name = spec["project_name"]
         description = spec["description"]
         features = spec["features"]
         tech_stack = spec["tech_stack"]
         styling = spec["styling"]

         agent_id = f"agent-{uuid.uuid4()}"
         timestamp = datetime.datetime.utcnow().isoformat()

         # 1) Store user spec in memory
         MemoryStoreTool()._call(
             agent_id=agent_id,
             content=json.dumps({
               "project_name": project_name,
               "description": description,
               "features": features,
               "tech_stack": tech_stack,
               "styling": styling
             }),
             metadata={"step": "spec_submitted", "timestamp": timestamp}
         )

         # 2) Build planning prompt
         with open("prompts/app_generation_plan.txt") as f:
             template = f.read()
         plan_prompt = template.format(
             project_name=project_name,
             description=description,
             features=", ".join(features),
             tech_stack=tech_stack,
             styling=styling,
             agent_id=agent_id,
             timestamp=timestamp
         )

         # 3) Call Ollama to get JSON plan
         plan_text = ollama.generate(plan_prompt)
         try:
             steps = json.loads(plan_text)
         except json.JSONDecodeError:
             raise HTTPException(status_code=500, detail=f"Planning JSON malformed: {plan_text}")

         # 4) Create temp project folder
         base_dir = f"temp_projects/{agent_id}"
         if os.path.isdir(base_dir):
             shutil.rmtree(base_dir)
         os.makedirs(base_dir, exist_ok=True)

         # 5) Execute each plan step
         logs = []
         for step in steps:
             tool_name = step.get("tool")
             inputs = step.get("input", {})
             if not tool_name or not inputs:
                 logs.append(f"Invalid step: {step}")
                 continue

             # Map to tool
             tool_map = {
                 "codegen_create": CodeGenCreateTool(),
                 "codegen_refactor": CodeGenRefactorTool(),
                 "memory_store": MemoryStoreTool()
             }
             tool = tool_map.get(tool_name)
             if not tool:
                 logs.append(f"Unknown tool: {tool_name}")
                 continue

             observation = tool._call(**inputs)
             logs.append(f"Step: {tool_name} → {json.dumps(observation)}")

             # If code was generated, write file
             file_path = observation.get("file_path")
             code_content = observation.get("code")
             if file_path and code_content:
                 full_path = os.path.join(base_dir, file_path)
                 dir_name = os.path.dirname(full_path)
                 make_dirs(dir_name)
                 write_file(full_path, code_content)
                 logs.append(f"Wrote file: {full_path}")

         # 6) Assemble ZIP
         zip_name = f"{project_name}.zip"
         zip_path = os.path.join("downloads", zip_name)
         if os.path.isfile(zip_path):
             os.remove(zip_path)
         with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
             for root, _, files in os.walk(base_dir):
                 for fname in files:
                     abs_path = os.path.join(root, fname)
                     rel_path = os.path.relpath(abs_path, base_dir)
                     zipf.write(abs_path, arcname=os.path.join(project_name, rel_path))

         # 7) Final memory store of summary
         summary = f"Generated {project_name} with files: {json.dumps([ob.get('file_path') for ob in [s.get('input') for s in steps] if ob.get('file_path')])}"
         MemoryStoreTool()._call(
             agent_id=agent_id,
             content=summary,
             metadata={"step": "generation_complete", "project": project_name, "timestamp": datetime.datetime.utcnow().isoformat()}
         )

         return JSONResponse(content={"status": "success", "download_url": f"/downloads/{zip_name}", "logs": logs})

     @app.get("/recall-last-app")
     async def recall_last_app():
         # Search memory for “latest app spec”
         resp = MemorySearchTool()._call(query="latest app spec")
         results = resp.get("results", [])
         if not results:
             raise HTTPException(status_code=404, detail="No previous spec found.")
         # Assume first result is most recent
         mem = results[0]
         # Extract fields from stored content (assuming JSON-serialized spec)
         try:
             spec = json.loads(mem["content"])
             return JSONResponse(content={
                 "project_name": spec.get("project_name"),
                 "description": spec.get("description"),
                 "features": spec.get("features"),
                 "tech_stack": spec.get("tech_stack"),
                 "styling": spec.get("styling")
             })
         except json.JSONDecodeError:
             raise HTTPException(status_code=500, detail="Malformed memory content.")
     ```
   * Run:

     ```bash
     uvicorn main:app --reload --port 8000
     ```

2. **Implement Tool Wrappers**

   * **`tools/base_tool.py`** (shared HTTP logic; see Section 5.3).
   * **`tools/codegen_create_tool.py`**:

     ```python
     import os
     from .base_tool import BaseAINativeTool

     class CodeGenCreateTool(BaseAINativeTool):
         name = "codegen_create"
         description = (
             "Generate a new code file from a template. Input: { 'template': str, 'file_path': str, 'variables': dict }"
         )

         def _call(self, template: str, file_path: str, variables: dict):
             payload = {"template": template, "file_path": file_path, "variables": variables}
             return self._post("/api/v1/code-generation/create", payload, timeout=30)
     ```
   * **`tools/codegen_refactor_tool.py`**:

     ```python
     from .base_tool import BaseAINativeTool

     class CodeGenRefactorTool(BaseAINativeTool):
         name = "codegen_refactor"
         description = (
             "Refactor an existing code file. Input: { 'file_path': str, 'existing_code': str, 'instructions': str }"
         )

         def _call(self, file_path: str, existing_code: str, instructions: str):
             payload = { "file_path": file_path, "existing_code": existing_code, "instructions": instructions }
             return self._post("/api/v1/code-generation/refactor", payload, timeout=30)
     ```
   * **`tools/memory_store_tool.py`**:

     ```python
     from .base_tool import BaseAINativeTool

     class MemoryStoreTool(BaseAINativeTool):
         name = "memory_store"
         description = (
             "Store a memory entry. Input: { 'agent_id': str, 'content': str, 'metadata': dict }"
         )

         def _call(self, agent_id: str, content: str, metadata: dict):
             payload = { "agent_id": agent_id, "content": content, "metadata": metadata }
             return self._post("/api/v1/agent/memory", payload, timeout=10)
     ```
   * **`tools/memory_search_tool.py`**:

     ```python
     from .base_tool import BaseAINativeTool

     class MemorySearchTool(BaseAINativeTool):
         name = "memory_search"
         description = (
             "Search for memory entries. Input: { 'query': str }"
         )

         def _call(self, query: str):
             payload = { "query": query }
             return self._post("/api/v1/agent/memory/search", payload, timeout=10)
     ```

3. **Implement File Writing Utility**

   * **`utils/file_writer.py`**:

     ```python
     import os

     def make_dirs(path: str):
         os.makedirs(path, exist_ok=True)

     def write_file(path: str, content: str):
         with open(path, "w", encoding="utf-8") as f:
             f.write(content)
     ```

---

### 9.3 Phase 3 (Day 4): Frontend UI & Integration

1. **Initialize Frontend Project**

   * In `frontend/`, run (using React as example):

     ```bash
     npx create-react-app .
     npm install axios
     ```
   * Remove all default boilerplate except `public/index.html`, `src/index.js`.

2. **Create Components**

   * **`src/components/SpecForm.jsx`**:

     ```jsx
     import React, { useState } from "react";
     import axios from "axios";

     export default function SpecForm({ onGenerate, onRecall }) {
       const [projectName, setProjectName] = useState("");
       const [description, setDescription] = useState("");
       const [features, setFeatures] = useState("");
       const [techStack, setTechStack] = useState("React + FastAPI + PostgreSQL");
       const [styling, setStyling] = useState("TailwindCSS");

       const handleGenerate = async () => {
         const feats = features.split(",").map((f) => f.trim());
         const payload = {
           project_name: projectName,
           description: description,
           features: feats,
           tech_stack: techStack,
           styling: styling,
         };
         onGenerate(payload);
       };

       const handleRecall = async () => {
         onRecall();
       };

       return (
         <div className="p-4 bg-white rounded shadow-md">
           <h2 className="text-xl font-bold mb-2">App Generator</h2>
           <label className="block mb-1">Project Name</label>
           <input
             className="border w-full mb-2 p-1"
             type="text" value={projectName}
             onChange={(e) => setProjectName(e.target.value)}
           />
           <label className="block mb-1">Description</label>
           <textarea
             className="border w-full mb-2 p-1"
             value={description}
             onChange={(e) => setDescription(e.target.value)}
           />
           <label className="block mb-1">Features (comma-separated)</label>
           <input
             className="border w-full mb-2 p-1"
             type="text" value={features}
             onChange={(e) => setFeatures(e.target.value)}
           />
           <label className="block mb-1">Tech Stack</label>
           <select
             className="border w-full mb-2 p-1"
             value={techStack}
             onChange={(e) => setTechStack(e.target.value)}
           >
             <option>React + FastAPI + PostgreSQL</option>
             <option>Vue + Node.js + MongoDB</option>
           </select>
           <label className="block mb-1">Styling</label>
           <select
             className="border w-full mb-4 p-1"
             value={styling}
             onChange={(e) => setStyling(e.target.value)}
           >
             <option>TailwindCSS</option>
             <option>Bootstrap</option>
             <option>Plain CSS</option>
           </select>
           <button
             className="bg-blue-500 text-white px-4 py-2 rounded mr-2"
             onClick={handleGenerate}
           >
             Generate App
           </button>
           <button
             className="bg-gray-500 text-white px-4 py-2 rounded"
             onClick={handleRecall}
           >
             Recall Last App
           </button>
         </div>
       );
     }
     ```

   * **`src/components/StatusPanel.jsx`**:

     ```jsx
     import React from "react";

     export default function StatusPanel({ logs, downloadUrl, error }) {
       return (
         <div className="mt-4 p-4 bg-gray-100 rounded">
           <h3 className="text-lg font-semibold mb-2">Status & Logs</h3>
           {error && <p className="text-red-600">{error}</p>}
           <ul className="list-disc pl-5">
             {logs.map((entry, idx) => (
               <li key={idx} className="mb-1 text-sm">{entry}</li>
             ))}
           </ul>
           {downloadUrl && (
             <a
               href={downloadUrl}
               className="mt-4 inline-block bg-green-500 text-white px-4 py-2 rounded"
             >
               Download Your App
             </a>
           )}
         </div>
       );
     }
     ```

   * **`src/App.jsx`**:

     ```jsx
     import React, { useState } from "react";
     import SpecForm from "./components/SpecForm";
     import StatusPanel from "./components/StatusPanel";
     import axios from "axios";

     function App() {
       const [logs, setLogs] = useState([]);
       const [downloadUrl, setDownloadUrl] = useState("");
       const [error, setError] = useState("");

       const handleGenerate = async (payload) => {
         setLogs(["Starting generation..."]);
         setDownloadUrl("");
         setError("");
         try {
           const response = await axios.post("/generate-app", payload);
           const { download_url, logs: serverLogs } = response.data;
           setLogs((prev) => [...prev, ...serverLogs, "Generation complete."]);
           setDownloadUrl(download_url);
         } catch (err) {
           console.error(err);
           setError(err.response?.data?.detail || "Unknown error occurred.");
           setLogs((prev) => [...prev, "Generation failed."]);
         }
       };

       const handleRecall = async () => {
         setError("");
         try {
           const response = await axios.get("/recall-last-app");
           const spec = response.data;
           // Pre-fill form fields by simulating user input
           // (Alternatively, send the data back to SpecForm via props or context)
           // For simplicity, just log it for now:
           setLogs((prev) => [...prev, `Recalled spec: ${JSON.stringify(spec)}`]);
         } catch (err) {
           setError(err.response?.data?.detail || "No previous spec found.");
           setLogs((prev) => [...prev, "Recall failed."]);
         }
       };

       return (
         <div className="max-w-2xl mx-auto mt-8">
           <SpecForm onGenerate={handleGenerate} onRecall={handleRecall} />
           <StatusPanel logs={logs} downloadUrl={downloadUrl} error={error} />
         </div>
       );
     }

     export default App;
     ```

3. **Configure Proxy for Development**

   * In `frontend/package.json`, add:

     ```json
     "proxy": "http://localhost:8000"
     ```
   * This ensures `axios.post("/generate-app", ...)` forwards to `http://localhost:8000/generate-app`.

4. **Run Frontend**

   ```bash
   cd frontend
   npm install
   npm start
   ```

   * Visit `http://localhost:3000` (or the port CRA defaults to). The form should appear.

5. **Test End-to-End**

   * Fill out the form, click “Generate App,” observe logs streaming in the StatusPanel, and download the ZIP when ready.
   * Click “Recall Last App” to test memory recall (it should log the recalled spec in StatusPanel).

---

### 9.4 Phase 4 (Day 5): Testing, Documentation & Wrap-Up

1. **Unit Tests for Tool Wrappers**

   * Create `backend/tests/test_tools.py` to mock AINative responses using `pytest` fixtures and `responses` library (or `httpx.MockTransport`).
   * Validate that `CodeGenCreateTool._call(...)` correctly returns `{"file_path": "...", "code": "..."}` when AINative returns that.
   * Test error handling (e.g., AINative returns 500 → tool returns `{"error": true, "message": "..."}`).

2. **Integration Tests for `/generate-app`**

   * Create `backend/tests/test_generate_app.py` to simulate a full request using a local “fake” AINative server (e.g., a FastAPI test client that intercepts `/api/v1/code-generation/*` calls and returns canned responses).
   * Assert that `/generate-app` returns `status=“success”` and that a ZIP file appears in `downloads/`.

3. **Finalize README(s)**

   * **Root README.md** (in project root) describing:

     1. High-level architecture
     2. How to run Ollama (`ollama serve vicuna-13b`)
     3. How to start backend (`uvicorn main:app --reload`)
     4. How to start frontend (`npm start`)
     5. How to test “Recall Last App”
     6. Directory structure overview
     7. How to extend: adding new templates or tech stacks
   * **Backend/README.md** summarizing Python dependencies and endpoints.
   * **Frontend/README.md** summarizing React dependencies and how to customize UI.

4. **Internal Demo & Feedback**

   * Present the working POC to internal stakeholders (product manager, engineer).
   * Collect feedback on:

     * UI clarity
     * Typical generation time (< 90s)
     * Quality of generated code (does it compile/run with minimal tweaks?)
     * Memory recall usability

5. **Plan Next Milestones**

   * Based on feedback, identify what to add in a “Phase 2” (e.g., supporting additional tech stacks, adding drag-and-drop UI components, implementing multi-agent coordination).

---

## 10. Risks & Mitigations

| **Risk**                                                                                                 | **Impact**                              | **Mitigation**                                                                                                                        |
| -------------------------------------------------------------------------------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **Malformed JSON Plan from Ollama**                                                                      | Medium – generation aborts              | – Validate with `json.loads()`; if failure, retry with a simpler prompt or return an error message to user.                           |
| – Provide fallback logic: if no valid plan, generate a minimal default scaffold (e.g., static template). |                                         |                                                                                                                                       |
| **AINative Latency or Errors**                                                                           | High – generation stalls or fails       | – Implement exponential backoff (2 retries) for each AINative call.                                                                   |
| – Time each call; if > 15s, abort that step and inform user to try again later.                          |                                         |                                                                                                                                       |
| – Cache common templates locally to reduce repeated calls.                                               |                                         |                                                                                                                                       |
| **Ollama OOM / Unavailable**                                                                             | High – planning unavailable             | – Detect Ollama health at startup (`ollama.list_models()`); if unavailable, return “Service temporarily down, please restart Ollama.” |
| – Plan for cloud fallback (OpenAI) if local Ollama fails.                                                |                                         |                                                                                                                                       |
| **File System Permissions / Disk Space**                                                                 | Medium – cannot write files or zip      | – Ensure the server has write permissions to `temp_projects/` and `downloads/`.                                                       |
| – Monitor disk usage; clean up old temporary folders (> 24h) via a scheduled job.                        |                                         |                                                                                                                                       |
| **Browser CORS / Proxy Issues**                                                                          | Low – AJAX calls blocked                | – Configure FastAPI CORS middleware (e.g., allow `http://localhost:3000`).                                                            |
| – Use CRA’s `proxy` for local development.                                                               |                                         |                                                                                                                                       |
| **User Inputs Invalid or Malicious**                                                                     | Medium – code injection, path traversal | – Sanitize `project_name` (allow only alphanumeric and hyphens).                                                                      |
| – Reject or sanitize file paths; never allow absolute paths outside `temp_projects/{agent_id}`.          |                                         |                                                                                                                                       |
| – Escape variables in prompts that map to file paths.                                                    |                                         |                                                                                                                                       |
| **Poor Code Quality in Generated Scaffold**                                                              | Medium – user dissatisfaction           | – Provide a basic “lint and format” step post-generation (e.g., run `prettier` or `black` via a `bash` tool).                         |
| – Document clearly that this is a POC; generated code may need manual edits.                             |                                         |                                                                                                                                       |

---

## 11. Roadmap & Next Phases

### Phase 2: Extended Tech Stack & Template Library

* **Support Additional Stacks**:
  – Add templates for “Next.js + Django + MySQL,” “Svelte + Go + PostgreSQL,” etc.
  – Expand `Tech Stack` dropdown accordingly.
* **Dynamic Template Discovery**:
  – Store template definitions (template name → AINative variables schema) in a JSON/YAML file.
  – Allow administrators to add new templates without code changes.

### Phase 3: Multi-Agent Coordination & Parallelization

* **Agent Roles**:
  – **DBSchemaAgent**: Generates all database models.
  – **BackendAgent**: Generates backend routes and controllers.
  – **FrontendAgent**: Generates frontend components and wiring.
  – **StylingAgent**: Applies CSS frameworks or design system elements.
  – **FinalizerAgent**: Bundles, lints, and packages the project.
* **AINative Coordination API**:
  – Use `/api/v1/agent/coordination/sequences` to define and execute the above agent roles in parallel (where applicable).
  – Monitor each “task” status, capture results via webhooks or polling, and aggregate.

### Phase 4: Advanced Browser UI

* **Drag-and-Drop Component Canvas**:
  – Let users visually place “Login Form,” “Task List,” “Dashboard” components onto a canvas.
  – Under the hood, the UI translates placements into a JSON spec (component: “LoginForm”, position: x,y) and sends to backend.
* **Live Preview**:
  – After generation, spin up a temporary container to host the app at a URL (e.g., `http://localhost:9000/<agent_id>/`) so users can click through.

### Phase 5: User Authentication & Account Management

* **Sign-In / OAuth**:
  – Let users create accounts, link their GitHub (so generated code can be pushed to a private repo automatically).
  – Implement per-user `AINATIVE_API_KEY` scoping.
* **Usage Tracking & Quotas**:
  – Track how many “apps generated” per user per month; limit to free tier vs. paid tier.
  – Provide dashboard showing usage metrics and cost estimates (AINative API calls, Ollama tokens used).

---

## 12. Appendix

### 12.1 Sample File Structure (After Generation)

```
QuickNotes/
├── frontend/
│   ├── package.json
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── index.js
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── Login.jsx
│   │   │   ├── NotesList.jsx
│   │   │   └── NoteEditor.jsx
│   │   └── utils/
│   │       └── api.js         # API helper to call FastAPI backend
│   └── tailwind.config.js     # if styling=TailwindCSS
├── backend/
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── notes.py
│   │   │   └── dashboard.py
│   │   └── database.py        # DB engine / session setup
│   └── alembic.ini            # (optional migrations)
├── README.md
└── .gitignore
```

* **`frontend/package.json`** (example):

  ```json
  {
    "name": "quicknotes-frontend",
    "version": "0.1.0",
    "scripts": {
      "start": "react-scripts start",
      "build": "react-scripts build",
      "test": "react-scripts test"
    },
    "dependencies": {
      "axios": "^1.3.0",
      "bootstrap": "^5.2.0",
      "react": "^18.2.0",
      "react-dom": "^18.2.0",
      "react-router-dom": "^6.3.0",
      "react-scripts": "5.0.1"
    }
  }
  ```
* **`backend/requirements.txt`** (example):

  ```
  fastapi
  uvicorn
  sqlalchemy
  psycopg2-binary
  alembic
  bcrypt
  python-dotenv
  ```

### 12.2 Example Prompt for Code Generation (`app_generation_plan.txt`)

```
You are an AI planning agent. Given the following app specification:
  - Project Name: {project_name}
  - Description: {description}
  - Features: {features}
  - Tech Stack: {tech_stack}
  - Styling: {styling}

Produce a JSON array of generation steps. Each step must be an object with:
  {
    "tool": "<tool_name>",
    "input": { ... }
  }
Valid tools: codegen_create, codegen_refactor, memory_store.

The sequence should logically begin with database schema generation, then backend routes, then frontend components, styling, and finally README. Do not output anything but valid JSON.

Example output:
[
  {
    "tool": "codegen_create",
    "input": {
      "template": "sqlalchemy-model",
      "file_path": "backend/app/models.py",
      "variables": {
        "model_name": "User",
        "fields": ["id:int:primary", "username:str:unique", "password:str"],
        "db": "PostgreSQL"
      }
    }
  },
  {
    "tool": "codegen_create",
    "input": {
      "template": "fastapi-route",
      "file_path": "backend/app/routes/auth.py",
      "variables": {
        "router_name": "auth_router",
        "path": "/auth",
        "methods": ["POST /signup", "POST /login"]
      }
    }
  },
  {
    "tool": "codegen_create",
    "input": {
      "template": "react-component",
      "file_path": "frontend/src/components/Login.jsx",
      "variables": {
        "component_name": "Login",
        "styling": "Bootstrap"
      }
    }
  },
  {
    "tool": "memory_store",
    "input": {
      "agent_id": "{agent_id}",
      "content": "Generated {project_name}: User model, auth routes, login component, notes CRUD, Bootstrap styling.",
      "metadata": {
        "project": "{project_name}",
        "timestamp": "{timestamp}"
      }
    }
  }
]
```

---

## 13. Conclusion

This PRD provides a comprehensive blueprint for a browser-based app generator POC, harnessing the combined power of **AINative Studio’s code-generation and memory APIs**, **LangChain’s orchestration**, and **Ollama’s local LLM**. By following this document, the team can:

1. **Rapidly build** a working prototype where non-technical users specify their desired app features in a web form and receive a downloadable code scaffold within minutes.
2. **Validate core integrations**—ensuring code generation, memory storage/retrieval, and prompt planning function cohesively.
3. **Lay the groundwork** for future expansion into multi-agent coordination, advanced GUIs (drag-and-drop), quantum enhancements, and production-grade deployment.

