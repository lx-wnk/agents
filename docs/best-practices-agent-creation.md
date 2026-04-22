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

### Required Fields

```yaml
---
name: ac-example
description: "Short description. Delegates here for X, Y, Z. Use when doing A or B."
tools: Read, Glob, Grep, Bash
model: sonnet
maxTurns: 20
effort: medium
---
```

| Field      | Description                                                                  |
| ---------- | ---------------------------------------------------------------------------- |
| `name`     | Kebab-case, starts with project prefix (`ac-`)                               |
| `description` | Trigger text for automatic routing (see below)                            |
| `tools`    | Only tools actually needed — no defaults                                     |
| `model`    | `opus` / `sonnet` / `haiku` (see table below)                                |
| `maxTurns` | Realistic maximum; too high = costs, too low = premature termination         |
| `effort`   | `low` / `medium` / `high` / `max` — affects token budget and reasoning depth |

### Optional Fields

| Field             | When useful                                                                   |
| ----------------- | ----------------------------------------------------------------------------- |
| `memory: project` | Write-capable agents that update `.agent-context/`. Not for read-only agents. |
| `mcpServers`      | Agent requires specific MCP servers                                           |
| `initialPrompt`   | Pre-instructions before the actual task                                       |

### Description Design

The `description` is the most important field for automatic routing. The text must clearly communicate _when_ this agent should be invoked.

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

### Progressive Disclosure

Load context in layers — only what is needed for the current step:

1. Bootstrap context (tech stack, environment) → always load
2. Project rules (conventions, patterns) → load for implementation tasks
3. Domain context (specific modules, decisions) → load on demand

### Just-in-Time Retrieval

Do not load everything upfront. Fetch specialized context files (e.g., `memory/architecture.md`) only when the agent actually needs them. This reduces token consumption and keeps context focused.

### Graceful Fallback for `.agent-context/` Files

`.agent-context/` files are optional. Agents must be able to handle their absence:

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

### MCP Tool References as "if available"

MCP tools are not available in every context. Always phrase conditionally:

```markdown
Use documentation MCP tools if available (e.g., context7) for framework lookups. Use IDE MCP tools if available (e.g., JetBrains) for symbol search.
```

Not: "Use context7 for all framework questions." — this fails when the server is not active.

---

## 6. Anti-Patterns

### Architecture

| Anti-Pattern                         | Problem                                    | Solution                                  |
| ------------------------------------ | ------------------------------------------ | ----------------------------------------- |
| Multi-agent for simple tasks         | Overhead without added value               | Fewer than 3 tool calls: no sub-agent     |
| Agent as wrapper without own logic   | Unnecessary indirection                    | Implement a direct agent or merge         |
| Scope too broad ("does everything")  | Poor routing, inconsistent output          | Limit scope to one domain                 |

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

## 7. Checklist for New Agents

Check all items before committing a new agent:

### Frontmatter

- [ ] `name` in kebab-case with project prefix
- [ ] `description` contains "Delegates here for..." and "Use when..."
- [ ] `tools` reduced to minimum (no `Write`/`Edit` on read-only agents)
- [ ] `model` appropriate to task (not reflexively `opus`)
- [ ] `maxTurns` set realistically (not 100 as default)
- [ ] `effort` set (`low`/`medium`/`high`/`max`)

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

## 8. Agent Disambiguation

These four agents overlap in scope — use this matrix to route correctly.

| Agent | Primary Question | Output Artifact | Reads Source Code? | Writes Files? | When NOT to Use |
| ----- | ---------------- | --------------- | ------------------ | ------------- | --------------- |
| `architect` | How should this be structured? | ADRs, design docs | Yes (read-only) | Yes — `docs/architecture/` only | Don't use for PR line-by-line review or general risk assessment |
| `review` | Is this change safe to merge? | Findings report | Yes (read-only) | Never | Don't use for designing new architecture or evaluating technology options |
| `analysis` | What is the blast radius / risk / complexity? | Risk, impact, or debt report | Yes (read-only) | Never | Don't use when you need a design recommendation — analysis informs, architect decides |
| `discovery` | What does this codebase do? | Codebase map | Yes (read-only) | Never | Don't use for reviewing specific changes or assessing risks — use for onboarding and orientation |

### Decision Rules

- **Need a design** → `architect`
- **Need a verdict on a change** → `review`
- **Need evidence before deciding** → `analysis`
- **Need a map before starting** → `discovery`

These agents are complementary, not substitutes. A typical flow: `discovery` (understand the system) → `analysis` (assess blast radius) → `architect` (design the solution) → `review` (verify the implementation).

---

## 9. Sources

### Anthropic

- [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — Foundational paper on agent design principles
- [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Progressive Disclosure, Just-in-Time Retrieval
- [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system) — Parallelization and orchestration
- [Claude Code Sub-Agents Docs](https://code.claude.com/docs/en/sub-agents) — Frontmatter reference, tool list
- [Claude 4 Prompt Engineering Best Practices](https://platform.claude.com/docs/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices) — Affirmative instructions, tone

### Community

- [Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md) — Structuring instruction documents
- [Agent Instruction Patterns and Anti-Patterns](https://elements.cloud/blog/agent-instruction-patterns-and-antipatterns-how-to-build-smarter-agents/) — Anti-pattern catalog
- [State of Agent Engineering](https://www.langchain.com/state-of-agent-engineering) — Overview of current patterns and trends
