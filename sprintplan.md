## Sprint Overview

* **Sprint Length:** 1 calendar day (8 productive hours)
* **Sprint Goal:** Deliver MVP “App Generator” end‐to‐end:

  1. Browser form for “App Spec”
  2. Backend integration (LangChain, Ollama, AINative tool wrappers)
  3. File assembly + ZIP download
  4. “Recall Last App” via AINative memory
* **Team Roles:**

  * **Developer / Orchestrator**: Implements backend (FastAPI + LangChain + Ollama + AINative wrappers)
  * **Frontend Engineer**: Implements browser UI (React or Vue) + AJAX integration
  * (If single person, they time‐slice and switch contexts)

---

## Sprint Backlog (User Stories)

1. **US001 (Setup & Tool Wrappers)**

   * **As a** developer,
   * **I want** to configure local development environment (Python, Ollama, AINative API key) and implement basic AINative‐wrapped “tools” (codegen\_create, codegen\_refactor, memory\_store, memory\_search),
   * **So that** I can call AINative endpoints programmatically in my backend.

2. **US002 (Database & Data Model)**

   * **As a** developer,
   * **I want** to define and spin up the relational schema (`projects`, `generation_steps`, `logs`, `memory_records`),
   * **So that** I can persist “project metadata,” “tool‐invocation steps,” and “memory references.”

3. **US003 (Backend Endpoints & LangChain Integration)**

   * **As a** developer,
   * **I want** to build `/generate-app` and `/recall-last-app` endpoints in FastAPI, integrate LangChain + Ollama planning prompt, execute each planned step by calling AINative wrappers, write files to disk, assemble project folder into ZIP, and return a download URL,
   * **So that** the browser can trigger end‐to‐end code generation.

4. **US004 (Frontend UI & AJAX)**

   * **As a** non‐technical user,
   * **I want** a simple form (project name, description, features, tech stack, styling) plus “Generate App” and “Recall Last App” buttons,
   * **So that** I can submit my spec and see generation logs + download link in a single page.

5. **US005 (File Writing + ZIP Packaging)**

   * **As a** developer,
   * **I want** utilities to write AINative‐returned code strings into the correct folder structure (e.g., `frontend/src/components/…`, `backend/app/models.py`),
   * **So that** I can zip the entire project and serve it via `/downloads`.

6. **US006 (Status/Logging Stream)**

   * **As a** user,
   * **I want** to see real‐time logs (“Planning…,” “Generating models…,” “Wrote file X,” “Complete!”) in the browser,
   * **So that** I know how the generation is progressing (and if it fails).

7. **US007 (Memory Recall)**

   * **As a** returning user,
   * **I want** to click “Recall Last App” and have my previous spec pre‐fill the form,
   * **So that** I can easily regenerate or tweak my last app.

---

## Timeboxed Workday Schedule

| **Time**                                    | **Task**                               | **Est. Duration** | **Notes / Acceptance Criteria** |
| ------------------------------------------- | -------------------------------------- | ----------------- | ------------------------------- |
| **9:00–9:30**                               | **Sprint Kickoff & Environment Setup** |                   |                                 |
| • Review PRD, data model, folder structure. |                                        |                   |                                 |
| • Confirm Ollama is installed and running:  |                                        |                   |                                 |

```bash
ollama serve vicuna-13b
```

• Verify AINative API key is in env: `export AINATIVE_API_KEY=…`.
• Create Python virtualenv / install dependencies:

```
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn langchain requests python-dotenv sqlalchemy psycopg2-binary
```

• Create React (or Vue) scaffold:

````
cd frontend
npx create-react-app .
npm install axios
``` | 30 min            | − “Ollama” responds to `GET http://localhost:11434/v1/models`.  
− AINative env var is set.  
− FastAPI + React projects created, dependencies installed.  
− Folder structure established:
````

backend/
main.py
tools/
prompts/
utils/
requirements.txt
frontend/
public/
src/
package.json

````
− Developer(s) ready to code. |
| **9:30–10:30** | **US001: Implement BaseAINativeTool & Four Tool Wrappers**  
1. **tools/base_tool.py**:  
 ```python
 import os, requests
 class BaseAINativeTool:
     def __init__(self):
         self.base_url = os.getenv("AINATIVE_BASE_URL", "https://api.ainative.studio")
         self.api_key  = os.getenv("AINATIVE_API_KEY")
     def _post(self, path: str, payload: dict, timeout: int = 30):
         headers = {"Authorization": f"Bearer {self.api_key}"}
         try:
             r = requests.post(f"{self.base_url}{path}", json=payload, headers=headers, timeout=timeout)
             r.raise_for_status()
             return r.json()
         except Exception as e:
             return {"error": True, "message": str(e)}
````

2. **tools/codegen\_create\_tool.py**:

   ```python
   from .base_tool import BaseAINativeTool
   class CodeGenCreateTool(BaseAINativeTool):
       name = "codegen_create"
       description = "Generate a new code file: {template, file_path, variables}"
       def _call(self, template: str, file_path: str, variables: dict):
           return self._post("/api/v1/code-generation/create", {"template": template, "file_path": file_path, "variables": variables})
   ```
3. **tools/codegen\_refactor\_tool.py**:

   ```python
   from .base_tool import BaseAINativeTool
   class CodeGenRefactorTool(BaseAINativeTool):
       name = "codegen_refactor"
       description = "Refactor an existing code file: {file_path, existing_code, instructions}"
       def _call(self, file_path: str, existing_code: str, instructions: str):
           return self._post("/api/v1/code-generation/refactor", {"file_path": file_path, "existing_code": existing_code, "instructions": instructions})
   ```
4. **tools/memory\_store\_tool.py**:

   ```python
   from .base_tool import BaseAINativeTool
   class MemoryStoreTool(BaseAINativeTool):
       name = "memory_store"
       description = "Store a memory entry: {agent_id, content, metadata}"
       def _call(self, agent_id: str, content: str, metadata: dict):
           return self._post("/api/v1/agent/memory", {"agent_id": agent_id, "content": content, "metadata": metadata})
   ```
5. **tools/memory\_search\_tool.py**:

   ```python
   from .base_tool import BaseAINativeTool
   class MemorySearchTool(BaseAINativeTool):
       name = "memory_search"
       description = "Search memory entries: {query}"
       def _call(self, query: str):
           return self._post("/api/v1/agent/memory/search", {"query": query})
   ```
6. **Quick Manual Tests**:

   * In Python REPL / small script, instantiate each tool and call with dummy data (e.g., `CodeGenCreateTool()._call("react-component", "foo.txt", {"component_name":"Test","styling":"TailwindCSS"})`).
   * Verify that, if no real AINative connection, it returns `{"error": True, …}` gracefully.

\| 1 hr             | − Four classes exist under `backend/tools/`.
− Each class compiles (no syntax errors) and can be instantiated.
− A dummy `.py` script imports each, calls `_call(...)`, and receives a valid JSON response or structured error.
− Code is formatted (PEP8) and committed to Git. |
\| **10:30–10:45** | **Break**                                                                                                                                                                                                                                                                                                                                                                                                                        | 15 min            | —                                                                                                                                                                                                                                                                                                                                                                                                                                              |
\| **10:45–11:45** | **US002: Define & Migrate Data Model**

1. **Install and configure PostgreSQL** (local or Docker‐Postgres).
2. **Create database**: `CREATE DATABASE appgenerator;`.
3. **SQLAlchemy Setup (optional)**: If you choose SQLAlchemy for ease, define models. Otherwise, run raw SQL migrations.

   ```python
   # in backend/models.py (SQLAlchemy)
   from sqlalchemy import Column, String, Text, JSON, TIMESTAMP, func
   from sqlalchemy.dialects.postgresql import UUID as PG_UUID
   from sqlalchemy.ext.declarative import declarative_base
   Base = declarative_base()

   class Project(Base):
       __tablename__ = "projects"
       project_id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
       project_name = Column(Text, nullable=False)
       description = Column(Text)
       features = Column(JSON, nullable=False)
       tech_stack = Column(Text, nullable=False)
       styling = Column(Text, nullable=False)
       agent_id = Column(Text, nullable=False, unique=True)
       initial_memory_id = Column(Text)
       final_memory_id = Column(Text)
       status = Column(Text, nullable=False, default="IN_PROGRESS")  # CHECK constraint omitted for brevity
       download_url = Column(Text)
       created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
       updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

   class GenerationStep(Base):
       __tablename__ = "generation_steps"
       step_id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
       project_id = Column(PG_UUID(as_uuid=True), ForeignKey("projects.project_id"), nullable=False)
       sequence_order = Column(Integer, nullable=False)
       tool_name = Column(Text, nullable=False)
       input_payload = Column(JSON)
       output_payload = Column(JSON)
       status = Column(Text, nullable=False, default="PENDING")
       created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
       updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

   class LogEntry(Base):
       __tablename__ = "logs"
       log_id = Column(Integer, primary_key=True, autoincrement=True)
       project_id = Column(PG_UUID(as_uuid=True), ForeignKey("projects.project_id"), nullable=False)
       log_text = Column(Text, nullable=False)
       created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

   class MemoryRecord(Base):
       __tablename__ = "memory_records"
       memory_record_id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
       project_id = Column(PG_UUID(as_uuid=True), ForeignKey("projects.project_id"), nullable=False)
       memory_id = Column(Text, nullable=False)
       content = Column(Text, nullable=False)
       metadata = Column(JSON)
       created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
   ```
4. **Run Migration / Create Tables** (using raw SQL or SQLAlchemy’s `Base.metadata.create_all(engine)`).
5. **Verify**: Connect with `psql` or a GUI (e.g., pgAdmin) and confirm tables exist with correct columns.

\| 1 hr             | − PostgreSQL database “appgenerator” is created.
− All four tables exist (`projects`, `generation_steps`, `logs`, `memory_records`).
− Columns match the schema (types, defaults).
− (If SQLAlchemy used) can `Base.metadata.create_all()`.
− Tables are empty and ready to accept data. |
\| **11:45–12:45** | **US003: Backend Endpoints Skeleton**

1. **FastAPI Boilerplate** in `backend/main.py`:

   ```python
   from fastapi import FastAPI, HTTPException
   from fastapi.responses import JSONResponse
   from fastapi.staticfiles import StaticFiles

   app = FastAPI()
   app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

   @app.post("/generate-app")
   async def generate_app(spec: dict):
       # For now, stub out with a placeholder response
       return JSONResponse(content={"status": "in_progress", "message": "Stub: Generate logic TBD"})

   @app.get("/recall-last-app")
   async def recall_last_app():
       # Stubbed: return sample spec or 404
       return JSONResponse(content={"error": "No previous spec found."}, status_code=404)
   ```
2. **Integrate SQLAlchemy Session** (or raw connections) so that inside `/generate-app`, you can:

   * Insert into `projects` table
   * Insert into `memory_records` for initial spec storage (using `MemoryStoreTool`)
   * Insert into `generation_steps` (placeholders)
   * Update status fields later
3. **Test with `curl`**:

   ```bash
   curl -X POST "http://localhost:8000/generate-app" \
     -H "Content-Type: application/json" \
     -d '{"project_name":"TestApp","description":"desc","features":["A"],"tech_stack":"React+FastAPI","styling":"Bootstrap"}'
   ```

   → Returns `{ "status": "in_progress", "message": "Stub: Generate logic TBD" }`.
4. **Ensure logs table and generation\_steps table are empty** at startup.

\| 1 hr             | − FastAPI app starts without errors (`uvicorn main:app --reload`).
− `/generate-app` responds with the stub JSON.
− `/recall-last-app` responds 404 with JSON error.
− Able to connect to DB, create a new `projects` row from within the endpoint (tested via a quick SQL insert in code).
− No extraneous errors or 500s. |
\| **12:45–1:30**  | **Lunch Break**                                                                                                                                                                                                                                                                                                                                                                                                                   | 45 min            | —                                                                                                                                                                                                                                                                                                                                                                                                                                              |
\| **1:30–2:45**  | **US003 (continued): Ollama Planning & Step Insertion**

1. **Load Planning Prompt** from `backend/prompts/app_generation_plan.txt`.
2. **Instantiate Ollama (LangChain LLM) & Tools**:

   ```python
   from langchain.llms import Ollama
   from tools.codegen_create_tool import CodeGenCreateTool
   from tools.codegen_refactor_tool import CodeGenRefactorTool
   from tools.memory_store_tool import MemoryStoreTool
   from tools.memory_search_tool import MemorySearchTool

   ollama = Ollama(base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), model="vicuna-13b", temperature=0.2, max_tokens=1024)
   tools = {
     "codegen_create": CodeGenCreateTool(),
     "codegen_refactor": CodeGenRefactorTool(),
     "memory_store": MemoryStoreTool()
   }
   ```
3. **Inside `/generate-app`**:

   * **a.** Extract JSON payload.
   * **b.** Insert a new `projects` row (capture `project_id` & `agent_id`).
   * **c.** Call `MemoryStoreTool()._call(agent_id, json.dumps(spec), {"step":"spec_submitted","timestamp":now})` → returns `{"memory_id":"m123"}`.
   * **d.** Insert into `memory_records` with that `memory_id`.
   * **e.** Format planning prompt with spec + `agent_id` + `timestamp`.
   * **f.** Call `plan_text = ollama.generate(plan_prompt)`.
   * **g.** `steps = json.loads(plan_text)` (validate with `try/except`). If malformed, update `projects.status='FAILED'` and return 500.
   * **h.** For each step in `steps`, insert a row into `generation_steps` with `sequence_order = i+1`, `tool_name = step["tool"]`, `input_payload = step["input"]`.
4. **Return a preliminary response**:

   ```json
   {
     "status": "in_progress",
     "project_id": "<uuid>",
     "logs": ["Planning completed, inserting 8 steps…"]
   }
   ```

   (We will fill in the “full execution” later.)
5. **Test** by POSTing a minimal spec; inspect the DB:

   * One new `projects` row, `status='IN_PROGRESS'`.
   * One new `memory_records` row for spec.
   * Eight new `generation_steps` rows with correct `input_payload`.

\| 1 hr 15 min      | − Ollama returns a valid JSON plan (use a simple test prompt if needed).
− All new rows inserted correctly (checked via `psql`).
− `/generate-app` returns status and project\_id without error.
− If plan JSON is invalid, `projects.status` is updated to `FAILED` and an HTTP 500 is returned.
− No unhandled exceptions. |
\| **2:45–3:30**  | **US005: File‐Writing Utilities + Step Execution Loop Skeleton**

1. **Implement `backend/utils/file_writer.py`**:

   ```python
   import os

   def make_dirs(path: str):
       os.makedirs(path, exist_ok=True)

   def write_file(path: str, content: str):
       with open(path, "w", encoding="utf-8") as f:
           f.write(content)
   ```
2. **Extend `/generate-app`** (continuing above) with an execution loop (pseudocode):

   ```python
   base_dir = f"temp_projects/{project_id}"
   os.makedirs(base_dir, exist_ok=True)

   for idx, step in enumerate(steps):
       tool_name = step["tool"]
       inputs = step["input"]
       # Call AINative wrapper
       tool = tools.get(tool_name)
       if not tool:
           # Insert a FAILED status for this step
           update_generation_step_status(...)
           logs.append(f"Unknown tool: {tool_name}")
           continue
       obs = tool._call(**inputs)
       # Update generation_steps.row to status=SUCCESS or FAILED and store output_payload = obs
       # Example:
       # UPDATE generation_steps SET output_payload = obs::JSONB, status='SUCCESS' WHERE step_id=...
       # If obs contains file_path & code, write to disk:
       if "file_path" in obs and "code" in obs:
           full_path = os.path.join(base_dir, obs["file_path"])
           make_dirs(os.path.dirname(full_path))
           write_file(full_path, obs["code"])
           logs.append(f"Wrote file: {obs['file_path']}")
       else:
           logs.append(f"Tool {tool_name} returned no file.")
   ```
3. **Insert Logs** into `logs` table after each major action (`“Called tool X”`, `“Wrote file Y”`, `“Step i SUCCESS/FAILED”`).
4. **Package ZIP** (skeleton; actual zipping later):

   ```python
   import zipfile
   zip_path = f"downloads/{project_name}.zip"
   with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
       for root, _, files in os.walk(base_dir):
           for fname in files:
               abs_path = os.path.join(root, fname)
               rel_path = os.path.relpath(abs_path, base_dir)
               zipf.write(abs_path, arcname=os.path.join(project_name, rel_path))
   ```
5. **Update `projects.download_url = f"/downloads/{project_name}.zip"`, `projects.status = 'SUCCESS'`**.

\| 45 min            | − After speaking to Ollama, each step is executed in order.
− Files are written under `temp_projects/<project_id>/…` with correct paths.
− A ZIP file is created under `downloads/<project_name>.zip`.
− Corresponding `generation_steps.status` rows are updated.
− Logs inserted in `logs` table (“Called tool X”, “Wrote file Y”, “Step i SUCCESS”).
− No uncaught errors (wrapped in try/except). |
\| **3:30–4:30**  | **US004: Frontend UI & AJAX Integration**

1. **SpecForm Component** (in `frontend/src/components/SpecForm.jsx`):

   * Fields: `projectName`, `description`, `features`, `techStack`, `styling`.
   * Buttons: “Generate App” → calls `POST /generate-app` via Axios.
   * “Recall Last App” → calls `GET /recall-last-app`.
   * On success: push logs into parent state, show “Download” when provided.
2. **StatusPanel Component** (`frontend/src/components/StatusPanel.jsx`):

   * Props: `logs` array, `downloadUrl`, `error` string.
   * Renders a scrollable list of `<li>` for each log.
   * If `downloadUrl` present, renders `<a href={downloadUrl}>Download ZIP</a>`.
3. **App Container** (`frontend/src/App.jsx`):

   * Holds state:

     ```js
     const [logs, setLogs] = useState([]);
     const [downloadUrl, setDownloadUrl] = useState("");
     const [error, setError] = useState("");
     ```
   * Functions:

     ```js
     const handleGenerate = async (payload) => {
       setLogs(["Starting generation…"]);
       setDownloadUrl("");
       setError("");
       try {
         const resp = await axios.post("/generate-app", payload);
         // Append returned logs, if any
         if (resp.data.logs) {
           setLogs((prev) => [...prev, ...resp.data.logs, "Generation complete."]);
         }
         setDownloadUrl(resp.data.download_url);
       } catch (err) {
         setError(err.response?.data?.detail || "Unknown error");
         setLogs((prev) => [...prev, "Generation failed."]);
       }
     };

     const handleRecall = async () => {
       setError("");
       try {
         const resp = await axios.get("/recall-last-app");
         const spec = resp.data;
         // Pre-fill form: (we can lift state or use a callback to SpecForm)
         setLogs((prev) => [...prev, `Recalled spec: ${JSON.stringify(spec)}`]);
         // Optionally pass spec down as props to SpecForm to pre-fill fields
       } catch (err) {
         setError(err.response?.data?.detail || "No previous spec.");
         setLogs((prev) => [...prev, "Recall failed."]);
       }
     };
     ```
4. **Configure Proxy**: In `frontend/package.json`, add:

   ```json
   "proxy": "http://localhost:8000"
   ```

   So that `/generate-app` maps to backend.
5. **Test End‐to‐End (Frontend ↔ Backend)**:

   * Run `npm start` and `uvicorn main:app --reload` simultaneously.
   * Fill out form, click “Generate App,” observe logs appear.
   * Confirm “Download ZIP” link appears once backend finishes.
   * Click “Recall Last App,” confirm logs show “Recalled spec: …”.

\| 1 hr             | − Browser form renders correctly with fields and buttons.
− Clicking “Generate App” triggers the backend; initial log “Starting generation…” appears.
− As backend returns JSON (with `logs`), logs append to StatusPanel.
− Once backend signals completion, “Download ZIP” link is visible and points to `http://localhost:8000/downloads/<project>.zip`.
− “Recall Last App” populates the logs with the recalled spec.
− No CORS or proxy errors in console. |
\| **4:30–5:00**  | **US006 & US007: Final Testing, Logging & Memory Recall Polishing**

1. **Stress Test**:

   * Generate an extremely simple “HelloWorld” spec (e.g., no features list) to confirm the system handles minimal cases.
   * Generate a slightly larger spec (5 features) to assess performance.
2. **Verify Memory Recall**:

   * After a successful generation, click “Recall Last App”—confirm that the form fields (in console or visually) reflect the last spec.
   * Inspect `memory_records` table: ensure there are two entries: spec submission and final summary.
3. **Log Persistence**:

   * Confirm that all logs for a given `project_id` are in `logs` table with proper timestamps.
   * Confirm that backend pushes new log entries as JSON in `/generate-app` response.
4. **Error Conditions**:

   * Temporarily stop Ollama or AINative (unsetting API key) and attempt “Generate App” → confirm user sees a clear error (“Ollama unavailable” or “AINative call failed”).
   * Test `/recall-last-app` when no memory exists → confirm 404 JSON.
5. **Wrap‐Up**:

   * Update final statuses: if backend did not already update, set `projects.status='SUCCESS'` in DB.
   * Commit all code, push to shared repo.
   * Document any known bugs or “stretch goals” (e.g., prompt fixes, additional tech stacks) in a short “Issues” list.

\| 30 min            | − “HelloWorld” and “QuickNotes” both generate valid ZIPs, browsable locally.
− `memory_records` has exactly two rows for each project: one for spec, one for final summary.
− `logs` table shows a full step‐by‐step log for the generation.
− Errors are captured and surfaced clearly to the browser.
− Backend `projects.status` fields reflect `SUCCESS` or `FAILED`.
− All tasks for US001–US007 have “Done” acceptance criteria met. |

---

## Summary of Deliverables by End of Day

1. **Git Repository** with two top‐level folders:

   * **`backend/`** (FastAPI server, LangChain/Ollama integration, AINative tool wrappers, data model, file writer, endpoints, migrations)
   * **`frontend/`** (React app with SpecForm, StatusPanel, AJAX logic, `proxy` configuration)
2. **Working MVP** on `http://localhost:3000`:

   * Fill out “App Spec” form, see real‐time logs, download a `.zip` for a generated project.
   * Click “Recall Last App” and have the form repopulate (or logs show the recalled spec).
3. **Database Schema** in PostgreSQL (or SQLite for speed, if necessary) with all four tables (`projects`, `generation_steps`, `logs`, `memory_records`) populated appropriately.
4. **README.md** (root) describing:

   * How to install and run Ollama (`ollama serve vicuna-13b`).
   * How to set AINative API key (`export AINATIVE_API_KEY=…`).
   * How to start backend (`cd backend && pip install -r requirements.txt && uvicorn main:app --reload`).
   * How to start frontend (`cd frontend && npm install && npm start`).
   * Quick example: “Generate a Notes App,” “Recall Last App.”
5. **Basic Unit Tests (Optional, if time permits)**:

   * A few `pytest` tests validating tool wrappers (mocking AINative).
   * A simple test for `/generate-app` returning `status=in_progress` when using a fake plan JSON.

---

## Post‐Sprint Retrospective & Next Steps

At day’s end, conduct a quick retro (15 min) to capture:

1. **What Went Well**

   * End‐to‐end flow completed in under 8 hours.
   * Ollama planning prompt produced a valid JSON plan on first try (with minor tweaks).
   * Browser UI integrated seamlessly via React → FastAPI proxy.

2. **What Didn’t Go Well**

   * Minor JSON parsing errors (e.g., Ollama output had trailing comments) required prompt tweaks.
   * Disk space cleanup: old `temp_projects/` folders accumulate; need a scheduled garbage collector.
   * Some AINative calls experienced transient timeouts requiring retries.

3. **Action Items for Tomorrow (Stretch Goals)**

   * **Add another Tech Stack**: e.g., “Vue + Node.js + MongoDB” templates & prompts.
   * **Implement Basic Lint/Format**: after codegen, run `prettier` on JS and `black` on Python.
   * **Dockerize**: create a Dockerfile for the entire POC (backend + frontend + Ollama as a service) for reproducibility.
   * **Expand Memory Recall**: let user choose from the last 5 specs, not just “latest.”
   * **Error Email Notifications**: if a generation fails, send an email (or Slack message) to developer.

