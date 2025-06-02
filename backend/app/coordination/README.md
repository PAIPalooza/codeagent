# Multi-Agent Coordination System

This directory contains the multi-agent coordination system for CodeAgent, which orchestrates multiple specialized agents to generate applications in parallel.

## Overview

The coordination system uses a workflow-based approach where different agents handle specific aspects of code generation:

- **DBSchemaAgent**: Generates database models and schema files
- **BackendAgent**: Creates API routes and business logic
- **FrontendAgent**: Generates UI components and views
- **StylingAgent**: Applies styling frameworks and custom styles
- **PackagingAgent**: Creates package files, documentation, and final assembly

## Agent Workflow

The agents follow a dependency-based execution order:

```
DBSchemaAgent (parallel start)
     ↓
BackendAgent (depends on DBSchemaAgent)
     ↓
FrontendAgent (depends on BackendAgent)
     ↓
StylingAgent (depends on FrontendAgent)
     ↓
PackagingAgent (depends on StylingAgent)
```

## Configuration

### sequence_template.json

The main configuration file that defines:

- **agents**: List of available agents
- **workflow**: Execution sequence with dependencies
- **metadata**: Project-specific information (filled at runtime)
- **settings**: Coordination parameters

### Template Placeholders

The following placeholders are replaced at runtime:

- `{project_id}`: Unique project identifier
- `{project_name}`: Project name
- `{tech_stack}`: Selected technology stack
- `{styling}`: Styling framework
- `{features}`: List of requested features
- `{timestamp}`: Current timestamp

## Agent Dependencies

Each workflow step can specify dependencies using the `depends_on` field:

```json
{
  "agent": "BackendAgent",
  "action": "generate_routes",
  "depends_on": ["DBSchemaAgent"],
  "description": "Generate API routes after models are created"
}
```

## Parallel Execution

Agents without dependencies (or whose dependencies are satisfied) can run in parallel. The `max_parallel_agents` setting controls the maximum number of concurrent agents.

## Error Handling

- Failed tasks can be retried based on `retry_failed_tasks` and `max_retries` settings
- Total workflow timeout is controlled by `total_timeout`
- Individual agent timeouts are specified per workflow step

## Adding New Agents

To add a new agent:

1. Create the agent class in `backend/app/agents/`
2. Add the agent to the `agents` list in `sequence_template.json`
3. Define workflow steps that use the agent
4. Implement the agent's callback handling

## Usage

The coordination system integrates with the main app generation flow and can be enabled/disabled via environment variables:

```bash
export USE_COORDINATION=true  # Enable multi-agent mode
export USE_COORDINATION=false # Use single-agent mode (fallback)
```