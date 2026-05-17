# Changelog

All notable changes to the ac-agents plugin are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.1.0] — 2026-05-09

### Added — New Agents

Five new specialist agents based on community consensus (VoltAgent 131+, wshobson 185, contains-studio rosters) and the May 2026 best-practices research.

#### accessibility (new)
- WCAG 2.2 / 3.0 audits, ARIA review, keyboard navigation, screen-reader compatibility
- Tools: `Read, Edit, Glob, Grep, Bash, WebFetch`; `model: sonnet`, `effort: high`
- Core principle: "Semantics first, ARIA second."

#### database (new)
- Schema design, migrations (forward and rollback), indexing, query optimization
- Tools: `Read, Write, Edit, Glob, Grep, Bash, WebFetch`; `model: sonnet`, `effort: high`, `memory: project`
- Core principle: "Migrations are one-way doors until proven otherwise."

#### devops (new)
- CI/CD pipelines (GitHub Actions, GitLab CI), container builds, Kubernetes / Helm, Terraform/Pulumi/OpenTofu
- Tools: `Read, Write, Edit, Glob, Grep, Bash, WebFetch`; `model: sonnet`, `effort: high`, `memory: project`
- Core principle: "Pipelines are code under the same review bar as application code."

#### refactor (new)
- Large-scale refactors, pattern extraction, dead-code removal, modernization
- Tools: `Read, Write, Edit, Glob, Grep, Bash`; `model: opus`, `effort: xhigh`, `memory: project`
- Core principle: "Behavior preservation is the contract."

#### security (new)
- OWASP audits, secret detection, AuthZ/AuthN review, dependency CVE assessment, threat modeling
- Tools: `Read, Glob, Grep, Bash, WebFetch, WebSearch`; `model: opus`, `effort: high`, `memory: project`; read-only
- Core principle: "Exploitability over theory."

### Changed — Scope Splits

Three existing agents narrowed in scope to delegate specialized work to the new agents.

#### backend
- `version`: 1.0.0 → 1.1.0
- Migrations and schema work removed from primary scope; delegate to `database`
- Description and Role updated to reference the delegation
- Implementation conventions section: removed migration-tool guidance per ecosystem

#### frontend
- `version`: 1.0.0 → 1.1.0
- Deep WCAG / ARIA / screen-reader work removed from primary scope; delegate to `accessibility`
- Frontend retains baseline a11y (semantic HTML, keyboard reachability, alt text)
- Description, Role, Quality Gate, and Checklist updated to reference the delegation

#### review
- `version`: 1.0.0 → 1.1.0
- Deep security audits removed from primary scope; delegate to `security`
- Multi-Perspective table: "Security" renamed to "Security triage" with explicit escalation rule
- Description and Role updated to reference the delegation

### Documentation

#### docs/best-practices-agent-creation.md
- §2 Frontmatter Design: rewrite with all 16 official frontmatter fields, grouped by purpose (Identity, Tools, Model & Effort, Permissions & Isolation, Context & Memory, Lifecycle); plugin-agent considerations documented for `mcpServers`, `hooks`, and `permissionMode` (all valid, used with care)
- §4 Context Engineering: added Tool Clearing, Compaction, Memory tool, Context Rot
- §5 Workflow Design: replaced "MCP if available" guidance with `mcpServers` field guidance for non-plugin agents; added Hooks-as-Gates, Worktree Isolation, Background Subagents
- §6 Anti-Patterns: added subagent-nesting, redundant personas, project-MCP-bloat, parallel-writer-races
- NEW §7 Agent Composition Patterns: Planner-Executor-Verifier, Evaluator-Optimizer, Fan-out/Fan-in, Chain-of-Agents, Sequential-vs-Parallel decision
- NEW §8 Skills vs Subagents vs Agent Teams vs Hooks: decision matrix
- §9 Checklist: updated for new frontmatter fields
- §11 Sources: 12 new entries (Anthropic Cookbook context engineering, Agent Teams docs, VoltAgent / wshobson rosters, claudefa.st patterns, 2026 Trends Report)

### Infrastructure

#### README.md
- Agents table: 5 new entries (accessibility, database, devops, refactor, security); 3 updated descriptions (backend, frontend, review)

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
