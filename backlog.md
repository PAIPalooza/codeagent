## Epic 1: Core App Generator MVP

**Goal**: Deliver an end-to-end “App Spec → Code Scaffold → Download ZIP” flow, plus basic memory recall.
**Value**: Prove the basic feasibility of orchestrating Ollama + AINative + LangChain behind a simple browser UI.

### Sprint 1 (1 Week) – MVP Delivery

**Sprint Objective**

> Implement the minimal vertically-sliced “Browser UI → Backend Orchestration → AINative Codegen → File Assembly → ZIP Download” workflow, plus “Recall Last App” memory retrieval.

#### User Stories (US)

1. **US1.1 (Environment & Tooling Setup)**

   * **As a** developer,
   * **I want** to provision and verify my local dev environment (Python 3.9+, Ollama, AINative API key, React/Vue tooling),
   * **So that** I can begin implementing code without configuration roadblocks.
   * **Acceptance Criteria**:

     * Ollama is running locally (`ollama serve vicuna-13b`).
     * `AINATIVE_API_KEY` and `AINATIVE_BASE_URL` are set in `.env`.
     * `backend/` has a functioning virtual environment, `pip install -r requirements.txt` passes.
     * `frontend/` (Create React App or Vue CLI) builds and runs with no errors.

2. **US1.2 (Data Model & Database Setup)**

   * **As a** developer,
   * **I want** to define and migrate the relational schema (`projects`, `generation_steps`, `logs`, `memory_records`),
   * **So that** I can persist “app generation” metadata, tool-execution steps, logs, and memory references.
   * **Acceptance Criteria**:

     * PostgreSQL (or SQLite) is reachable, schema is created exactly as specified.
     * Running a migration script (SQL or SQLAlchemy) generates all four tables.
     * Each table’s columns, types, and constraints match the PRD’s data model.

3. **US1.3 (AINative Tool Wrappers)**

   * **As a** developer,
   * **I want** to implement Python wrappers around AINative’s endpoints (`code-generation/create`, `code-generation/refactor`, `agent/memory`, `agent/memory/search`),
   * **So that** I can call AINative programmatically under a consistent interface.
   * **Acceptance Criteria**:

     * Classes `CodeGenCreateTool`, `CodeGenRefactorTool`, `MemoryStoreTool`, `MemorySearchTool` exist under `backend/tools/`.
     * Each wrapper sends a POST to the correct AINative path with `Authorization: Bearer {API_KEY}`.
     * When called with dummy data, each returns either a valid JSON response (if AINative is reachable) or a structured `{"error": true, "message": …}`.

4. **US1.4 (Basic File‐Writer Utility)**

   * **As a** developer,
   * **I want** a small utility (`make_dirs`, `write_file`) to write code strings to a given file path under a base folder,
   * **So that** I can assemble the generated project on disk.
   * **Acceptance Criteria**:

     * `backend/utils/file_writer.py` exists with two functions:

       ```python
       def make_dirs(path: str): ...
       def write_file(path: str, content: str): ...
       ```
     * A quick smoke test (`write_file("temp/foo/bar.txt", "hello")`) writes the file and creates parent dirs if necessary.

5. **US1.5 (Backend Endpoint Skeleton & LangChain Integration)**

   * **As a** developer,
   * **I want** to scaffold two FastAPI endpoints—`POST /generate-app` and `GET /recall-last-app`—and wire in a minimal LangChain + Ollama “plan” call,
   * **So that** the backend is ready to receive app specs and plan out steps.
   * **Acceptance Criteria**:

     * `backend/main.py` defines:

       ```python
       @app.post("/generate-app")
       async def generate_app(spec: dict): ...
       @app.get("/recall-last-app")
       async def recall_last_app(): ...
       ```
     * The `generate_app` handler:

       1. Validates that `spec` has all required fields (`project_name`, `description`, `features`, `tech_stack`, `styling`).
       2. Instantiates `ollama = Ollama(base_url=…, model="vicuna-13b")`.
       3. Calls `plan_text = ollama.generate(…)` with a placeholder prompt (returns a JSON string).
       4. Parses `steps = json.loads(plan_text)`; on failure, raises HTTP 500.
       5. Inserts a new row into `projects` (status=`IN_PROGRESS`, capturing `agent_id`).
       6. Returns a JSON response `{ "status": "in_progress", "project_id": "<uuid>" }` to the caller.
     * The `recall_last_app` handler:

       1. Calls `MemorySearchTool()._call(query="latest app spec")`.
       2. If no results, returns HTTP 404 `{ "error": "No previous spec found." }`.
       3. Else, returns the top memory’s content as parsed JSON (`project_name`, `description`, `features`, `tech_stack`, `styling`).
     * Manual test with `curl` confirms endpoints return expected stubs.

6. **US1.6 (Step Insertion & Status Logging)**

   * **As a** developer,
   * **I want** to take the JSON plan from Ollama (an array of steps) and insert each step into the `generation_steps` table (status=`PENDING`),
   * **So that** I can later track execution status per step.
   * **Acceptance Criteria**:

     * Following parsing of `steps`, for each element `(i, step_obj)` in `steps`, insert a new `generation_steps` row with:

       * `project_id` = the new project’s UUID
       * `sequence_order` = `i+1`
       * `tool_name` = `step_obj["tool"]`
       * `input_payload` = JSONB of `step_obj["input"]`
       * `status` = `PENDING`
     * If any insert fails, rollback and return a 500.
     * Querying `SELECT * FROM generation_steps WHERE project_id=…` returns exactly N rows (one per step).

7. **US1.7 (Execution Loop & File Assembly)**

   * **As a** developer,
   * **I want** to iterate over all `PENDING` `generation_steps`, call the corresponding AINative wrapper, update each row’s `status` to `SUCCESS`/`FAILED` and store `output_payload`, then write code (if any) to disk under `temp_projects/<project_id>/<file_path>`,
   * **So that** the full project folder (frontend + backend) is assembled.
   * **Acceptance Criteria**:

     * Loop retrieves all steps in `sequence_order`, calling `tools[tool_name]._call(**input_payload)`.
     * On each call’s response (`obs`), update `generation_steps.output_payload=obs`, `status='SUCCESS'` if no `obs.get("error")`, else `status='FAILED'`.
     * If `obs` contains `file_path` and `code`, call `make_dirs(os.path.dirname(full_path))` and `write_file(full_path, obs["code"])`.
     * If any step fails, record an error and proceed to the next step (don’t abort the entire loop).
     * At the end of the loop, verify that at least one file was written in `temp_projects/<project_id>/…` (e.g., `backend/app/models.py`).

8. **US1.8 (ZIP Packaging & Download URL)**

   * **As a** developer,
   * **I want** to zip the entire `temp_projects/<project_id>/` folder into `downloads/<project_name>.zip` and update `projects.download_url = "/downloads/<project_name>.zip"`, `projects.status = "SUCCESS"`,
   * **So that** the browser can offer a `Download ZIP` link.
   * **Acceptance Criteria**:

     * After file assembly, code runs:

       ```python
       zip_path = f"downloads/{project_name}.zip"
       with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
           for root, _, files in os.walk(base_dir):
               for fname in files:
                   abs_path = os.path.join(root, fname)
                   rel_path = os.path.relpath(abs_path, base_dir)
                   zipf.write(abs_path, arcname=os.path.join(project_name, rel_path))
       ```
     * A new file `downloads/<project_name>.zip` exists on disk.
     * `projects` row is updated:

       ```sql
       UPDATE projects
         SET download_url = '/downloads/<project_name>.zip',
             status = 'SUCCESS',
             updated_at = NOW()
       WHERE project_id = <id>;
       ```
     * A `GET http://localhost:8000/downloads/<project_name>.zip` returns the ZIP.

9. **US1.9 (Status Logging & Streaming to Frontend)**

   * **As a** user,
   * **I want** to see real-time logs (e.g., “Planning…”, “Generated file: backend/app/models.py”, “Packaging complete”) in the UI as the backend works,
   * **So that** I know the generation progress and can diagnose failures.
   * **Acceptance Criteria**:

     * After each major action (plan parsing, step call, file write, zip creation), backend inserts a row into `logs(project_id, log_text)`.
     * The `/generate-app` response JSON includes an array field `"logs": [<all logs so far>]`.
     * The frontend’s StatusPanel appends each new log entry to a scrolling list.
     * If a tool fails, a log entry like `"Step 3 (codegen_create) failed: <error message>"` appears.

10. **US1.10 (Recall Last App – End-to-End)**

    * **As a** user,
    * **I want** to click “Recall Last App” in the browser,
    * **So that** the form fields are pre-populated with my most recent app spec.
    * **Acceptance Criteria**:

      * Frontend sends `GET /recall-last-app`.
      * Backend fetches from `memory_records` where `project_id` = latest project and `metadata->>'step' = 'spec_submitted'`.
      * If found, returns JSON with keys: `project_name`, `description`, `features`, `tech_stack`, `styling`.
      * Frontend populates the form fields accordingly (either via passing props or a callback).
      * If no memory exists, backend returns HTTP 404 with `{ "error": "No previous spec found." }` and frontend displays an error banner.

---

## Epic 2: Template & Tech-Stack Expansion

**Goal**: Add support for multiple “Tech Stack + Styling” combinations and a richer library of code-generation templates.
**Value**: Broaden the appeal beyond just “React + FastAPI + PostgreSQL + Bootstrap.”

### Sprint 2 (2 Weeks) – Expand Templates & Stack Options

**Sprint Objective**

> Enable the generator to handle at least two additional tech-stack combinations (e.g., “Vue + Node.js + MongoDB” and “Next.js + Django + MySQL”), plus conditional prompt branching based on stack.

#### User Stories

1. **US2.1 (Add “Vue + Node.js + MongoDB” Support)**

   * **As a** user,
   * **I want** to select “Vue + Node.js + MongoDB” from the Tech Stack dropdown,
   * **So that** I can get a Vue frontend and Node/Express + Mongoose backend scaffold.
   * **Tasks**:

     1. Create new code-generation templates on AINative for:

        * “vue-component”
        * “express-route”
        * “mongoose-model”
        * “frontend/package.json” and “backend/package.json”
     2. Update `app_generation_plan.txt` to detect `tech_stack == "Vue + Node.js + MongoDB"` and produce a corresponding JSON plan.
     3. Write AINative template variable definitions (e.g., field lists for Mongoose).
     4. Extend `frontend/src/components/SpecForm.jsx` to include the new option.
   * **Acceptance Criteria**:

     * When “Vue + Node.js + MongoDB” is selected, Ollama’s plan includes steps such as:

       ```json
       { "tool":"codegen_create", "input": { "template":"mongoose-model", "file_path":"backend/models/User.js", "variables":{...} } }
       { "tool":"codegen_create", "input": { "template":"express-route", "file_path":"backend/routes/auth.js", "variables":{...} } }
       { "tool":"codegen_create", "input": { "template":"vue-component", "file_path":"frontend/src/components/Login.vue", "variables":{...} } }
       ```
     * Running `/generate-app` with that selection produces a `frontend/` folder containing `.vue` files and `backend/` folder containing `.js`/.
     * The generated `package.json` files install the right dependencies (e.g., `vue`, `mongoose`, `express`).

2. **US2.2 (Add “Next.js + Django + MySQL” Support)**

   * **As a** user,
   * **I want** to select “Next.js + Django + MySQL,”
   * **So that** I can have a Next.js React app (for SSR) and a Django backend with a MySQL schema.
   * **Tasks**:

     1. Define AINative templates:

        * `django-model` (fields, MySQL options)
        * `django-viewset` or `django-rest-route`
        * `next-page` (React + SSR)
        * `next-api-route`
     2. Prompt prompt template: handle `tech_stack == "Next.js + Django + MySQL"`.
     3. Extend `SpecForm.jsx` to include the new option.
   * **Acceptance Criteria**:

     * Ollama’s plan for “Next.js + Django + MySQL” includes appropriate `codegen_create` steps:

       * Create Django models (e.g., `backend/app/models.py`)
       * Create DRF viewsets or URL routes (`backend/app/urls.py`)
       * Create Next.js pages (`frontend/pages/index.jsx`, `frontend/pages/api/notes.js`)
     * The ZIP contains both `frontend/` (Next.js scaffold) and `backend/` (Django app).
     * `requirements.txt` includes `django`, `djangorestframework`, `mysqlclient`.

3. **US2.3 (Dynamic Prompt Branching Based on Stack)**

   * **As a** developer,
   * **I want** the planning prompt to dynamically insert the correct set of templates and file‐paths based on `tech_stack` and `styling`,
   * **So that** Ollama always knows which templates to call.
   * **Tasks**:

     1. Update `app_generation_plan.txt` to include conditional logic (pseudo-instructions) like:

        ```
        If tech_stack == "Vue + Node.js + MongoDB": use templates ["mongoose-model", "express-route", "vue-component"]…
        If tech_stack == "Next.js + Django + MySQL": use templates ["django-model", "django-rest-route", "next-page", "next-api-route"]…
        ```
     2. Incorporate `styling` (e.g., “TailwindCSS” vs. “Bootstrap”) into variable injection.
     3. Test prompts manually by copying from the UI inputs and pasting into Ollama to see a valid JSON plan.
   * **Acceptance Criteria**:

     * For each supported stack, Ollama’s output plan:

       * Lists exactly the correct tools and file-paths (no mixing of React vs. Vue code).
       * Refers to the chosen `styling` (e.g., “Add Tailwind classes to form fields” or “Use Bootstrap classes for buttons”).
     * Automated prompt tests (small script) verify that all branch combinations yield valid JSON.

4. **US2.4 (Front-End Form Enhancements)**

   * **As a** user,
   * **I want** additional dropdown options for `tech_stack` and `styling`,
   * **So that** I can choose from the expanded set without editing code.
   * **Tasks**:

     1. In `SpecForm.jsx`, change the `Tech Stack` `<select>` to accept at least three options (React/Next.js, Vue/Express, etc.).
     2. Change the `Styling` `<select>` to allow (Tailwind, Bootstrap, Plain CSS).
     3. Ensure the form’s `handleGenerate` collects and sends these new values in JSON.
   * **Acceptance Criteria**:

     * The dropdown in the UI now shows “React + FastAPI + PostgreSQL,” “Vue + Node.js + MongoDB,” “Next.js + Django + MySQL.”
     * The `styling` dropdown shows the three options.
     * Inspecting the network call to `/generate-app` confirms the correct JSON keys and values.

5. **US2.5 (Test & Validate New Stacks)**

   * **As a** QA/dev,
   * **I want** to run `/generate-app` for each new stack with a minimal set of features (e.g., only “User login”),
   * **So that** I can validate the generated scaffolds compile (or at least the directories/files exist).
   * **Tasks**:

     1. For each stack, run `/generate-app` with a short spec.
     2. Unzip the returned ZIP, inspect file paths.
     3. On the host machine, spin up the generated apps (e.g., `cd backend && pip install … && uvicorn main:app`).
     4. Confirm no syntax errors in generated code.
   * **Acceptance Criteria**:

     * For “Vue + Node.js + MongoDB,” `frontend/package.json` and `backend/package.json` install without NPM/Yarn errors; `mongoose` schema file exists.
     * For “Next.js + Django + MySQL,” `backend/requirements.txt` installs `django`; `frontend/` builds with `npm run build`.
     * Any compile error or missing file is logged as a defect for later sprints.

#### Sprint 2 Conclusion

By the end of Sprint 2, the system should support at least three distinct tech-stack combinations (React/Flutter alternative optional), dynamic Ollama prompt branching, and a UI form that fully reflects them. Users can generate scaffolds for any supported stack, download a ZIP, and recall their last spec.

---

## Epic 3: Multi-Agent Orchestration & Parallelism

**Goal**: Introduce true multi-agent workflows by leveraging AINative’s `/agent/coordination` endpoints. This allows parallel or staged execution of tasks (e.g., “DB Schema Agent” → “Backend Agent” → “Frontend Agent” → “Styling Agent”).
**Value**: Improve performance (parallelize independent tasks) and demonstrate more advanced orchestration patterns.

### Sprint 3 (2 Weeks) – AINative Coordination Integration

**Sprint Objective**

> Replace the single Ruby-thinking loop with a coordinated, multi-agent flow: submit a “sequence” to AINative, let each agent run in parallel, collect results via webhooks or polling, and aggregate.

#### User Stories

1. **US3.1 (Define Agent Roles & Sequences)**

   * **As a** architect,
   * **I want** to design a “sequence definition” JSON that identifies the set of agents (e.g., `DBSchemaAgent`, `BackendAgent`, `FrontendAgent`, `StylingAgent`) and their inter-dependencies,
   * **So that** I can submit a single `/agent/coordination/sequences` request.
   * **Tasks**:

     1. Review AINative’s Coordination API docs.
     2. Draft a sample “sequence” payload (in `backend/prompts/coordination_sequence_template.json`), e.g.:

        ```json
        {
          "agents": ["DBSchemaAgent", "BackendAgent", "FrontendAgent", "StylingAgent"],
          "workflow": [
            { "agent": "DBSchemaAgent", "action": "generate_models", "depends_on": [] },
            { "agent": "BackendAgent", "action": "generate_routes", "depends_on": ["DBSchemaAgent"] },
            { "agent": "FrontendAgent", "action": "generate_components", "depends_on": ["BackendAgent"] },
            { "agent": "StylingAgent", "action": "apply_styles", "depends_on": ["FrontendAgent"] }
          ],
          "metadata": { "project_id": "{project_id}", "project_name": "{project_name}" }
        }
        ```
     3. Document each agent’s “capabilities” (i.e., which templates they call).
   * **Acceptance Criteria**:

     * A JSON template exists that enumerates `agents`, `workflow` steps, and dependencies.
     * The template references placeholders (`{project_id}`, `{project_name}`) that can be programmatically replaced.
     * A short README in `backend/coordination/README.md` explains how to define new sequences.

2. **US3.2 (Submit Coordination Sequence & Polling)**

   * **As a** developer,
   * **I want** the backend to call `POST /api/v1/agent/coordination/sequences` with the filled-in sequence JSON (replacing placeholders),
   * **So that** AINative begins multi-agent execution.
   * **Tasks**:

     1. Extend `tools/coordination_tool.py` to wrap:

        * `POST /api/v1/agent/coordination/sequences`
        * `POST /api/v1/agent/coordination/sequences/{seq_id}/execute`
        * `GET /api/v1/agent/coordination/tasks/{task_id}` (to poll status)
     2. Inside `/generate-app`, after inserting `generation_steps`, call `coord_tools.create_sequence(filled_template)` → return `sequence_id`.
     3. Call `coord_tools.execute_sequence(sequence_id)`, then poll all tasks until they reach `status: completed` or `failed`.
   * **Acceptance Criteria**:

     * `coordination_tool.create_sequence(...)` returns a valid `sequence_id`.
     * Immediately after, `coordination_tool.execute_sequence(sequence_id)` returns a 200 OK.
     * Polling each `GET /coordination/tasks/{task_id}` eventually yields `status: completed`.
     * Backend logs a summary of each agent’s `result` in `logs`.

3. **US3.3 (Agent-Level Implementations)**

   * **As a** developer,
   * **I want** to create LangChain “sub-agents” that correspond to each role (DBSchemaAgent, BackendAgent, FrontendAgent, StylingAgent),
   * **So that** when a task is dispatched to AINative, my code can “pick up” the task details and invoke the right AINative tool(s).
   * **Tasks**:

     1. Define 4 LangChain agents (Python classes or prompt templates) that know:

        * Which AINative templates to invoke (e.g., `DBSchemaAgent` calls `codegen_create` with `template="sqlalchemy-model"` or `template="mongoose-model"` depending on stack).
        * How to parse incoming “task input” and produce a JSON output (or write code to disk).
     2. Implement a simple “worker” loop or FastAPI webhook (e.g., `POST /coord-task-callback`) that AINative can call when a task is complete.
     3. If webhooks are not possible, implement a poller thread (in the backend) that hits `GET /coordination/tasks/{task_id}` until `status` flips to `completed`, then calls the appropriate agent logic.
   * **Acceptance Criteria**:

     * Four agent classes exist under `backend/agents/`:

       * `db_schema_agent.py`, `backend_agent.py`, `frontend_agent.py`, `styling_agent.py`.
     * Each agent can accept a “task payload” JSON (containing `file_path`, `variables`) and invoke the correct wrapper(s) to write code.
     * When AINative posts to `/coord-task-callback`, the payload arrives and the correct agent runs.
     * `logs` are inserted for each agent’s activity.

4. **US3.4 (Parallel Execution Validation)**

   * **As a** QA/dev,
   * **I want** to generate a simple spec that yields a 4-step sequence, then run the multi-agent flow and confirm that at least two non-dependent agents run concurrently,
   * **So that** I know parallelism is working.
   * **Tasks**:

     1. Create a spec with:

        * DB models
        * Backend routes
        * Frontend components
        * Styling
     2. Confirm that—once `sequence.execute()` is called—AINative spawns tasks for `DBSchemaAgent` and `FrontendAgent` at the same time (if neither depends on each other).
     3. Show in `logs` that the timestamp for “DBSchemaAgent started” and “FrontendAgent started” overlap.
   * **Acceptance Criteria**:

     * Two distinct tasks have “status=running” simultaneously when polled.
     * Corresponding code files appear (e.g., `backend/app/models.py` and `frontend/src/components/Login.jsx`) with correct timestamps.
     * No deadlocks or infinite waits.

5. **US3.5 (Fall-Back to Single-Agent Mode)**

   * **As a** developer,
   * **I want** a configuration flag (`USE_COORDINATION=false`) that reverts to the old single-loop execution (execute step-by-step sequentially),
   * **So that** I can quickly switch back if Coordination API is down or misbehaving.
   * **Tasks**:

     1. Add an environment variable `USE_COORDINATION` (default `true`).
     2. In `/generate-app`, wrap the multi-agent logic in `if USE_COORDINATION: … else: run sequential_loop()`.
     3. Write a shell test to set `USE_COORDINATION=false` and confirm sequential loop takes over.
   * **Acceptance Criteria**:

     * If `USE_COORDINATION` is unset or `true`, the code runs multi-agent flow.
     * If `USE_COORDINATION=false`, the code runs the old “call each tool in sequence” loop.
     * No errors or side effects in either mode.

#### Sprint 3 Conclusion

At the end of Sprint 3, the generation path is fully multi-agent. AINative’s coordination engine powers parallel execution of agents (DBSchema, Backend, Frontend, Styling). A fallback to sequential mode is available for reliability. QA has validated parallel task execution.

---

## Epic 4: Advanced Browser UI & Developer Experience

**Goal**: Elevate the front-end beyond a simple form–log view. Introduce drag-and-drop component placement, live preview, and per-component customization.
**Value**: Dramatically improve UX and allow non-technical users to “visualize” their app before downloading code.

### Sprint 4 (2 Weeks) – Drag-&-Drop Canvas + Live Preview

**Sprint Objective**

> Build a richer front-end that lets users place “login form,” “task list,” “dashboard” components on a canvas; generate a preview of the UI server-side; and allow per-component parameter tweaks before final generation.

#### User Stories

1. **US4.1 (Drag-and-Drop Component Palette)**

   * **As a** user,
   * **I want** a “Component Palette” sidebar listing “Login Form,” “Notes List,” “Note Editor,” “Dashboard,”
   * **So that** I can drag a component onto a “Canvas” area to visually sketch my app’s UI.
   * **Tasks**:

     1. Research a lightweight drag-&-drop library (e.g., `react-dnd`).
     2. Create a `ComponentPalette` React component listing available components with icons.
     3. Create a `Canvas` React component that accepts drop events and spawns draggable “widgets” (e.g., `<LoginWidget />`).
     4. Maintain a front-end state array `selectedComponents = [{ type: "LoginForm", x:50, y:80 }, …]`.
     5. Write CSS to position these widgets absolutely inside the canvas.
   * **Acceptance Criteria**:

     * User can drag “Login Form” from the palette into the canvas.
     * A draggable “LoginForm” placeholder appears at the drop location.
     * The state `selectedComponents` correctly captures the component’s type and coordinates.
     * The UI does not break on multiple drags/drops.

2. **US4.2 (Per-Component Configuration Panel)**

   * **As a** user,
   * **I want** to click a component in the canvas and see a small modal or side panel where I can rename fields (e.g., “Username” → “Email Address”),
   * **So that** I can customize labels and field names before code generation.
   * **Tasks**:

     1. When a widget on the canvas is clicked, open a `ComponentConfigModal` that lists configurable props (label text, placeholder, validation rules).
     2. Store these props in `state.componentConfigs = { <uniqueId>: { label1:"Username", fieldType1:"string" }, … }`.
     3. Update the preview (in US4.3) to reflect new labels.
   * **Acceptance Criteria**:

     * Clicking a “LoginForm” widget opens a modal with inputs for “Username Label” and “Password Label.”
     * Changing those inputs updates `componentConfigs[widgetId]` in real time.
     * Closing the modal persists the new config.

3. **US4.3 (Live Preview Rendering)**

   * **As a** user,
   * **I want** to see a live preview (client-side) of how my combined components will look (html/css) based on the current canvas layout and configs,
   * **So that** I have immediate visual feedback before generating code.
   * **Tasks**:

     1. For each `selectedComponents[i]`, map to a React “Preview” component (`<LoginPreview config={…} />`).
     2. Render all preview components inside a styled container (mimicking a mobile or desktop viewport).
     3. Use the selected styling framework (Tailwind/Bootstrap) CSS classes in the preview.
     4. On any config change, re-render the preview.
   * **Acceptance Criteria**:

     * Placing “LoginForm” + “NotesList” into the canvas automatically shows a preview mode below or beside the canvas (not actual code, but styled HTML).
     * Modifying “Username Label” changes the label text in the preview.
     * The preview uses the correct styling library (Tailwind vs. Bootstrap) based on the form’s `styling` selection.

4. **US4.4 (Save/Load Canvas Layout)**

   * **As a** user,
   * **I want** to save my current canvas layout and component configs into localStorage,
   * **So that** if I accidentally reload or navigate away, I can restore my work.
   * **Tasks**:

     1. On every major state change (`selectedComponents` or `componentConfigs`), serialize to `localStorage.setItem("canvasState", JSON.stringify(...))`.
     2. On component mount, if `localStorage.canvasState` exists, parse and restore `selectedComponents` & `componentConfigs`.
     3. Provide a “Reset Canvas” button to clear both state and storage.
   * **Acceptance Criteria**:

     * Dragging two widgets and configuring them, then refreshing the browser, restores both the widgets and their custom labels.
     * Clicking “Reset Canvas” clears the canvas and localStorage.

5. **US4.5 (Integrate Canvas Into `/generate-app` Payload)**

   * **As a** developer,
   * **I want** the final `/generate-app` request to include an additional field “canvasLayout” (JSON array of component types, positions, and configs),
   * **So that** the backend can decide which code templates to invoke for each component.
   * **Tasks**:

     1. Modify `SpecForm` (or a wrapper) so that when “Generate App” is clicked, the AJAX payload includes:

        ```json
        {
          "project_name": "...",
          "description": "...",
          "features": [...],
          "tech_stack": "...",
          "styling": "...",
          "canvasLayout": [
            { "type": "LoginForm", "x": 50, "y": 80, "config": { "usernameLabel": "Email" } },
            { "type": "NotesList", "x": 200, "y": 80, "config": { "showTimestamps": true } }
          ]
        }
        ```
     2. Update backend’s `generate_app` handler to accept and store `canvasLayout` in a new `canvas_layout` JSONB column on `projects` (ALTER TABLE).
     3. Modify Ollama planning prompt template to incorporate `canvasLayout` as part of the user spec summary (“We need code for LoginForm with config X, then code for NotesList with config Y”).
   * **Acceptance Criteria**:

     * An AJAX request to `/generate-app` includes `"canvasLayout"` exactly as defined.
     * Backend’s `projects` table now has a `canvas_layout JSONB` column; new row stores the layout.
     * Ollama’s planning prompt (logged for debug) includes a formatted description of each component from `canvasLayout`.

#### Sprint 4 Conclusion

By the end of Sprint 4, users can visually assemble components on a canvas, configure them, and preview their UI in real time. When they click “Generate App,” the backend receives a rich “canvasLayout” that informs Ollama which components to generate. The experience is far more interactive than a simple form.

---

## Epic 5: User Accounts, GitHub Integration & Deployment

**Goal**: Add authentication, per-user project management, and optional “Push to GitHub” so that generated code can live in a user’s repo.
**Value**: Transition from a throwaway POC to something a small team can actually use and version control.

### Sprint 5 (2 Weeks) – Authentication & GitHub Integration

**Sprint Objective**

> Implement user sign-up/sign-in, associate projects with users, allow users to push generated code directly to a GitHub repository (via OAuth).

#### User Stories

1. **US5.1 (User Sign-Up / Login)**

   * **As a** user,
   * **I want** to create an account (via email/password or GitHub OAuth),
   * **So that** I can manage my generated apps and have them tied to my identity.
   * **Tasks**:

     1. Add a new `users` table to Postgres:

        ```sql
        CREATE TABLE users (
          user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          email   TEXT UNIQUE NOT NULL,
          name    TEXT,
          password_hash TEXT,  -- if using email/password
          github_id   TEXT,    -- if using GitHub OAuth
          created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
        ```
     2. Install and configure a simple authentication library in FastAPI (e.g., `fastapi-users` or custom JWT).
     3. Create endpoints:

        * `POST /auth/register` (email + password) → create user + hash password.
        * `POST /auth/login` → verify credentials → return JWT.
        * `GET /auth/github/login` → redirect to GitHub OAuth.
        * `GET /auth/github/callback` → receive code → exchange for access token → fetch user info → create or fetch `users` row.
     4. Protect `/generate-app` and `/recall-last-app` behind authentication (anti-CSRF, JWT).
   * **Acceptance Criteria**:

     * A new user can `POST /auth/register` with `{ email, password, name }` and get a success.
     * That user can `POST /auth/login` with their credentials and receive a valid JWT.
     * Requests to `/generate-app` without a valid `Authorization: Bearer <token>` are rejected with 401.
     * GitHub OAuth flow: user clicks “Login with GitHub,” is redirected back, and a `users` row with `github_id` exists.

2. **US5.2 (Associate Projects with Users)**

   * **As a** user,
   * **I want** my generated apps to appear in a personal “Dashboard,”
   * **So that** I can revisit or regenerate them.
   * **Tasks**:

     1. Alter `projects` table to add `user_id UUID REFERENCES users(user_id)`.
     2. In `/generate-app`, after verifying JWT, extract `user_id` and insert it when creating `projects`.
     3. Create endpoint `GET /user/projects` that returns a list of `{ project_id, project_name, status, created_at, download_url }` for the current user.
     4. Update frontend:

        * After login, redirect to `/dashboard`.
        * On `/dashboard`, fetch `GET /user/projects` and display a list.
        * Provide buttons for each: “Download ZIP” or “Regenerate” (pre-fills form).
   * **Acceptance Criteria**:

     * Running `GET /user/projects` with a valid JWT returns only that user’s projects in JSON.
     * The UI’s Dashboard shows each project’s name (clickable), status, and a link to “Download” if `status == SUCCESS`.
     * The “Regenerate” button triggers a new `/generate-app` with the same spec (using `canvas_layout` from the existing `projects` row).

3. **US5.3 (GitHub Push Integration)**

   * **As a** user,
   * **I want** to (optionally) push my generated code to a new GitHub repository under my account,
   * **So that** I can immediately have a hosted codebase (and share or collaborate).
   * **Tasks**:

     1. Add a “Push to GitHub” checkbox in the front-end form (below “Styling”).
     2. If selected, flow in the frontend:

        * On login (if via GitHub OAuth), store the user’s GitHub access token (in session/localStorage).
        * When generating the code, after ZIP creation, clone or create a new repo under the user’s GitHub account via GitHub’s REST API:

          * `POST https://api.github.com/user/repos` with `{ "name": "QuickNotes-<timestamp>" }` → returns `clone_url`.
          * Extract `clone_url` (HTTPS) and run a subprocess:

            ```bash
            git init
            git remote add origin <clone_url>
            git add .
            git commit -m "Initial commit"
            git push -u origin main
            ```
        * Capture the new GitHub repo URL (e.g., `https://github.com/<username>/QuickNotes-…`) and return it in the response JSON.
     3. Persist `projects.github_url` in the `projects` table.
   * **Acceptance Criteria**:

     * When “Push to GitHub” is checked and the user has a valid GitHub OAuth token, backend:

       1. Creates a new GitHub repo under the user’s account with the name `<project_name>-<unique>`.
       2. Pushes the generated code to `main` branch.
       3. Returns JSON `{ "github_url": "https://github.com/<username>/QuickNotes-…" }`.
     * In the Dashboard, each project row now shows a “View on GitHub” link if `github_url` is not null.

4. **US5.4 (Email Notifications on Completion)**

   * **As a** user,
   * **I want** to optionally receive an email when my app generation completes (especially for large specs),
   * **So that** I don’t have to continuously watch the status panel.
   * **Tasks**:

     1. Add a checkbox “Notify me by email when complete” in the UI (only visible if user has email on record).
     2. Add a new boolean column in `projects`: `email_notify` (default false).
     3. In `/generate-app`, if `email_notify = true`, store `true` in the `projects` row.
     4. After `projects.status` is updated to `SUCCESS` or `FAILED`, enqueue an email (using a simple SMTP library like `smtplib` or a service like SendGrid) to the user’s email.
     5. The email body:

        ```
        Subject: Your App “<project_name>” is Ready

        Hi <user_name>,

        Your app “<project_name>” has finished generating.

        • Status: SUCCESS  
        • Download here: http://<host>/downloads/<project_name>.zip  
        • (If GitHub push enabled) View on GitHub: <github_url>

        Thanks for using App Generator!
        ```
     6. Log email success/failure in a new table `email_logs (email_log_id, project_id, status, error_message, created_at)`.
   * **Acceptance Criteria**:

     * When `email_notify` is true, backend sends exactly one email to `users.email` upon generation completion.
     * An `email_logs` row is inserted with `status='SENT'` or `status='FAILED'`.
     * If email fails (e.g., SMTP error), the failure is recorded and the user sees a “Email notification failed” entry in `logs`.

#### Sprint 5 Conclusion

By the end of Sprint 5, each user can log in, see their personal dashboard of generated apps, push code to GitHub, and get email alerts upon completion. The POC is now a bona fide multi-tenant code-generator service rather than a single user demo.

---

## Epic 6: Monitoring, Scalability & Production Hardening

**Goal**: Prepare the system for low-volume production usage: Dockerization, metrics/monitoring, automated cleanup of old temp folders, rate limiting, and performance optimizations.
**Value**: Ensure reliability, observability, and maintainability as usage grows.

### Sprint 6 (2 Weeks) – Production Readiness

**Sprint Objective**

> Containerize the full stack, add logging/metrics, implement a scheduled cleanup of temporary projects, enforce API rate limits, and optimize Ollama/DB usage.

#### User Stories

1. **US6.1 (Dockerize Backend, Frontend & Ollama)**

   * **As a** DevOps engineer,
   * **I want** to build Docker images for:

     1. FastAPI backend (including tool wrappers, DB client, Ollama client)
     2. React frontend (static build)
     3. Ollama LLM server (using the official Ollama Docker base, if available)
   * **So that** I can deploy all services consistently in containers.
   * **Tasks**:

     1. **Dockerfile (backend/Dockerfile)**:

        ```dockerfile
        FROM python:3.9-slim
        WORKDIR /app
        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt
        COPY . .
        EXPOSE 8000
        CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
        ```
     2. **Dockerfile (frontend/Dockerfile)**:

        ```dockerfile
        FROM node:16-alpine AS builder
        WORKDIR /app
        COPY package.json yarn.lock ./
        RUN yarn install
        COPY . .
        RUN yarn build

        FROM nginx:alpine
        COPY --from=builder /app/build /usr/share/nginx/html
        EXPOSE 80
        # NGINX config if needed
        CMD ["nginx", "-g", "daemon off;"]
        ```
     3. **Docker Compose** `docker-compose.yml` orchestrating:

        * `ollama-server` (image: `ollama/ollama:latest`, environment to load `vicuna-13b`)
        * `postgres` (13-alpine)
        * `backend` (build from `backend/`)
        * `frontend` (build from `frontend/`)
        * Network port mapping:

          * `frontend:80 → host:3000`
          * `backend:8000 → host:8000`
          * `ollama-server:11434 → host:11434`
     4. Test `docker-compose up --build` and confirm:

        * `http://localhost:11434` responds to Ollama liveness.
        * `http://localhost:8000/docs` shows FastAPI Swagger UI.
        * `http://localhost:3000` shows the React UI.
   * **Acceptance Criteria**:

     * All services run in isolation, with no “works on my machine” issues.
     * No host Python or Node.js installation is required to run the stack—just Docker.
     * The React UI can call the backend via the internal Docker network (`http://backend:8000`).

2. **US6.2 (Auto-Cleanup of Temporary Projects)**

   * **As a** developer,
   * **I want** a scheduled job (cron or background worker) that deletes `temp_projects/<project_id>` folders older than 24 hours,
   * **So that** disk usage remains under control.
   * **Tasks**:

     1. Write a small Python script `backend/cleanup_temp_projects.py` that:

        ```python
        import os, time, shutil

        BASE = "temp_projects"
        THRESHOLD = 24 * 3600  # 24 hours in seconds
        now = time.time()
        for folder in os.listdir(BASE):
            full_path = os.path.join(BASE, folder)
            if os.path.isdir(full_path):
                mtime = os.path.getmtime(full_path)
                if (now - mtime) > THRESHOLD:
                    shutil.rmtree(full_path)
                    print(f"Deleted {full_path}")
        ```
     2. Add a scheduled cron entry (in Docker Compose or on the host) to run this script every hour.
     3. Update `backend/main.py` logs to indicate when a cleanup occurs and how many folders were removed.
   * **Acceptance Criteria**:

     * After creating a dummy directory under `temp_projects/` with a modified `mtime` older than 24 hours, running the script removes it.
     * Checking the logs shows “Deleted temp\_projects/<project>”.
     * No accidental deletion of folders less than 24 hours old.

3. **US6.3 (Metrics & Monitoring)**

   * **As a** devops/dev,
   * **I want** to expose Prometheus-style metrics (e.g., request counts, latencies, Ollama token usage, AINative API call counts),
   * **So that** I can build a Grafana dashboard showing system health.
   * **Tasks**:

     1. In `backend/main.py`, install and configure `fastapi-prometheus` or `prometheus_fastapi_instrumentator`:

        ```python
        from prometheus_fastapi_instrumentator import Instrumentator
        instrumentator = Instrumentator()
        instrumentator.instrument(app).expose(app)
        ```
     2. Instrument:

        * HTTP request count and latency for each endpoint (`/generate-app`, `/recall-last-app`).
        * A custom counter for each AINative tool invocation (e.g., `codegen_create_calls_total`).
        * A gauge for “number of projects in IN\_PROGRESS” status.
     3. Run a local Prometheus container that scrapes `http://localhost:8000/metrics`.
     4. Create a bare-bones Grafana dashboard with panels:

        * Request rate (per endpoint)
        * 95th percentile latency for `/generate-app`
        * AINative tool call counts
   * **Acceptance Criteria**:

     * Visiting `http://localhost:8000/metrics` shows Prometheus text format metrics.
     * Prometheus can scrape those metrics without error.
     * Grafana panels visualize real-time data for at least one hour.
     * Alerts (optional) can be set for error rate > 5% or latency > 15 s.

4. **US6.4 (API Rate Limiting & Throttling)**

   * **As a** developer,
   * **I want** to enforce a per-user or global rate limit on `POST /generate-app` (e.g., max 5 calls per minute),
   * **So that** the system does not get overwhelmed and AINative costs are controlled.
   * **Tasks**:

     1. Install `slowapi` (FastAPI rate limiting) or write a simple in-memory/Redis counter.
     2. Configure a rule:

        ```python
        from slowapi import Limiter
        limiter = Limiter(key_func=get_remote_address)
        app.state.limiter = limiter

        @app.post("/generate-app")
        @limiter.limit("5/minute")
        async def generate_app(...):
            ...
        ```
     3. Return HTTP 429 “Too Many Requests” if rate limit exceeded.
     4. Document the policy in README (e.g., “Max 5 generations/min”).
   * **Acceptance Criteria**:

     * Sending 6 rapid `POST /generate-app` requests from the same IP (without valid JWT) yields HTTP 429 on the 6th.
     * Headers include `Retry-After: X`.
     * After 1 minute, the user can again call the endpoint.

5. **US6.5 (Performance Tuning & Ollama Resource Management)**

   * **As a** devops/LLM engineer,
   * **I want** to minimize Ollama’s memory footprint (e.g., swap to `vicuna-7b` for planning) and configure a GPU if available,
   * **So that** the service can handle multiple concurrent requests with minimal latency.
   * **Tasks**:

     1. Benchmark `vicuna-13b` vs. `vicuna-7b` on a sample planning prompt; measure 95th percentile latency.
     2. If `vicuna-7b` is acceptable (< 5 s for planning), change default model in `ollama = Ollama(...)` to `vicuna-7b`.
     3. If a GPU is available, confirm Ollama is using GPU (monitor `nvidia-smi`).
     4. Tune `temperature` and `max_tokens` settings to reduce token usage (and cost) while maintaining plan correctness.
   * **Acceptance Criteria**:

     * With `vicuna-7b`, planning `<100 tokens>` JSON runs in < 4 s.
     * A simple load test (10 concurrent `/generate-app` calls) shows < 15 s 95th percentile planning latency.
     * Ollama logs confirm GPU utilization (if applicable).
     * Token usage (from AINative) is tracked and reported in metrics.

#### Sprint 6 Conclusion

By the end of Sprint 6, the stack is Dockerized, networked, and production-ready for low-volume usage. Automated cleanup ensures disk hygiene, metrics and rate-limiting guard against abuse, and performance tuning ensures responsive UX. The “App Generator” is now a robust microservice.

---

## Epic 7: Extensibility, Documentation & Knowledge Transfer

**Goal**: Produce comprehensive documentation, examples, and onboarding guides so that new engineers can extend the system (add stacks, templates, or agent roles) without friction.
**Value**: Ensure the project does not rely on tribal knowledge and can scale beyond initial developers.

### Sprint 7 (1 Week) – Documentation & Example Extensions

**Sprint Objective**

> Write thorough docs (in Markdown/Notion): architecture diagrams, how to add a new tech stack, how to create AINative templates, and a “Hello World” example for multi-agent coordination.

#### User Stories

1. **US7.1 (Architecture & Onboarding Guide)**

   * **As a** new engineer,
   * **I want** a top-level README (or Notion page) that describes:

     1. High-level data flow (diagram + text).
     2. How to spin up the stack (prerequisites, Docker Compose, environment vars).
     3. How to run a basic smoke test.
   * **Acceptance Criteria**:

     * README includes a “Quickstart” section:

       1. `git clone … && cd <repo>`
       2. `docker-compose up --build`
       3. Visit `http://localhost:3000`.
       4. Fill form, click “Generate App,” download ZIP.
     * Architecture diagram (PNG or ASCII) shows UI → FastAPI → Ollama → AINative → DB.
     * Document environment variables: `AINATIVE_API_KEY`, `OLLAMA_BASE_URL`, `DATABASE_URL`, `USE_COORDINATION`.

2. **US7.2 (Add-a-New-Stack Tutorial)**

   * **As a** new developer,
   * **I want** a step-by-step guide on how to add a “Svelte + Go + PostgreSQL” stack,
   * **So that** I can replicate the process for any future stack.
   * **Acceptance Criteria**:

     * A Markdown doc `docs/adding_new_stack.md` exists with:

       1. Copy-and-paste AINative template definitions for `svelte-component`, `go-route`, `gorm-model`.
       2. How to edit `app_generation_plan.txt` to detect `tech_stack == "Svelte + Go + PostgreSQL"`.
       3. Example of adding `<option>` to the frontend form.
       4. Example “sample spec” JSON for the new stack and expected JSON plan.
     * Following the tutorial verbatim, a new minimal project can be generated with Svelte UI and Go backend.

3. **US7.3 (Multi-Agent Coordination Cookbook)**

   * **As a** developer,
   * **I want** documentation on how to add a new agent role (e.g., “SecurityAgent” that calls a vulnerability scanner) to the coordination workflow,
   * **So that** I can extend the system’s multi-agent capabilities.
   * **Acceptance Criteria**:

     * A Markdown page `docs/coordination_agent_guide.md` exists with:

       1. How to define a new agent in `backend/agents/security_agent.py`.
       2. How to wrap its AINative tool (e.g., `SecurityScanTool`).
       3. How to modify the `coordination_sequence_template.json` to include the new agent and its `depends_on`.
       4. Example of polling webhooks or using the callback endpoint.
     * A minimal “SecurityAgent” stub is provided that logs “Security scan placeholder.”

4. **US7.4 (API Reference & Tool Wrapper Docs)**

   * **As a** developer,
   * **I want** autogenerated (or manually written) API documentation for all backend endpoints (`/generate-app`, `/recall-last-app`, `/user/projects`, `/auth/*`),
   * **So that** I can quickly see request/response schemas.
   * **Acceptance Criteria**:

     * FastAPI’s Swagger UI (`/docs`) lists every endpoint, its input model, and possible responses.
     * The `backend/tools/` folder has individual README files summarizing each wrapper class’s methods, inputs, and expected outputs.
     * An OpenAPI export (`openapi.json`) is committed to `docs/openapi.json`.

---

## Sprint Schedule Summary

| **Epic**                               | **Sprint** | **Duration** | **Objective**                                                                                                       |
| -------------------------------------- | ---------- | ------------ | ------------------------------------------------------------------------------------------------------------------- |
| **Epic 1: Core App Generator MVP**     | Sprint 1   | 1 Week       | Build end-to-end MVP: Browser form → Ollama plan → AINative codegen → File assembly → ZIP + Recall.                 |
| **Epic 2: Template & Stack Expansion** | Sprint 2   | 2 Weeks      | Add multiple stacks (Vue/Express, Next.js/Django), dynamic prompts, test & validate new scaffolds.                  |
| **Epic 3: Multi-Agent Orchestration**  | Sprint 3   | 2 Weeks      | Integrate AINative Coordination API, define agent roles, parallel execution, fallback to sequential.                |
| **Epic 4: Advanced Browser UI**        | Sprint 4   | 2 Weeks      | Implement drag-&-drop canvas, per-component config, live preview, save/load canvases, feed canvasLayout to backend. |
| **Epic 5: User Accounts & GitHub**     | Sprint 5   | 2 Weeks      | Add login/register (email + GitHub OAuth), per-user project dashboard, push to GitHub, email notifications.         |
| **Epic 6: Production Hardening**       | Sprint 6   | 2 Weeks      | Dockerize all services, metrics, rate limiting, cleanup scripts, performance tuning, logging.                       |
| **Epic 7: Documentation & Training**   | Sprint 7   | 1 Week       | Write comprehensive docs: architecture, “add-a-new-stack” guide, multi-agent cookbook, API reference.               |

---

## Backlog by Epic (In Detail)

Below is a consolidated backlog, grouped by Epic, with associated Sprint assignments and high-level acceptance criteria.

### Epic 1: Core App Generator MVP

| **User Story**                        | **Sprint** | **Estimate** | **Acceptance Criteria (Summary)**                                                                 |
| ------------------------------------- | ---------- | ------------ | ------------------------------------------------------------------------------------------------- |
| US1.1 Environment & Tooling Setup     | Sprint 1   | 0.5 day      | Ollama runs; AINative API key set; Python & Node envs installed.                                  |
| US1.2 Data Model & Database Setup     | Sprint 1   | 1 day        | Four tables exist; can insert/select without errors.                                              |
| US1.3 AINative Tool Wrappers          | Sprint 1   | 1 day        | Classes for codegen\_create, codegen\_refactor, memory\_store, memory\_search; simple tests pass. |
| US1.4 File-Writer Utility             | Sprint 1   | 0.25 day     | `make_dirs` + `write_file` write files to disk correctly.                                         |
| US1.5 Backend Endpoint Skeleton       | Sprint 1   | 1 day        | `/generate-app` & `/recall-last-app` stubs exist; return correct HTTP codes.                      |
| US1.6 Step Insertion & Status Logging | Sprint 1   | 0.75 day     | Ollama plan parsing + insertion into `generation_steps`.                                          |
| US1.7 Execution Loop & File Assembly  | Sprint 1   | 1 day        | Iterate `generation_steps`, call AINative tools, write code to `temp_projects/<project_id>`.      |
| US1.8 ZIP Packaging & Download URL    | Sprint 1   | 0.5 day      | ZIP is created; `projects` row updated; Download link works.                                      |
| US1.9 Status Logging & Streaming      | Sprint 1   | 0.5 day      | Logs inserted into `logs`; `/generate-app` response JSON contains `"logs": [...]`.                |
| US1.10 Recall Last App End-to-End     | Sprint 1   | 0.5 day      | `/recall-last-app` returns last spec JSON; UI pre-fills or logs.                                  |

> **Total MVP Capacity**: \~6.5 days of work if done sequentially; compress to 1 week by overlapping certain tasks (e.g., environment setup + DB migrations can overlap with tool wrapper design).

### Epic 2: Template & Tech-Stack Expansion

| **User Story**                         | **Sprint** | **Estimate** | **Acceptance Criteria (Summary)**                                                                            |
| -------------------------------------- | ---------- | ------------ | ------------------------------------------------------------------------------------------------------------ |
| US2.1 Vue + Node.js + MongoDB Support  | Sprint 2   | 3 days       | Ollama plan uses `mongoose-model`/`express-route`/`vue-component`; generated files exist and compile.        |
| US2.2 Next.js + Django + MySQL Support | Sprint 2   | 3 days       | Ollama plan uses `django-model`/`django-rest-route`/`next-page`/`next-api-route`; generated scaffold builds. |
| US2.3 Dynamic Prompt Branching         | Sprint 2   | 2 days       | `app_generation_plan.txt` handles conditional stacks + styling; all branches yield valid JSON.               |
| US2.4 Front-End Form Enhancements      | Sprint 2   | 1 day        | Dropdown now shows three stacks + three styling options; AJAX payload correct.                               |
| US2.5 Test & Validate New Stacks       | Sprint 2   | 1 day        | Each new stack generates a valid ZIP; compilation smoke tests pass.                                          |

> **Total**: \~10 days; collapse to 2 weeks (10 working days) by carefully parallelizing the prompt editing and front-end form work.

### Epic 3: Multi-Agent Orchestration & Parallelism

| **User Story**                               | **Sprint** | **Estimate** | **Acceptance Criteria (Summary)**                                                                                   |
| -------------------------------------------- | ---------- | ------------ | ------------------------------------------------------------------------------------------------------------------- |
| US3.1 Define Agent Roles & Sequences         | Sprint 3   | 2 days       | Coordination JSON template exists; documents agent capabilities.                                                    |
| US3.2 Submit Coordination Sequence & Polling | Sprint 3   | 3 days       | Sequence creation & execute calls succeed; tasks poll to completion.                                                |
| US3.3 Agent-Level Implementations            | Sprint 3   | 4 days       | Four agent classes (`DBSchemaAgent`, `BackendAgent`, `FrontendAgent`, `StylingAgent`) process tasks and write code. |
| US3.4 Parallel Execution Validation          | Sprint 3   | 2 days       | At least two agents run concurrently; logs show overlapping timestamps.                                             |
| US3.5 Sequential Fallback Mode               | Sprint 3   | 1 day        | Setting `USE_COORDINATION=false` reverts to existing sequential loop.                                               |

> **Total**: \~12 days; compress to \~2.5 weeks or push some work into Sprint 4 if needed. For a 2-week window, drop US3.4’s in-depth load testing into Sprint 4.

### Epic 4: Advanced Browser UI & Developer Experience

| **User Story**                            | **Sprint** | **Estimate** | **Acceptance Criteria (Summary)**                                                                            |
| ----------------------------------------- | ---------- | ------------ | ------------------------------------------------------------------------------------------------------------ |
| US4.1 Drag-and-Drop Component Palette     | Sprint 4   | 4 days       | User can drag items from palette into canvas; state updates.                                                 |
| US4.2 Per-Component Configuration Panel   | Sprint 4   | 3 days       | Clicking a widget opens a modal; modifications reflect in state.                                             |
| US4.3 Live Preview Rendering              | Sprint 4   | 4 days       | Canvas + configs render a live preview in chosen styling framework.                                          |
| US4.4 Save/Load Canvas Layout             | Sprint 4   | 2 days       | `localStorage` retains layout across reloads; “Reset Canvas” works.                                          |
| US4.5 Integrate CanvasLayout Into Payload | Sprint 4   | 2 days       | `/generate-app` receives `canvasLayout` JSON; stored in `projects.canvas_layout`; Ollama prompt includes it. |

> **Total**: \~15 days; compress to 3 weeks if necessary, or push US4.4 (save/load) into a half-week stretch.

### Epic 5: User Accounts, GitHub Integration & Deployment

| **User Story**                          | **Sprint** | **Estimate** | **Acceptance Criteria (Summary)**                                                                        |
| --------------------------------------- | ---------- | ------------ | -------------------------------------------------------------------------------------------------------- |
| US5.1 User Sign-Up / Login              | Sprint 5   | 4 days       | `/auth/register` + `/auth/login` + GitHub OAuth work; JWT protection on endpoints.                       |
| US5.2 Associate Projects with Users     | Sprint 5   | 2 days       | `projects.user_id` populated; `/user/projects` returns correct list; UI Dashboard shows user’s projects. |
| US5.3 GitHub Push Integration           | Sprint 5   | 5 days       | “Push to GitHub” creates a new repo, pushes code, returns `github_url`; UI shows link.                   |
| US5.4 Email Notifications on Completion | Sprint 5   | 2 days       | If `email_notify=true`, send one email at completion; record in `email_logs`.                            |

> **Total**: \~13 days; schedule as \~2.5 weeks. If time-boxed to 2 weeks, drop US5.4 to a follow-on mini sprint or allocate only minimal effort (ligthweight SMTP).

### Epic 6: Monitoring, Scalability & Production Hardening

| **User Story**                                        | **Sprint** | **Estimate** | **Acceptance Criteria (Summary)**                                                       |
| ----------------------------------------------------- | ---------- | ------------ | --------------------------------------------------------------------------------------- |
| US6.1 Dockerize Backend, Frontend & Ollama            | Sprint 6   | 4 days       | Dockerfiles + Docker Compose up and run all services; no host dependencies.             |
| US6.2 Auto-Cleanup of Temporary Projects              | Sprint 6   | 2 days       | `cleanup_temp_projects.py` deletes folders older than 24h; scheduled job runs hourly.   |
| US6.3 Metrics & Monitoring                            | Sprint 6   | 4 days       | `/metrics` exposed; Prometheus scrapes; basic Grafana dashboard visualizes key metrics. |
| US6.4 API Rate Limiting & Throttling                  | Sprint 6   | 2 days       | Rate limit 5 gen/min per IP; returns HTTP 429 with `Retry-After`.                       |
| US6.5 Performance Tuning & Ollama Resource Management | Sprint 6   | 3 days       | Switch to `vicuna-7b` (or GPU) for planning; measure 95th percentile < 5 s.             |

> **Total**: \~15 days; compress to \~3 weeks (assuming overlap between Dockerizing and cleanup scripting).

### Epic 7: Extensibility, Documentation & Knowledge Transfer

| **User Story**                          | **Sprint** | **Estimate** | **Acceptance Criteria (Summary)**                                                                     |
| --------------------------------------- | ---------- | ------------ | ----------------------------------------------------------------------------------------------------- |
| US7.1 Architecture & Onboarding Guide   | Sprint 7   | 2 days       | README + diagram + “Quickstart” steps; environment variables documented.                              |
| US7.2 Add-a-New-Stack Tutorial          | Sprint 7   | 2 days       | `docs/adding_new_stack.md` with step-by-step instructions; can follow to generate a new stack.        |
| US7.3 Multi-Agent Coordination Cookbook | Sprint 7   | 2 days       | `docs/coordination_agent_guide.md`; example “SecurityAgent” stub.                                     |
| US7.4 API Reference & Tool Wrapper Docs | Sprint 7   | 2 days       | FastAPI Swagger UI wired; `tools/` folder contains README for each wrapper; `openapi.json` committed. |

> **Total**: \~8 days; compress to \~2 weeks.

---

## Optional Epics / Future Enhancements

Depending on team appetite and user feedback, the following epics can follow after the initial seven:

1. **Epic 8: GraphQL API & Playground**

   * Replace or augment REST endpoints with a GraphQL API, providing a schema for querying projects, steps, logs, and memory.
   * Build a GraphQL Playground so that integrators can run ad hoc queries.

2. **Epic 9: Mobile-Friendly UI & PWA Support**

   * Refactor the front end to be mobile-responsive.
   * Add a Service Worker to make the app a Progressive Web App (offline caching, install-to-home-screen).

3. **Epic 10: Multi-Region & Geo-Routing**

   * Deploy Ollama + AINative proxies in multiple regions (e.g., us-west, us-east) and use a global load balancer to route users to the nearest endpoint for lower latency.

4. **Epic 11: AI-Driven Code Review & Testing**

   * Introduce a “ReviewAgent” that, after code generation, runs linters/formatters and uses a dedicated LLM to produce a high-level code review.
   * Add a “TestGenerationAgent” that writes unit tests for each generated endpoint/component.

5. **Epic 12: Enterprise Features & Compliance**

   * Implement role-based access control (RBAC) with fine-grained permissions (e.g., “Admin”, “Developer”, “Viewer”).
   * Add audit logs and SSO integration (SAML, OIDC).
   * Ensure data is encrypted at rest (e.g., use AWS RDS encryption) and in transit (TLS for all endpoints).

---

## Summary Roadmap

Below is a compact view of how the entire backlog fits into a six-month timeline (assuming 2 week sprints plus a 1 week kickoff/cleanup sprint). Adjust as needed for team size and velocity.

| **Month**  | **Sprint #**           | **Focus**                                                         | **Completion Criteria**                                                                                       |
| ---------- | ---------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Month 1    | Sprint 1 (Week 1)      | **Epic 1** – MVP End-to-End Flow                                  | Browser form → Ollama plan → AINative codegen → file assembly → ZIP + recall.                                 |
|            |                        |                                                                   |                                                                                                               |
| Month 2    | Sprint 2 (Weeks 2–3)   | **Epic 2** – Template & Stack Expansion                           | + Vue/Express + Next.js/Django stacks; dynamic prompt branching; UI selects new options; validates scaffolds. |
|            |                        |                                                                   |                                                                                                               |
|            | Sprint 3 (Weeks 4–5)   | **Epic 3** – Multi-Agent Orchestration                            | AINative coordination integration; agent roles; parallel execution; fallback mode.                            |
|            |                        |                                                                   |                                                                                                               |
| Month 3    | Sprint 4 (Weeks 6–7)   | **Epic 4** – Advanced Browser UI & Dev UX                         | Drag-&-drop canvas; per-component config; live preview; save/load; pass canvasLayout to backend.              |
|            |                        |                                                                   |                                                                                                               |
|            | Sprint 5 (Weeks 8–9)   | **Epic 5** – User Accounts & GitHub Integration                   | OAuth (email + GitHub); per-user dashboard; push to GitHub; email notifications.                              |
|            |                        |                                                                   |                                                                                                               |
| Month 4    | Sprint 6 (Weeks 10–11) | **Epic 6** – Production Hardening & Monitoring                    | Dockerized containers; auto-cleanup; Prometheus/Grafana metrics; rate limiting; performance tuning.           |
|            |                        |                                                                   |                                                                                                               |
|            | Sprint 7 (Week 12)     | **Epic 7** – Documentation & Knowledge Transfer                   | Architecture docs; “Add-a-New-Stack” guide; multi-agent cookbook; API reference.                              |
|            |                        |                                                                   |                                                                                                               |
| Months 5–6 | Optional Sprints       | **Future Epics** – GraphQL, Mobile PWA, Multi-Region, Code Review | Build enhancements based on user feedback; enterprise features; expand to production SaaS.                    |

---

### Notes on Backlog & Sprint Planning

1. **Dependencies & Parallel Work**

   * Many tasks in Epic 2 (e.g., front-end form updates and Ollama prompt adjustments) can run in parallel once the basic MVP is stable.
   * Epics 3 and 4 overlap slightly: multi-agent logic must be stable before feeding “canvasLayout” into it, but UI work can proceed in parallel.

2. **Time Estimates**

   * Individual story estimates assume a mid-level developer with experience in FastAPI, React, LangChain, and AINative.
   * Adjust up or down based on your team’s expertise.
   * Where multiple devs are available, split tasks: e.g., one works on Epics 2 & 3 while another starts Epic 4’s UI tasks.

3. **Definition of Done (DoD)**

   * For every story: code is merged to `main`, tests pass (unit & smoke), relevant database migrations applied, and demo in staging environment.
   * Avoid scope creep by deferring “nice to have” features to subsequent sprints.

4. **Backlog Refinement & Grooming**

   * Before each sprint planning meeting, refine the top stories in the backlog:

     * Revalidate the prompt templates (Ollama’s output can drift over time).
     * Review AINative’s API changes (if any).
     * Ensure the data model is still valid (e.g., if new features require new columns).

5. **Acceptance Testing & QA**

   * At the end of each sprint, conduct a demo:

     * For Epic 1: generate a “Hello World” app, download, inspect files.
     * For Epic 2: generate each supported stack, run minimal smoke tests.
     * For Epic 3: run multi-agent sequence and inspect parallel logs.
     * For Epic 4: build a small UI in the canvas, preview, then generate code.
     * For Epic 5: create two user accounts, generate distinct apps, push to GitHub, receive email.
     * For Epic 6: deploy the Docker stack and storm test with 10 concurrent users, monitor via Grafana.

