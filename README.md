# AC Agents

Specialist sub-agents for AI-assisted development, packaged as a Claude Code Plugin.

## Agents

| Agent          | Role                                                          |
| -------------- | ------------------------------------------------------------- |
| `ac-analysis`  | Impact analysis, dependency analysis, risk & complexity       |
| `ac-architect` | System & component architecture design and review            |
| `ac-backend`   | Server-side development, APIs, database, business logic       |
| `ac-chrome`    | Chrome browser automation, visual testing, GIF recording      |
| `ac-concept`   | Technical concepts, effort estimates, user stories            |
| `ac-debug`     | Bug investigation, root cause analysis, test failure fixes    |
| `ac-discovery` | Codebase mapping, architecture exploration, onboarding        |
| `ac-docs`      | READMEs, API docs, ADRs, changelogs, project memory updates   |
| `ac-frontend`  | HTML, CSS, JS/TS, React, Vue, Angular, design-to-code         |
| `ac-performance` | Performance audits, profiling, bottleneck analysis          |
| `ac-research`  | Technology evaluation, best practices, API/SDK documentation  |
| `ac-review`    | PR reviews, code quality checks, security audits              |
| `ac-testing`   | Writing tests, TDD, coverage improvement, test infrastructure |

## Design Principles

**Zero coupling to `.agent-context/`** — Agents detect tech stack from project manifests and receive project context via the delegating prompt. They work in any project without requiring the Agent-Context framework.

**Persist block protocol** — Write-coupled agents (`ac-architect`, `ac-docs`) return structured `persist:` blocks in their responses instead of writing directly to project files. The orchestrating agent decides where to persist the data.

## Installation

Add to your `plugins.json`:

```json
"agents@lx-wnk"
```

## Usage with Agent-Context

See [docs/integration-with-agent-context.md](docs/integration-with-agent-context.md) for how to wire these agents into the Agent-Context framework (delegating prompt patterns, persist block consumption).

## License

MIT
