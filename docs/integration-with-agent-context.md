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

| Agent          | Inject from               |
| -------------- | ------------------------- |
| `ac-backend`   | layer1 (stack), layer2 (rules), decisions.json (patterns) |
| `ac-frontend`  | layer1 (stack), layer2 (CSS/component conventions)         |
| `ac-testing`   | layer2 (test conventions, QA command)                      |
| `ac-architect` | layer2 (conventions), decisions.json (existing ADRs)       |
| `ac-review`    | layer2 (coding conventions)                                |
| `ac-concept`   | layer1 (stack), decisions.json (constraints)               |
| `ac-discovery` | layer1 (stack) — optional                                  |
| `ac-chrome`    | layer1 (local domains/ports)                               |

For `ac-debug`, `ac-analysis`, `ac-performance`, `ac-research`: no structured context injection needed — they work well from the task description alone.

## Persist Block Protocol

Two agents return structured `persist:` blocks instead of writing files directly:

### ac-architect

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

### ac-docs

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

## Version Compatibility

This plugin is designed to work alongside Agent-Context. When Agent-Context runs its auto-update, it will sync the plugin reference in `plugins.json` but will not overwrite the agents themselves (they live in this separate repo).
