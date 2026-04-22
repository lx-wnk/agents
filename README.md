# AC Agents

Specialist sub-agents for AI-assisted development, packaged as a Claude Code Plugin.

## Agents

| Agent          | Role                                                          |
| -------------- | ------------------------------------------------------------- |
| `analysis`     | Impact analysis, dependency analysis, risk & complexity       |
| `architect`    | System & component architecture design and review            |
| `backend`      | Server-side development, APIs, database, business logic       |
| `chrome`       | Chrome browser automation, visual testing, GIF recording      |
| `concept`      | Technical concepts, effort estimates, user stories            |
| `debug`        | Bug investigation, root cause analysis, test failure fixes    |
| `discovery`    | Codebase mapping, architecture exploration, onboarding        |
| `docs`         | READMEs, API docs, ADRs, changelogs, project memory updates   |
| `frontend`     | HTML, CSS, JS/TS, React, Vue, Angular, design-to-code         |
| `performance`  | Performance audits, profiling, bottleneck analysis          |
| `research`     | Technology evaluation, best practices, API/SDK documentation  |
| `review`       | PR reviews, code quality checks, architecture analysis, security audits |
| `testing`      | Writing tests, TDD, coverage improvement, test infrastructure |

## Design Principles

**Zero coupling to `.agent-context/`** — Agents detect tech stack from project manifests and receive project context via the delegating prompt. They work in any project without requiring the Agent-Context framework.

**Persist block protocol** — Write-coupled agents (`architect`, `docs`) return structured `persist:` blocks in their responses instead of writing directly to project files. The orchestrating agent decides where to persist the data.

## Installation

Add to your `plugins.json`:

```json
"agents@lx-wnk"
```

## Usage with Agent-Context

See [docs/integration-with-agent-context.md](docs/integration-with-agent-context.md) for how to wire these agents into the Agent-Context framework (delegating prompt patterns, persist block consumption).

## License

MIT
