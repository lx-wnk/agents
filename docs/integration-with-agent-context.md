# Integration with Agent-Context

This document explains how to use the `ac-agents` plugin together with the [Agent-Context](https://github.com/lx-wnk/Agent-Context) framework.

## Overview

The `ac-agents` plugin provides specialist sub-agents that are **fully decoupled** from `.agent-context/`. Agents detect the tech stack from project manifests and receive project context via the delegating prompt — not by reading layer files directly.

This means:
- The agents work in ANY project, with or without Agent-Context installed
- The orchestrating agent (you, or layer0) controls what context each specialist receives
- Write-coupled agents return `persist:` blocks instead of writing to `.agent-context/` directly

## Delegating to Specialist Agents

### Orchestrator Pattern

When delegating to a specialist agent, inject relevant context from your project's layer files into the prompt:

```
You are being dispatched as [agent-name].

## Project Context

Tech stack: [from layer1]
Key conventions: [from layer2]
Relevant decisions: [from decisions.json]

## Task

[specific task]
```

The specialist does not know about `.agent-context/` — you must provide context explicitly.

### What Context to Include

| Agent         | Inject from               |
| ------------- | ------------------------- |
| `backend`     | layer1 (stack), layer2 (rules), decisions.json (patterns) |
| `frontend`    | layer1 (stack), layer2 (CSS/component conventions)         |
| `testing`     | layer2 (test conventions, QA command)                      |
| `architect`   | layer2 (conventions), decisions.json (existing ADRs)       |
| `review`      | layer2 (coding conventions)                                |
| `concept`     | layer1 (stack), decisions.json (constraints)               |
| `discovery`   | layer1 (stack) — optional                                  |
| `chrome`      | layer1 (local domains/ports)                               |

For `debug`, `analysis`, `performance`, `research`: no structured context injection needed — they work well from the task description alone.

## Persist Block Protocol

Two agents return structured `persist:` blocks instead of writing files directly:

### architect

Returns at the end of its response when a decision should be recorded:

```
persist:
  type: adr
  title: <short decision title>
  context: <why this decision was needed>
  decision: <what was decided>
  consequences: <trade-offs>
```

**Handling it in Agent-Context:**
Append a new entry to `.agent-context/decisions.json` with the fields from the persist block.

### docs

Returns persist blocks for lessons or memory updates:

```
persist:
  type: memory-update
  file: memory/lessons.md
  content: <content to append>
```

**Handling it in Agent-Context:**
Append the content to the specified memory file under `.agent-context/`.

## Layer 0 Integration

In the Agent-Context repo, [`context/layer0-agent-workflow.md`](https://github.com/lx-wnk/Agent-Context/blob/main/context/layer0-agent-workflow.md) — "Delegating to Specialist Agents" section — describes the full protocol for injecting context and consuming persist blocks. Agents installed via the `agents@lx-wnk` plugin are available as subagent types matching the `name:` field in each agent's YAML frontmatter.

## Dispatch Envelope

When dispatching a specialist agent, structure your prompt as a typed envelope for consistent handling:

```json
{
  "agent": "backend",
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "projectContext": {
    "techStack": "PHP 8.3 / Symfony 7 / Doctrine ORM",
    "conventions": "PSR-12, readonly DTOs, additive migrations only",
    "relevantDecisions": ["use Doctrine for all DB queries", "no raw SQL"]
  },
  "task": "Add a POST /api/orders endpoint that creates an order and dispatches an OrderCreated event",
  "constraints": {
    "maxTurns": 30,
    "timeoutMs": 120000
  }
}
```

| Field | Type | Description |
| ----- | ---- | ----------- |
| `agent` | string | Agent name matching the `name:` frontmatter field |
| `correlationId` | string (UUID v4) | Unique ID for tracing this dispatch; echoed in agent response |
| `projectContext` | object | Tech stack, conventions, relevant decisions from layer files |
| `task` | string | The specific task for the agent to complete |
| `constraints` | object | Optional: `maxTurns` (int), `timeoutMs` (int) |

## Response Envelope

Agents that support structured output return a response envelope:

```json
{
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "status": "success",
  "output": "## Implementation Summary\n**Task:** ...",
  "persist": [
    {
      "schemaVersion": 1,
      "type": "memory-update",
      "file": "memory/lessons.md",
      "content": "Symfony Messenger requires explicit transport config..."
    }
  ],
  "confidence": "high",
  "followUps": ["Run integration tests against the orders endpoint", "Update API documentation"]
}
```

| Field | Type | Description |
| ----- | ---- | ----------- |
| `correlationId` | string | Echoed UUID from the dispatch envelope |
| `status` | `success` \| `partial` \| `failed` | Completion status |
| `output` | string | The agent's primary response content |
| `persist` | PersistBlock[] (optional) | Structured persist blocks — see `schemas/persist-block.schema.json` |
| `confidence` | `high` \| `medium` \| `low` | Confidence in the completeness or correctness of the output |
| `followUps` | string[] (optional) | Suggested next actions for the orchestrator |

## Correlation ID Convention

The correlation ID enables request tracing across multi-agent pipelines:

1. **Orchestrator generates** a UUID v4 before dispatching: e.g., `550e8400-e29b-41d4-a716-446655440000`
2. **Pass in prompt** as part of the dispatch envelope (see above)
3. **Agent echoes** the correlation ID as the first line of its response:
   ```
   ## correlationId: 550e8400-e29b-41d4-a716-446655440000
   ```
4. **Orchestrator matches** the ID in the response to the original dispatch for logging and error recovery

This allows pipelines with parallel dispatches to route responses correctly even when agents complete out of order.

## Fallback Hierarchy

When an agent fails or returns `INCOMPLETE`, follow this escalation chain:

### architect fails

1. **Retry once** with the same dispatch envelope (transient failures)
2. **Dispatch `review`** with the same scope + a note that `architect` failed — review can provide structural observations without full design output
3. **Human escalation** — surface both the architect's partial output and the review's observations to the user for a final decision

### General pattern

```
Primary agent → retry once → secondary agent with context note → human escalation
```

- Always include the primary agent's partial output in the secondary dispatch
- Note the failure reason so the secondary agent can calibrate its scope
- Human escalation should include: task, both agent outputs, and a clear question

## Version Compatibility

This plugin is designed to work alongside Agent-Context. When Agent-Context runs its auto-update, it will sync the plugin reference in `plugins.json` but will not overwrite the agents themselves (they live in this separate repo).
