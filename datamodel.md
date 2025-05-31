1. **Projects**: each “app generation request” and its metadata.
2. **Generation Steps**: the sequence of tool‐invocation steps produced by Ollama.
3. **Logs**: plain‐text status/log entries for each project (to drive the Status & Logs Panel).
4. **Memory Records**: references to AINative memory entries (spec submissions, final summaries).

All timestamp columns use `TIMESTAMP WITH TIME ZONE` for consistency. Features and any arbitrary JSON inputs/outputs are stored as `JSONB`.

---

## 1. Entity-Relationship Overview

```
┌─────────────────┐       ┌─────────────────────────┐       ┌────────────────┐
│     projects    │1───◄─│   generation_steps     │       │    logs        │
│  (project_id)   │       │   (step_id ... )       │       │   (log_id ...) │
└─────────────────┘       └─────────────────────────┘       └────────────────┘
        ▲                                                        ▲
        │                                                        │
        │                                                        │
        │                                                        │
        │                                                        │
        │                                                        │
        │                                                        │
        │                                                        │
        ▼                                                        ▼
┌────────────────────────┐                                  ┌──────────────────────────┐
│   memory_records       │                                  │        (future)         │
│ (memory_record_id ...) │                                  │   users (if any)        │
└────────────────────────┘                                  └──────────────────────────┘
```

* **projects** ⭆ ←── **generation\_steps** (1\:n)
* **projects** ⭆ ←── **logs** (1\:n)
* **projects** ⭆ ←── **memory\_records** (1\:n)

(User authentication is out of scope for this POC; if added later, you would introduce a `users` table and add a `user_id` FK on `projects`.)

---

## 2. Table Definitions

### 2.1 projects

Stores one row per “app generation request.”

| Column Name         | Data Type                | Constraints                              | Description                                                                                   |
| ------------------- | ------------------------ | ---------------------------------------- | --------------------------------------------------------------------------------------------- |
| project\_id         | UUID                     | PRIMARY KEY, DEFAULT `gen_random_uuid()` | Unique identifier for each project.                                                           |
| project\_name       | TEXT                     | NOT NULL                                 | Name of the app (e.g., “QuickNotes”).                                                         |
| description         | TEXT                     |                                          | Free-text description (e.g., “A simple notes app with user auth and note CRUD.”).             |
| features            | JSONB                    | NOT NULL                                 | Array of feature strings. E.g. `['User login/signup', 'Task CRUD', 'Dashboard view']`.        |
| tech\_stack         | TEXT                     | NOT NULL                                 | Chosen tech stack (e.g., “React + FastAPI + PostgreSQL”).                                     |
| styling             | TEXT                     | NOT NULL                                 | Chosen styling framework (e.g., “TailwindCSS” or “Bootstrap”).                                |
| agent\_id           | TEXT                     | NOT NULL, UNIQUE                         | The Ollama‐generated agent identifier (e.g., “agent-xxxxxxxx”).                               |
| initial\_memory\_id | TEXT                     |                                          | The AINative memory\_id returned when storing the user’s original spec.                       |
| final\_memory\_id   | TEXT                     |                                          | The AINative memory\_id returned when storing the final summary (after generation completes). |
| status              | TEXT                     | NOT NULL, DEFAULT 'IN\_PROGRESS'         | One of {`IN_PROGRESS`, `SUCCESS`, `FAILED`}.                                                  |
| download\_url       | TEXT                     |                                          | Relative URL (e.g., `/downloads/QuickNotes.zip`) for the generated ZIP.                       |
| created\_at         | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT `NOW()`                | Timestamp when the project row was inserted.                                                  |
| updated\_at         | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT `NOW()`                | Timestamp last modified (e.g., status change, URL assigned).                                  |

#### Example

```sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- for gen_random_uuid()

CREATE TABLE projects (
  project_id        UUID                    PRIMARY KEY DEFAULT gen_random_uuid(),
  project_name      TEXT                    NOT NULL,
  description       TEXT,
  features          JSONB                   NOT NULL,
  tech_stack        TEXT                    NOT NULL,
  styling           TEXT                    NOT NULL,
  agent_id          TEXT                    NOT NULL UNIQUE,
  initial_memory_id TEXT,
  final_memory_id   TEXT,
  status            TEXT   CHECK ( status IN ('IN_PROGRESS','SUCCESS','FAILED') ) NOT NULL DEFAULT 'IN_PROGRESS',
  download_url      TEXT,
  created_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

---

### 2.2 generation\_steps

Each row represents a single tool invocation (e.g., “codegen\_create” or “codegen\_refactor”) along the ordered sequence produced by Ollama.

| Column Name     | Data Type                | Constraints                                                   | Description                                                                                                                                |
| --------------- | ------------------------ | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| step\_id        | UUID                     | PRIMARY KEY, DEFAULT `gen_random_uuid()`                      | Unique identifier for this step.                                                                                                           |
| project\_id     | UUID                     | NOT NULL, REFERENCES `projects(project_id)` ON DELETE CASCADE | The project this step belongs to.                                                                                                          |
| sequence\_order | INTEGER                  | NOT NULL                                                      | The 1-based order of execution in the plan (1 → first step, 2 → second, …).                                                                |
| tool\_name      | TEXT                     | NOT NULL                                                      | E.g., `codegen_create`, `codegen_refactor`, or `memory_store`.                                                                             |
| input\_payload  | JSONB                    |                                                               | The exact JSON that was passed to the tool (e.g., `{"template":"react-component", "file_path":"frontend/src/components/Login.jsx", ...}`). |
| output\_payload | JSONB                    |                                                               | The JSON response returned by AINative for this step (e.g., `{"file_path":"frontend/src/components/Login.jsx","code":"<code>..."}`).       |
| status          | TEXT                     | NOT NULL, DEFAULT 'PENDING'                                   | One of {`PENDING`, `SUCCESS`, `FAILED`}.                                                                                                   |
| created\_at     | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW()                                       | Timestamp when this row was created.                                                                                                       |
| updated\_at     | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW()                                       | Timestamp last modified (e.g., status changed to `SUCCESS` or `FAILED`).                                                                   |

#### Example

```sql
CREATE TABLE generation_steps (
  step_id         UUID                    PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id      UUID                    NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
  sequence_order  INTEGER                 NOT NULL,
  tool_name       TEXT                    NOT NULL,
  input_payload   JSONB,
  output_payload  JSONB,
  status          TEXT  CHECK (status IN ('PENDING','SUCCESS','FAILED')) NOT NULL DEFAULT 'PENDING',
  created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

---

### 2.3 logs

A simple append‐only table capturing plain‐text log entries (status updates) for each project. These feed directly into the “Status & Logs Panel” in the browser UI.

| Column Name | Data Type                | Constraints                                                   | Description                                                                            |
| ----------- | ------------------------ | ------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| log\_id     | SERIAL                   | PRIMARY KEY                                                   | Auto-incrementing identifier for each log entry.                                       |
| project\_id | UUID                     | NOT NULL, REFERENCES `projects(project_id)` ON DELETE CASCADE | Which project this log belongs to.                                                     |
| log\_text   | TEXT                     | NOT NULL                                                      | The log or status message (e.g., “Planning…”, “Generated file: frontend/src/App.jsx”). |
| created\_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW()                                       | Timestamp when the log entry was created.                                              |

> **Note:** We use a simple `SERIAL` primary key since these entries are write-heavy and in append order.

#### Example

```sql
CREATE TABLE logs (
  log_id       SERIAL PRIMARY KEY,
  project_id   UUID   NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
  log_text     TEXT   NOT NULL,
  created_at   TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

---

### 2.4 memory\_records

Tracks all AINative “memory” entries associated with a given project. Each row links our local `projects.project_id` to a returned `memory_id` from AINative, plus any associated content or metadata.

| Column Name        | Data Type                | Constraints                                                   | Description                                                                                             |
| ------------------ | ------------------------ | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| memory\_record\_id | UUID                     | PRIMARY KEY, DEFAULT `gen_random_uuid()`                      | Unique identifier for this memory record.                                                               |
| project\_id        | UUID                     | NOT NULL, REFERENCES `projects(project_id)` ON DELETE CASCADE | The project this memory belongs to.                                                                     |
| memory\_id         | TEXT                     | NOT NULL                                                      | The AINative `memory_id` returned by `POST /api/v1/agent/memory`.                                       |
| content            | TEXT                     | NOT NULL                                                      | The raw content string stored (e.g., the JSON-serialized user spec or final summary).                   |
| metadata           | JSONB                    |                                                               | Any metadata passed to AINative (e.g., `{"step":"spec_submitted","timestamp":"2025-05-31T12:00:00Z"}`). |
| created\_at        | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW()                                       | Timestamp when this memory was stored.                                                                  |

#### Example

```sql
CREATE TABLE memory_records (
  memory_record_id  UUID                    PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id        UUID                    NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
  memory_id         TEXT                    NOT NULL,
  content           TEXT                    NOT NULL,
  metadata          JSONB,
  created_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

---

## 3. Example Workflow (Populating the Tables)

1. **User clicks “Generate App”** → Backend receives spec payload:

   ```json
   {
     "project_name": "QuickNotes",
     "description": "A simple notes app with user auth and note CRUD.",
     "features": ["User login/signup", "Task CRUD", "Dashboard view"],
     "tech_stack": "React + FastAPI + PostgreSQL",
     "styling": "Bootstrap"
   }
   ```

2. **Insert into `projects`** (auto-generated `project_id`, `agent_id` = `"agent-xxxx"`, `status` = `"IN_PROGRESS"`):

   ```sql
   INSERT INTO projects (
     project_name, description, features, tech_stack, styling, agent_id
   ) VALUES (
     'QuickNotes',
     'A simple notes app with user auth and note CRUD.',
     '["User login/signup", "Task CRUD", "Dashboard view"]'::JSONB,
     'React + FastAPI + PostgreSQL',
     'Bootstrap',
     'agent-xxxx'
   )
   RETURNING project_id;
   ```

   > Suppose `project_id = 'd1f23a6c-4e5b-4a7d-9c21-2f13afbd9a4e'`.

3. **Store initial memory** (spec submission) via AINative:

   * Call `POST /api/v1/agent/memory` → returns `{ "memory_id": "m123" }`.
   * Insert into `memory_records`:

     ```sql
     INSERT INTO memory_records (project_id, memory_id, content, metadata)
     VALUES (
       'd1f23a6c-4e5b-4a7d-9c21-2f13afbd9a4e',
       'm123',
       '{"project_name":"QuickNotes","description":"A simple notes app with user auth and note CRUD.","features":["User login/signup","Task CRUD","Dashboard view"],"tech_stack":"React + FastAPI + PostgreSQL","styling":"Bootstrap"}',
       '{"step":"spec_submitted","timestamp":"2025-05-31T12:00:00Z"}'::JSONB
     );
     ```

4. **Ollama Planning** → returns JSON array of 8 steps. For each step:

   * **Step 1**:

     ```json
     {
       "tool":"codegen_create",
       "input":{
         "template":"sqlalchemy-model",
         "file_path":"backend/app/models.py",
         "variables":{"model_name":"User","fields":["id:int:primary","email:str:unique","password:str"],"db":"PostgreSQL"}
       }
     }
     ```

     Insert into `generation_steps` (initially `status='PENDING'`):

     ```sql
     INSERT INTO generation_steps (
       project_id, sequence_order, tool_name, input_payload
     ) VALUES (
       'd1f23a6c-4e5b-4a7d-9c21-2f13afbd9a4e',
       1,
       'codegen_create',
       '{"template":"sqlalchemy-model","file_path":"backend/app/models.py","variables":{"model_name":"User","fields":["id:int:primary","email:str:unique","password:str"],"db":"PostgreSQL"}}'::JSONB
     ) RETURNING step_id;
     ```
   * (Repeat for steps 2…8 similarly.)

5. **Execute Step 1** → call AINative’s `POST /api/v1/code-generation/create`. Suppose returns:

   ```json
   {
     "file_path": "backend/app/models.py",
     "code": "from sqlalchemy import Column, Integer, String...\nclass User(Base): ..." 
   }
   ```

   * Update `generation_steps.status='SUCCESS'`, `output_payload` with returned JSON, `updated_at=NOW()`:

     ```sql
     UPDATE generation_steps
       SET output_payload = '{"file_path":"backend/app/models.py","code":"from sqlalchemy ..."}'::JSONB,
           status = 'SUCCESS',
           updated_at = NOW()
     WHERE step_id = '<that_step_id>';
     ```
   * Write the code string to disk at `/tmp/<agent_id>/backend/app/models.py`.
   * Insert a log entry into `logs`:

     ```sql
     INSERT INTO logs (project_id, log_text)
     VALUES (
       'd1f23a6c-4e5b-4a7d-9c21-2f13afbd9a4e',
       'Step 1 (codegen_create): Generated backend/app/models.py'
     );
     ```

6. **Subsequent Steps** (2…7) are handled similarly:

   * For each, insert a `generation_steps` row, invoke the tool, update status, write file, insert a log.

7. **Final Step** (memory\_store summary):

   * AINative returns `{ "memory_id":"m456" }`.
   * Update the corresponding `generation_steps` row.
   * Insert into `memory_records`:

     ```sql
     INSERT INTO memory_records (project_id, memory_id, content, metadata)
     VALUES (
       'd1f23a6c-4e5b-4a7d-9c21-2f13afbd9a4e',
       'm456',
       'Generated QuickNotes: User model, auth routes, notes CRUD, React components, Bootstrap styling.',
       '{"step":"generation_complete","project":"QuickNotes","timestamp":"2025-05-31T12:02:00Z"}'::JSONB
     );
     ```
   * Update `projects.final_memory_id = 'm456'`, `projects.status = 'SUCCESS'`, `projects.updated_at = NOW()`.
   * Zip the `temp_projects/d1f23a6c-.../` folder into `downloads/QuickNotes.zip`.
   * Update `projects.download_url = '/downloads/QuickNotes.zip'`.

8. **Recall Last App**:

   * Backend executes:

     ```sql
     SELECT content, metadata
       FROM memory_records
      WHERE project_id = (
        SELECT project_id 
          FROM projects
         ORDER BY created_at DESC
         LIMIT 1
      )
        AND metadata->>'step' = 'spec_submitted'
      ORDER BY created_at DESC
      LIMIT 1;
     ```
   * Return the `content` JSON back to the browser, which pre-fills the form.

---

## 4. Schema Diagram (Markdown)

```markdown
 #### projects
 ───────────────────────────────────────────────────────────────────────────────
  Column              | Type                               | Constraints
 ───────────────────────────────────────────────────────────────────────────────
  project_id          | UUID                               | PK, DEFAULT gen_random_uuid()
  project_name        | TEXT                               | NOT NULL
  description         | TEXT                               | 
  features            | JSONB                              | NOT NULL
  tech_stack          | TEXT                               | NOT NULL
  styling             | TEXT                               | NOT NULL
  agent_id            | TEXT                               | NOT NULL, UNIQUE
  initial_memory_id   | TEXT                               | 
  final_memory_id     | TEXT                               | 
  status              | TEXT                               | NOT NULL, CHECK IN ('IN_PROGRESS','SUCCESS','FAILED'), DEFAULT 'IN_PROGRESS'
  download_url        | TEXT                               | 
  created_at          | TIMESTAMP WITH TIME ZONE           | NOT NULL, DEFAULT NOW()
  updated_at          | TIMESTAMP WITH TIME ZONE           | NOT NULL, DEFAULT NOW()
 ───────────────────────────────────────────────────────────────────────────────

 #### generation_steps
 ───────────────────────────────────────────────────────────────────────────────
  Column             | Type                               | Constraints
 ───────────────────────────────────────────────────────────────────────────────
  step_id            | UUID                               | PK, DEFAULT gen_random_uuid()
  project_id         | UUID                               | NOT NULL, FK → projects(project_id) ON DELETE CASCADE
  sequence_order     | INTEGER                            | NOT NULL
  tool_name          | TEXT                               | NOT NULL
  input_payload      | JSONB                              | 
  output_payload     | JSONB                              | 
  status             | TEXT                               | NOT NULL, CHECK IN ('PENDING','SUCCESS','FAILED'), DEFAULT 'PENDING'
  created_at         | TIMESTAMP WITH TIME ZONE           | NOT NULL, DEFAULT NOW()
  updated_at         | TIMESTAMP WITH TIME ZONE           | NOT NULL, DEFAULT NOW()
 ───────────────────────────────────────────────────────────────────────────────

 #### logs
 ───────────────────────────────────────────────────────────────────────────────
  Column             | Type                               | Constraints
 ───────────────────────────────────────────────────────────────────────────────
  log_id             | SERIAL                             | PK
  project_id         | UUID                               | NOT NULL, FK → projects(project_id) ON DELETE CASCADE
  log_text           | TEXT                               | NOT NULL
  created_at         | TIMESTAMP WITH TIME ZONE           | NOT NULL, DEFAULT NOW()
 ───────────────────────────────────────────────────────────────────────────────

 #### memory_records
 ───────────────────────────────────────────────────────────────────────────────
  Column             | Type                               | Constraints
 ───────────────────────────────────────────────────────────────────────────────
  memory_record_id   | UUID                               | PK, DEFAULT gen_random_uuid()
  project_id         | UUID                               | NOT NULL, FK → projects(project_id) ON DELETE CASCADE
  memory_id          | TEXT                               | NOT NULL
  content            | TEXT                               | NOT NULL
  metadata           | JSONB                              | 
  created_at         | TIMESTAMP WITH TIME ZONE           | NOT NULL, DEFAULT NOW()
 ───────────────────────────────────────────────────────────────────────────────
```

---

## 5. Additional Notes & Future Extensions

1. **Normalization vs. JSONB**

   * We store `features` and any arbitrary “payloads” as `JSONB` for flexibility.
   * If the set of features becomes large or needs to be queried individually (e.g., “find all projects with feature = 'User login/signup'”), you could extract `features` into a separate `project_features` table:

     ```sql
     CREATE TABLE project_features (
       project_id UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
       feature TEXT NOT NULL,
       PRIMARY KEY (project_id, feature)
     );
     ```
   * For now, storing them as `JSONB` suffices for the POC.

2. **User Accounts (Future)**

   * If “Recall Last App” should be per user rather than global, introduce:

     ```sql
     CREATE TABLE users (
       user_id   UUID   PRIMARY KEY DEFAULT gen_random_uuid(),
       email     TEXT   UNIQUE NOT NULL,
       name      TEXT,
       created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
     );

     -- Add user_id FK to projects
     ALTER TABLE projects
       ADD COLUMN user_id UUID REFERENCES users(user_id) ON DELETE SET NULL;
     ```
   * Adjust all queries to filter by `user_id`.

3. **Indexing & Performance**

   * Add indexes on:

     * `generation_steps(project_id, sequence_order)`
     * `logs(project_id, created_at)`
     * `memory_records(project_id, created_at)`
   * Example:

     ```sql
     CREATE INDEX idx_generation_steps_project_order ON generation_steps (project_id, sequence_order);
     CREATE INDEX idx_logs_project_created ON logs (project_id, created_at DESC);
     CREATE INDEX idx_memory_records_project_created ON memory_records (project_id, created_at DESC);
     ```

4. **Soft Deletes (Future)**

   * If you want to “archive” old projects, add a `deleted_at TIMESTAMP` column to `projects` instead of hard‐deleting (set `deleted_at = NOW()`).
   * Modify queries to include `WHERE deleted_at IS NULL`.

5. **Audit Trail**

   * The `logs` table can be extended to capture:

     * `log_level` (e.g., `INFO`, `WARNING`, `ERROR`)
     * `source` (e.g., `OLLAMA`, `AINATIVE`, `FILE_WRITE`)
   * This improves debugging in production.

---

### 6. Summary

This data model aligns directly with the POC PRD for a Browser-Based App Generator:

* **projects** captures all high-level metadata (app spec, agent IDs, statuses, memory references, download URLs).
* **generation\_steps** records each discrete tool invocation (as orchestrated by Ollama and LangChain), including inputs, outputs, and status.
* **logs** provides an append-only history of status messages for real-time feedback in the UI.
* **memory\_records** tracks AINative memory entries (both initial spec storage and final summary storage), enabling “Recall Last App” functionality.
