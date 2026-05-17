# Best Practices: Agent Creation

This document is the authoritative reference for creating new agents in the Agent-Context project.

---

## 1. Core Principles

### Simplicity First

An agent solves exactly one clearly defined task. If the description requires more than two sentences, the scope is probably too broad.

### Focused Scope

Agents are not general-purpose assistants. The narrower the scope, the more precise the routing and the better the output. Two specialized agents beat one generalist agent.

### Evidence Over Assumption

Agents read project context (`.agent-context/` files, `package.json`, `composer.json` etc.) before making assumptions about the tech stack. Without context, ask or explore — never guess.

---

## 2. Frontmatter Design

### Minimal Example

```yaml
---
name: example
version: 1.0.0
description: "Short description. Delegates here for X, Y, Z. Use when doing A or B."
tools: Read, Glob, Grep, Bash
model: sonnet
maxTurns: 20
effort: medium
---
```

### Field Reference (grouped by purpose)

The official spec lists 16 fields. Group them by purpose to know which apply to which agent type.

#### Identity

| Field         | Description                                                            |
| ------------- | ---------------------------------------------------------------------- |
| `name`        | Kebab-case identifier. No prefix needed when distributed via plugin    |
| `version`     | Semver string. Bump on breaking prompt or contract changes             |
| `description` | Trigger text for automatic routing — see "Description Design" below   |
| `color`       | Optional UI color tag for the agent                                    |

#### Tools

| Field             | Description                                                                                              |
| ----------------- | -------------------------------------------------------------------------------------------------------- |
| `tools`           | Allowlist. Only tools actually needed — no defaults. Omit to inherit all                                 |
| `disallowedTools` | Denylist. Inherits everything except listed tools. Useful when you want broad MCP/Bash access minus edits |

Use `disallowedTools` for read-mostly agents that need many MCP tools — listing all allowed tools is brittle. Use `tools` for write-capable agents where the surface should stay small.

#### Model & Effort

| Field      | Description                                                                  |
| ---------- | ---------------------------------------------------------------------------- |
| `model`    | `opus` / `sonnet` / `haiku` / `inherit` (default). See table below           |
| `effort`   | `low` / `medium` / `high` / `xhigh` / `max` — token budget and reasoning depth |
| `maxTurns` | Realistic ceiling. Too high = runaway costs; too low = premature termination |

#### Permissions & Isolation

| Field            | Description                                                                                          |
| ---------------- | ---------------------------------------------------------------------------------------------------- |
| `permissionMode` | `default` / `acceptEdits` / `auto` / `dontAsk` / `bypassPermissions` / `plan`. Use sparingly in plugin agents — affects user permission UX |
| `isolation`      | `worktree` runs the agent in a temporary git worktree; auto-cleans if no changes. Critical for parallel writers |
| `background`     | `true` for long-running tasks that should not block the main thread                                  |

#### Context & Memory

| Field      | Description                                                                                                       |
| ---------- | ----------------------------------------------------------------------------------------------------------------- |
| `memory`   | `user` / `project` / `local`. Persistent knowledge directory at `~/.claude/agent-memory/`. Enables cross-session learning |
| `skills`   | List of skills to preload into the agent's startup context (different from invoking via the Skill tool at runtime) |
| `initialPrompt` | Auto-submitted first turn when the agent is run as the main agent (e.g. `claude --agent <name>`)             |

#### Lifecycle (advanced)

| Field        | Description                                                                                                    |
| ------------ | -------------------------------------------------------------------------------------------------------------- |
| `mcpServers` | Agent-scoped MCP servers, inline or by reference. Keeps tool descriptions out of the parent context |
| `hooks`      | Subagent-scoped lifecycle hooks (`PreToolUse`, `PostToolUse`, `Stop`, etc.). User-environment concern — declare only when the plugin owns the lifecycle |

### Plugin-Agent Considerations

All 16 frontmatter fields are technically valid for plugin-distributed agents, but they differ in how cleanly they compose with the user's environment:

- **`mcpServers` is fully supported and recommended** when the agent depends on a specific MCP server. See `agents/chrome.md` for a reference using `claude-in-chrome`. Document the required server in the agent's prose section too, so users know what to install.
- **`hooks`** are user-environment configuration in spirit. Declare them in a plugin agent only when the lifecycle gate is intrinsic to the agent's contract (e.g., a `Stop` hook that the agent itself depends on). For project-wide gates (format-on-save, secret-scan), keep them in the user's `.claude/settings.json`.
- **`permissionMode`** changes the user's permission UX. Use sparingly and only with a clear justification — auto-approving edits in a plugin agent can surprise users.

### Description Design

The `description` is the most important field for automatic routing. The text must clearly communicate _when_ this agent should be invoked. Phrase it action-oriented — orchestrators match on imperative triggers like "Use proactively after code changes."

**Good:**

```yaml
description: "Backend development specialist. Delegates here for server-side code, APIs, database operations. Use when implementing business logic, creating endpoints, or modifying database schemas."
```

**Bad:**

```yaml
description: "An agent that does backend stuff."
```

Patterns for good descriptions:

- `"<Role>. Delegates here for <task types>. Use when <concrete triggers>."`
- Name concrete keywords that can be matched during routing
- No marketing speak — technical and precise

### Model Selection

| Model    | When to use                                                                 | Cost/Speed                  |
| -------- | --------------------------------------------------------------------------- | --------------------------- |
| `opus`   | Complex reasoning, architecture decisions, multi-perspective analysis        | Slow, expensive             |
| `sonnet` | Well-defined tasks, code generation, documentation                          | Fast, affordable            |
| `haiku`  | Quick read-only tasks, classification, simple lookups                       | Very fast, very affordable  |

Rule of thumb: Choose the weakest model that reliably fulfills the task.

### Tool Minimization

Only declare tools the agent actually uses. Unnecessary tools increase the attack surface and confuse the model.

| Agent Type                       | Typical Tools                                 |
| -------------------------------- | --------------------------------------------- |
| Read-Only (Review, Discovery)    | `Read, Glob, Grep, Bash`                      |
| Development (Backend, Frontend)  | `Read, Write, Edit, Glob, Grep, Bash`         |
| Research                         | `Read, Glob, Grep, Bash, WebFetch, WebSearch` |
| Browser Automation               | `Read, Glob, Grep, Bash, Write` + MCP Tools   |

Only use the `Agent` tool for agents that explicitly dispatch sub-agents (e.g., `review` for parallel review perspectives).

---

## 3. Prompt Structure

### Consistent Sections

All agents follow this basic structure:

```markdown
# <Agent-Name>

<One-liner: role and main task.> Respond in the user's language.

## Role

<Detailed role description with scope>

## Core Principle

**<Core rule in bold.>** <Explanation of why this rule matters.>

## Workflow

### 1. Load Context

### 2. Analysis / Planning

### 3. Execution

### 4. Quality Gate

## Output Format

<Expected output format, with Markdown template if applicable>

## Rules

<Few, hard rules — only what truly needs to be enforced>
```

The sequence Role → Core Principle → Workflow → Output Format → Rules is proven: the model first understands _who_ it is, then _how_ it proceeds, then _what_ it should deliver, then _what never_.

### Affirmative Phrasing

Positive instructions are more precise and are followed better than prohibitions.

**Prefer:**

```markdown
- Use the project's ORM/DAL for all database queries
- Ask for clarification when requirements are ambiguous
```

**Avoid:**

```markdown
- Never use raw SQL unless explicitly required
- Don't guess what the user wants
```

Reserve `NEVER` and `ALWAYS` in uppercase only for hard security rules (e.g., "NEVER modify production data directly"). Aggressive language like "CRITICAL: YOU MUST" reduces output quality — Claude 4.x responds better to calm, factual instructions.

### Consistent Terminology

Use uniform terms within an agent. Do not alternate between "task", "job", "request" — choose one term and stick with it.

---

## 4. Context Engineering

The guiding principle (Anthropic, "Effective Context Engineering for AI Agents", 2025): give the agent the **smallest set of high-signal tokens** that lets it solve the task. Output quality degrades as the context window fills — a phenomenon called **context rot**. The four levers below all serve that one goal.

### Progressive Disclosure

Load context in layers — only what is needed for the current step:

1. Bootstrap context (tech stack, environment) → always load
2. Project rules (conventions, patterns) → load for implementation tasks
3. Domain context (specific modules, decisions) → load on demand

### Just-in-Time Retrieval

Do not load everything upfront. Fetch specialized context files (e.g., `memory/architecture.md`) only when the agent actually needs them. This reduces token consumption and keeps context focused.

### Tool Clearing

Tool descriptions are tokens too. An agent that loads 30 MCP tools at startup pays for all of them on every turn. Use `tools` / `disallowedTools` to scope down, and prefer agent-scoped `mcpServers` over project-level `.mcp.json` for tools that only one agent needs.

### Compaction & Memory

For long-running agents that approach the context limit:

- **Compaction**: summarize earlier turns into a compressed handoff. The harness does this automatically near the limit, but you can trigger it earlier in `Workflow` instructions for predictable behavior.
- **Memory tool / `memory` field**: persist learnings across sessions to `~/.claude/agent-memory/`. Use for stable facts (project conventions, recurring decisions) — not for ephemeral state.

### Graceful Fallback for `.agent-context/` Files

`.agent-context/` files are optional. Agents must handle their absence:

```markdown
### 1. Load Context

- Load `.agent-context/layer1-bootstrap.md` → tech stack, environment
- Load `.agent-context/layer2-project-core.md` → conventions, rules
- If not present: detect tech stack from `package.json`, `composer.json`, `go.mod`, `requirements.txt` etc.
```

No hard errors when files are missing — explore as an alternative.

---

## 5. Workflow Design

### Stopping Conditions

Every workflow step should have a clear completion condition. Agents that don't know when they are done iterate unnecessarily or terminate too early.

Example: "Step is considered complete when all tests are green and the QA command runs without errors."

### Error Recovery

Describe error handling explicitly:

- What to do when a file is not found?
- What to do when a command fails?
- When to ask the user for clarification vs. deciding independently?

### MCP Tool References

For **optional** MCP integrations (the agent works without the server but benefits when present), phrase usage conditionally:

```markdown
Use documentation MCP tools if available (e.g., context7) for framework lookups.
```

For **required** MCP integrations (the agent cannot do its job without the server), hard-scope it via the `mcpServers` frontmatter field — including in plugin-distributed agents. This keeps tool descriptions out of the parent context and makes the requirement explicit:

```yaml
mcpServers:
  - context7
```

Always document the required server in prose at the top of the prompt too (see `agents/chrome.md` for a reference). That way users know what to install before invoking the agent.

### Hooks as Deterministic Gates

Hooks (`PreToolUse`, `PostToolUse`, `Stop`, etc.) execute deterministic shell commands around tool calls. Use them when a check **must** run — e.g., format on save, lint before commit, secret-scan before a Write. For project-wide gates, prefer the user's `.claude/settings.json`; declare hooks in a plugin agent only when the gate is intrinsic to that agent's contract.

### Worktree Isolation for Parallel Writers

When multiple agents may write files in parallel, set `isolation: worktree` so each agent runs in its own temporary git worktree. The harness auto-cleans worktrees with no changes; surviving worktrees return a path and branch the orchestrator can merge. Without isolation, parallel writers race on the same working tree and corrupt each other's diffs.

### Background Subagents

Long-running tasks (large codebase scans, multi-stage builds) should set `background: true`. The orchestrator gets a completion notification instead of blocking — never poll with `sleep`.

---

## 6. Anti-Patterns

### Architecture

| Anti-Pattern                         | Problem                                    | Solution                                  |
| ------------------------------------ | ------------------------------------------ | ----------------------------------------- |
| Multi-agent for simple tasks         | Overhead without added value               | Fewer than 3 tool calls: no sub-agent     |
| Agent as wrapper without own logic   | Unnecessary indirection                    | Implement a direct agent or merge         |
| Scope too broad ("does everything")  | Poor routing, inconsistent output          | Limit scope to one domain                 |
| Subagent spawning subagent           | Not supported — subagents cannot nest      | Use Agent Teams (`SendMessage`) for peer-to-peer coordination |
| Redundant overlapping personas       | Routing confusion, wasted tokens           | Merge or define a sharp disambiguation matrix |
| Project-level MCP for one-agent need | Bloats context for every agent             | Use agent-scoped `mcpServers` (or prose for plugin agents) |
| Parallel writers without isolation   | Worktree races, corrupted diffs            | Set `isolation: worktree` on writers      |

### Instructions

| Anti-Pattern                               | Problem                                | Solution                            |
| ------------------------------------------ | -------------------------------------- | ----------------------------------- |
| Inconsistent terminology                   | Confusion, unpredictable behavior      | One term per concept — consistently |
| Aggressive language ("CRITICAL: YOU MUST") | Reduced output quality                 | Calm, factual phrasing              |
| Contradictory rules                        | Model chooses arbitrarily              | Define explicit priorities          |

### Tools

| Anti-Pattern                         | Problem                                    | Solution                                     |
| ------------------------------------ | ------------------------------------------ | -------------------------------------------- |
| Tool lists too broad                 | Increased attack surface, distraction      | Minimal set per agent type (see §2)          |
| `Write`/`Edit` on read-only agents   | Security risk                              | Explicitly declare only read tools           |
| `Agent` tool without dispatch logic  | Unused overhead                            | Only when sub-agents are actually dispatched |

### Output

| Anti-Pattern                         | Problem                                    | Solution                                        |
| ------------------------------------ | ------------------------------------------ | ----------------------------------------------- |
| No output format defined             | Every run delivers different structure     | Define Markdown template in prompt              |
| Too detailed output for simple tasks | Noise, hard to use                         | Adapt output length to task type                |
| No summary at the end                | User must interpret output themselves      | Always include a short summary of what was done |

---

## 7. Agent Composition Patterns

How agents compose into larger workflows. Pick the pattern that matches the task shape — do not invent ad-hoc orchestration.

### Planner-Executor-Verifier

The orchestrator delegates to a **planner** (read-only, produces a step list), then to one or more **executors** (write-capable, do the work), then to a **verifier** (read-only, confirms outcome). Maps cleanly onto our `discovery` / `architect` → `backend`/`frontend` → `review` chain.

Use when: changes are non-trivial and a wrong plan is expensive to undo.

### Evaluator-Optimizer (judge loop)

Executor produces a candidate output. A **judge** agent rates it against criteria. If the rating is below threshold, the executor revises with the judge's feedback. Three judge tiers (cheapest first):

1. Static checks (lint, types, tests) — free, deterministic
2. LLM-judge — moderate cost, catches style/correctness
3. Sample/Monte-Carlo — expensive, only for high-stakes outputs

Use when: quality is hard to specify upfront but easy to recognize.

### Fan-out / Fan-in (parallel subagents)

Orchestrator spawns N subagents in parallel on independent slices, then merges results. Requires `isolation: worktree` if any spawn writes files. Our `review` agent uses this for parallel review perspectives.

Use when: slices are genuinely independent (no shared state, no merge conflicts).

### Chain-of-Agents (Agent Teams)

For workflows that span sessions or need peer-to-peer messaging, use Agent Teams (`SendMessage` between persistent agents) rather than subagents. Subagents are fire-and-forget; teams keep state and can iterate.

Use when: agents need to converse, retain state across turns, or escalate to each other.

### Sequential vs Parallel — decision

- **Sequential** when later steps depend on earlier outputs (planner → executor)
- **Parallel** when slices are independent (fan-out review perspectives, multi-file refactor)
- **Parallel costs ~7× tokens** of single-thread (community measurements). Only parallelize when wall-clock matters more than spend.

---

## 8. Skills vs Subagents vs Agent Teams vs Hooks

Choosing the right primitive for a capability is the most common design mistake. Quick decision matrix:

| Primitive       | What it is                                     | Use when                                                                 |
| --------------- | ---------------------------------------------- | ------------------------------------------------------------------------ |
| **Skill**       | Portable instructions, lazy-loaded              | Knowledge applies to many contexts; you want any agent to use it on demand |
| **Subagent**    | Isolated context + tool restrictions           | You need context preservation, tool scoping, or parallel execution       |
| **Agent Team**  | Persistent, peer-to-peer messaging, shared task list | Multi-step workflow with state; agents need to converse                  |
| **Hook**        | Deterministic shell command on lifecycle event | A check **must** run regardless of model decisions (lint, secret-scan)   |
| **Slash command** | User-triggered prompt template                | The user, not the orchestrator, should invoke it                         |

**Combining**: a subagent's `skills:` field preloads skill content into its dedicated context. This is often better than invoking the skill at runtime — it avoids re-fetching across turns.

**Anti-pattern**: re-implementing a built-in subagent (`Explore`, `Plan`, `general-purpose`, `statusline-setup`, `claude-code-guide`). Reference and compose them instead.

---

## 9. Checklist for New Agents

Check all items before committing a new agent:

### Frontmatter

- [ ] `name` in kebab-case (no prefix needed when distributed via plugin)
- [ ] `version` set (semver) and bumped on contract changes
- [ ] `description` contains "Delegates here for..." and "Use when..." with action-oriented triggers
- [ ] `tools` (or `disallowedTools`) reduced to minimum — no `Write`/`Edit` on read-only agents
- [ ] `model` appropriate to task (not reflexively `opus`)
- [ ] `maxTurns` set realistically (not 100 as default)
- [ ] `effort` set (`low`/`medium`/`high`/`xhigh`/`max`)
- [ ] `isolation: worktree` set for any agent that may run in parallel with other writers
- [ ] `memory: project` only on agents that genuinely persist learnings across sessions
- [ ] `mcpServers` declared only when the agent genuinely requires a specific server (and documented in prose)
- [ ] `hooks` / `permissionMode` declared only with a clear plugin-side justification

### Prompt

- [ ] One-liner role description present
- [ ] `Respond in the user's language.` included
- [ ] Sections: Role → Core Principle (optional) → Workflow → Output Format → Rules
- [ ] Workflow has numbered steps with clear completion conditions
- [ ] Graceful fallback for missing `.agent-context/` files
- [ ] MCP tool references conditionally phrased with "if available"
- [ ] Output format defined with Markdown template or description

### Quality

- [ ] No contradictory rules
- [ ] Consistent terminology throughout the document
- [ ] No aggressive language except for hard security rules
- [ ] Affirmative rather than negative phrasing where possible
- [ ] Agent is placed in `.claude/agents/` or `agents/`

### Test

- [ ] Agent manually tested with a representative task
- [ ] Scope clear enough that routing works correctly

---

## 10. Agent Disambiguation

These agents have overlapping scopes — use this matrix to route correctly.

### Read-only / Analytical

| Agent | Primary Question | Output Artifact | When NOT to Use |
| ----- | ---------------- | --------------- | --------------- |
| `architect` | How should this be structured? | ADRs, design docs | Don't use for PR line-by-line review or general risk assessment |
| `review` | Is this change safe to merge? | Findings report | Don't use for deep security or performance audits — those have dedicated agents |
| `security` | What attacks are possible against this? | Security audit with severity and threat paths | Don't use for general code quality — that is `review` |
| `analysis` | What is the blast radius / risk / complexity? | Risk, impact, or debt report | Don't use when you need a design recommendation — analysis informs, architect decides |
| `discovery` | What does this codebase do? | Codebase map | Don't use for reviewing specific changes — use for onboarding and orientation |
| `performance` | Where is the bottleneck? | Profiling report with measurements | Don't use without a measurable problem — start with `analysis` |
| `accessibility` | Does this work for all users? | WCAG audit with SC references | Don't use for general UI work — that is `frontend` |

### Write-capable / Implementation

| Agent | Primary Question | Output Artifact | When NOT to Use |
| ----- | ---------------- | --------------- | --------------- |
| `backend` | Implement the server-side change | Code + tests | Don't use for schema / migrations — delegate to `database` |
| `frontend` | Implement the UI | Components + styles | Don't use for deep WCAG audits — delegate to `accessibility` |
| `database` | Change the schema or query safely | Migration + entity update | Don't use for application logic — delegate to `backend` |
| `devops` | Ship this safely | Pipeline / manifest / IaC | Don't use for application code — delegate to `backend`/`frontend` |
| `refactor` | Restructure without changing behavior | Behavior-preserving diff | Don't use for new features — delegate to `backend`/`frontend` |
| `testing` | Specify behavior with tests | Test files | Don't use for general implementation — tests are the artifact |
| `debug` | Find and fix the root cause | Fix + regression test | Don't use for new features or refactors |
| `docs` | Document what is not obvious from code | READMEs, ADRs, changelogs | Don't use for architectural decisions — use `architect` |

### Decision Rules

- **Need a design** → `architect`
- **Need a verdict on a change** → `review`
- **Need an attack-path audit** → `security`
- **Need evidence before deciding** → `analysis`
- **Need a map before starting** → `discovery`
- **Need a behavior-preserving cleanup** → `refactor`
- **Need a schema change** → `database`
- **Need WCAG conformance** → `accessibility`
- **Need to ship it** → `devops`

A typical implementation flow: `discovery` → `analysis` → `architect` → `backend`/`frontend` (+ `database`/`devops` as needed) → `testing` → `review` (+ `security`/`accessibility`/`performance` for deep audits when warranted).

---

## 11. Sources

### Anthropic — Foundational

- [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — Foundational paper on agent design principles
- [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Smallest set of high-signal tokens, context rot, compaction
- [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system) — Parallelization, orchestration, fan-out/fan-in
- [Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler) — Parallel agent case study
- [Claude 4 Prompt Engineering Best Practices](https://platform.claude.com/docs/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices) — Affirmative instructions, tone

### Anthropic — Claude Code & Skills

- [Create custom subagents](https://code.claude.com/docs/en/sub-agents) — Full frontmatter reference (16 fields)
- [Orchestrate teams of Claude Code sessions](https://code.claude.com/docs/en/agent-teams) — Agent Teams primitive (Opus 4.6+)
- [Extend Claude with skills](https://code.claude.com/docs/en/skills) — Skill packaging
- [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — Skills vs Subagents
- [Skills explained](https://claude.com/blog/skills-explained) — Lazy-loaded portable expertise
- [Customize your status line](https://code.claude.com/docs/en/statusline)
- [Context engineering: memory, compaction, and tool clearing](https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools) — Three core levers
- [Managed Agents: SRE Incident Responder cookbook](https://platform.claude.com/cookbook/managed-agents-sre-incident-responder) — Reference incident-response agent

### Community — Roster & Patterns

- [VoltAgent / awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) — 131+ agents in 10 categories
- [wshobson / agents](https://github.com/wshobson/agents) — 185 agents, 25 categories, 80 plugins
- [contains-studio / agents](https://github.com/contains-studio/agents) — Studio/department-oriented roster
- [Community-Access / accessibility-agents](https://github.com/Community-Access/accessibility-agents) — 11 a11y specialists
- [Claude Code Subagents: A Practical 2026 Guide — Nimbalyst](https://nimbalyst.com/blog/claude-code-subagents-guide/)
- [Sub-Agent Best Practices — claudefa.st](https://claudefa.st/blog/guide/agents/sub-agent-best-practices)
- [Agent Patterns: Orchestration Strategies — claudefa.st](https://claudefa.st/blog/guide/agents/agent-patterns)
- [Designing a team of agents — DEV](https://dev.to/nfrankel/designing-a-team-of-agents-j1b) — The 3-5 rule
- [Best practices for Claude Code subagents — PubNub](https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/)
- [Split-and-Merge Pattern — MindStudio](https://www.mindstudio.ai/blog/claude-code-split-and-merge-pattern-sub-agents)
- [2026 Agentic Coding Trends Report — Anthropic](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf)

### Community — General

- [Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md) — Structuring instruction documents
- [Agent Instruction Patterns and Anti-Patterns](https://elements.cloud/blog/agent-instruction-patterns-and-antipatterns-how-to-build-smarter-agents/) — Anti-pattern catalog
- [State of Agent Engineering](https://www.langchain.com/state-of-agent-engineering) — Overview of current patterns and trends
