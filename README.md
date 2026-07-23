# AC Agents

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Release](https://img.shields.io/github/v/release/lx-wnk/agents)](https://github.com/lx-wnk/agents/releases) [![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-7c3aed)](https://github.com/lx-wnk/agents)

Specialist sub-agents for AI-assisted development, packaged as a Claude Code Plugin.

## Why specialist agents?

One generalist agent doing every kind of work accumulates context it doesn't need, carries every tool whether it uses it or not, and blurs the judgement call of _which_ approach fits. A focused specialist avoids all three:

- **Context isolation** — each agent runs in its own window. A `security` audit doesn't drag the `frontend` session's half-finished refactor along with it, and a long investigation never crowds out the orchestrator's own context.
- **Least privilege** — an agent declares only the tools it actually uses. Read-only agents (`review`, `security`, `analysis`, `research`) carry no `Write`/`Edit` _and_ are enforced by a `PreToolUse` hook that blocks write-shaped Bash, so an audit cannot mutate the code it audits.
- **Right-sized cost** — each agent pins the weakest model tier that reliably does its job instead of reflexively running everything on the largest.
- **One task, one owner** — every agent solves exactly one clearly defined job. Sharp scopes mean routing is unambiguous and results are predictable.

## How it works

You delegate a task to a `subagent_type`; the agent runs isolated and returns just the result.

1. **Route** — pick the specialist by `subagent_type` (or let the orchestrator match the task to an agent's description).
2. **Detect** — the agent reads the tech stack from project manifests (`package.json`, `composer.json`, `go.mod`, …). No dependency on the Agent-Context framework — agents work in any project.
3. **Run** — it does the one job in its own context, with only its declared tools.
4. **Return** — source and docs are written directly; project-memory and decision-log updates come back as structured `persist:` blocks for the orchestrator to place (see Design Principles).

## Agents

| Agent           | Role                                                                       |
| --------------- | -------------------------------------------------------------------------- |
| `accessibility` | WCAG audits, ARIA review, keyboard navigation, screen-reader compatibility |
| `agent-tooling` | Authoring Claude Code artifacts — subagents, skills, hooks, commands, manifests |
| `analysis`      | Impact analysis, dependency analysis, risk & complexity                    |
| `architect`     | System & component architecture design and review                          |
| `backend`       | Server-side development, APIs, business logic, service architecture        |
| `chrome`        | Chrome browser automation, visual testing, GIF recording                   |
| `concept`       | Technical concepts, effort estimates, user stories                         |
| `database`      | Schema design, migrations, indexing, query optimization                    |
| `debug`         | Bug investigation, root cause analysis, test failure fixes                 |
| `devops`        | CI/CD pipelines, container builds, Kubernetes, Infrastructure-as-Code      |
| `discovery`     | Codebase mapping, architecture exploration, onboarding                     |
| `docs`          | READMEs, API docs, ADRs, changelogs, project memory updates                |
| `frontend`      | HTML, CSS, JS/TS, React, Vue, Angular, design-to-code                      |
| `incident`      | Production incident triage, timeline reconstruction, mitigation strategy   |
| `performance`   | Performance audits, profiling, bottleneck analysis                         |
| `refactor`      | Large-scale refactors, pattern extraction, modernization, dead-code        |
| `research`      | Technology evaluation, best practices, API/SDK documentation               |
| `review`        | PR reviews, code quality checks, architecture triage                       |
| `security`      | OWASP audits, secret detection, auth review, CVE checks, threat modeling   |
| `testing`       | Writing tests, TDD, coverage improvement, test infrastructure              |

## Design Principles

**Zero coupling to `.agent-context/`** — Agents detect tech stack from project manifests and receive project context via the delegating prompt. They work in any project without requiring the Agent-Context framework.

**Persist block protocol** — For project-memory and decision-log updates (ADRs, lessons), write-coupled agents (`architect`, `docs`) return structured `persist:` blocks instead of writing those memory files themselves, so the orchestrator decides where the data lands. Source code and ordinary docs are still written directly via the agents' Write/Edit tools — the protocol covers only memory artifacts. Persist blocks are validated against `schemas/persist-block.schema.json` (typed fields, allowed target paths under `memory/` or `docs/`, no path traversal).

## Installation

```bash
claude plugin marketplace add https://github.com/lx-wnk/agents
claude plugin install agents@lx-wnk
```

Once installed, agents are available as `subagent_type` in the `Agent` tool:

```
subagent_type: "analysis"   # or backend, frontend, debug, etc.
```

## Plugin Groups

The full `agents` bundle ships all 20 specialists. Four opt-in subset plugins reduce the per-session description footprint — install only the groups you need rather than carrying all 20 descriptions in every session.

The `subagent_type` namespace is `<plugin>:<name>`, so existing `agents:<name>` names stay stable; group plugins add parallel names like `agents-web:frontend`.

| Plugin                 | Agents                                                            |
| ---------------------- | ---------------------------------------------------------------- |
| `agents` (full bundle) | all 20                                                            |
| `agents-core`          | discovery, analysis, architect, concept, research, docs, debug, refactor, agent-tooling |
| `agents-web`           | frontend, accessibility, chrome                                  |
| `agents-ops`           | backend, database, devops, incident                              |
| `agents-quality`       | review, security, testing, performance                           |

```bash
claude plugin marketplace add https://github.com/lx-wnk/agents
claude plugin install agents@lx-wnk          # full bundle
claude plugin install agents-web@lx-wnk      # web specialists only
claude plugin install agents-quality@lx-wnk  # verification specialists only
```

Read-only agents (`review`, `security`, `analysis`, `research`) are enforced read-only by a plugin-level `PreToolUse` hook that blocks write-shaped Bash. A `SubagentStop` hook reminds the orchestrator to dispatch an independent verifier — never the authoring agent — after a write-capable agent finishes.

## Usage with Agent-Context

See [docs/integration-with-agent-context.md](docs/integration-with-agent-context.md) for how to wire these agents into the Agent-Context framework (delegating prompt patterns, persist block consumption).

## License

MIT
