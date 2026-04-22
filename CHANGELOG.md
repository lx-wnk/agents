# Changelog

All notable changes to the ac-agents plugin are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — 2026-04-22

### Changed

#### analysis
- Frontmatter: `name` → `analysis` (removed `ac-` prefix), `model` → `sonnet`, `maxTurns` → 30, added `version: 1.0.0`
- Added `## Workflow` section with `### 1. Load Project Context` (6-step `.agent-context/` fallback chain)
- Added `Done when:` completion markers to all 6 Analysis Types sections
- Added `## When I cannot complete this task` section before `## Rules`
- Added `confidence: high | medium | low` field to `### Summary` in Output Format

#### architect
- Frontmatter: `name` → `architect` (removed `ac-` prefix), added `version: 1.0.0`
- Updated `description` cross-references: `ac-review` → `review`, `ac-analysis` → `analysis`
- Added `schemaVersion: 1` to persist block example

#### backend
- Frontmatter: `name` → `backend`, `model` → `sonnet`, `maxTurns` → 30, added `version: 1.0.0`
- Added `## Core Principle` section: "Implement to the project's existing patterns, not to an ideal."
- Added `### 1. Load Project Context` as first workflow step; renumbered existing steps to 2–6
- Added `Done when:` markers to all 6 workflow steps
- Added `## Output Format` section with Implementation Summary template
- Added `## When I cannot complete this task` section before `## Checklist`

#### chrome
- Frontmatter: `name` → `chrome`, added `version: 1.0.0`
- Added `## Core Principle` section: "One action, one screenshot."
- Added `### 1. Load Project Context` as first workflow step; renumbered existing steps to 2–6
- Added `Done when:` markers to all 6 workflow steps
- Added `## When I cannot complete this task` section

#### concept
- Frontmatter: `name` → `concept`, `model` → `sonnet`, added `version: 1.0.0`
- Added `### 1. Load Project Context` as first workflow step; renumbered existing steps to 2–6
- Added `Done when:` markers to all 6 workflow steps
- Added `## When I cannot complete this task` section before `## Rules`

#### debug
- Frontmatter: `name` → `debug`, `effort` → `xhigh`, added `version: 1.0.0`, added `memory: project`
- Added `## Core Principle` section: "Fix the root cause, not the symptom."
- Added `### 1. Load Project Context` as first workflow step; renumbered existing steps to 2–8
- Added `Done when:` markers to all 8 workflow steps
- Added `## When I cannot complete this task` section
- Added `Confidence: <high | medium | low>` field to Bug Report output header

#### discovery
- Frontmatter: `name` → `discovery`, `model` → `sonnet`, added `version: 1.0.0`
- Added `### Phase 0: Load Project Context` before Phase 1 in methodology
- Added `Done when:` markers to all 5 discovery phases
- Added `## When I cannot complete this task` section before `## Rules`

#### docs
- Frontmatter: `name` → `docs`, added `version: 1.0.0`
- Added `## Core Principle` section: "Document what cannot be discovered from code."
- Added `### 1. Load Project Context` as first workflow step; renumbered existing steps to 2–6
- Added `Done when:` markers to all 6 workflow steps
- Added `## When I cannot complete this task` section before `## Rules`
- Added `schemaVersion: 1` to both persist block examples (memory-update and adr)

#### frontend
- Frontmatter: `name` → `frontend`, `model` → `sonnet`, `maxTurns` → 30, added `version: 1.0.0`, removed `WebSearch` from tools
- Added `### 1. Load Project Context` as first workflow step; renumbered existing steps to 2–6
- Added `Done when:` markers to all 6 workflow steps (replacing existing partial "Step complete when" notes)
- Added `## Output Format` section with Implementation Summary template
- Added `## When I cannot complete this task` section before `## Checklist`

#### performance
- Frontmatter: `name` → `performance`, `effort` → `xhigh`, added `version: 1.0.0`
- Added `### 1. Load Project Context` as first workflow step; renumbered existing steps to 2–7
- Added `Done when:` markers to all 7 workflow steps
- Added `## When I cannot complete this task` section before `## Anti-Pattern Checklist`
- Added `Confidence: <high | medium | low>` field to Performance Audit output header

#### research
- Frontmatter: `name` → `research`, `model` → `sonnet`, added `version: 1.0.0`, added `memory: project`
- Added `### 1. Load Project Context` as first workflow step; renumbered existing steps to 2–5
- Added `Done when:` markers to all 5 workflow steps
- Added `## When I cannot complete this task` section before `## Rules`

#### review
- Frontmatter: `name` → `review`, added `version: 1.0.0`, added `memory: project`
- Added `## Core Principle` section: "Signal over noise."
- Added `### 1. Load Project Context` as first workflow step; renumbered existing steps to 2–5
- Added `Done when:` markers to all 5 workflow steps
- Added `## When I cannot complete this task` section before `## Output Format`
- Added `Confidence: <high | medium | low>` field to Review Summary output header

#### testing
- Frontmatter: `name` → `testing`, added `version: 1.0.0`
- Added `## Core Principle` section: "Tests are specifications, not afterthoughts."
- Added `### 1. Load Project Context` as first workflow step; renumbered existing steps to 2–7
- Added `Done when:` markers to all 7 workflow steps
- Added `## Output Format` section with Testing Summary template
- Added `## When I cannot complete this task` section before `## Checklist`
- Softened language: `it MUST fail` → `it must fail` in TDD step

### Documentation

#### docs/integration-with-agent-context.md
- Updated all `ac-*` agent name references to prefix-free form
- Added `## Dispatch Envelope` section with typed JSON prompt structure and field reference
- Added `## Response Envelope` section with typed JSON response structure referencing `persist-block.schema.json`
- Added `## Correlation ID Convention` — orchestrator generates UUID v4, agent echoes in output header
- Added `## Fallback Hierarchy` — architect fails → retry → review with context → human escalation

#### docs/best-practices-agent-creation.md
- Updated `ac-review` cross-reference to `review`
- Added `## 8. Agent Disambiguation` section with architect/review/analysis/discovery matrix and decision rules

### Infrastructure

#### schemas/persist-block.schema.json (new)
- JSON Schema Draft-07 for persist blocks
- Two typed variants via `oneOf`: `adr` (title, context, decision, consequences) and `memory-update` (file, content)
- Both variants require `schemaVersion: 1` and use `additionalProperties: false`
