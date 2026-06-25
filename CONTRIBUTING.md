# Contributing

Thanks for your interest in improving this plugin. It ships specialist sub-agents for
Claude Code as a plugin marketplace. Contributions that sharpen an existing agent's scope,
fix a routing overlap, or add a well-justified new specialist are all welcome.

## Scope

This repo distributes agent definitions (`agents/*.md`), plugin metadata
(`.claude-plugin/`), and the bash hooks under `hooks/`. Keep changes focused on those
artifacts. Agent design follows one rule above all others: each agent solves exactly one
clearly defined task.

## Proposing or adding an agent

1. Open an agent-proposal issue first so the scope can be discussed before you write code.
   Explain the one-task scope and why the existing agents (see the disambiguation matrix in
   `docs/best-practices-agent-creation.md` §10) don't already cover it.
2. Follow the authoritative contributor guide: `docs/best-practices-agent-creation.md`.
   Work through the checklist in §9 before opening a PR — it covers frontmatter, prompt
   structure, and quality gates.
3. Apply these design constraints in particular:
   - **Tools, least privilege.** Declare only the tools the agent actually uses. Read-only
     agents carry no `Write`/`Edit`. See §2 (Tool Minimization).
   - **Explicit model tier.** Set `model` to the weakest tier that reliably does the job.
     The tiering rationale is single-sourced in §2 (Model Selection) — match it, don't
     reflexively pick `opus`.
   - **Graceful `.agent-context/` fallback.** Agents stay decoupled from the Agent-Context
     framework. When `.agent-context/` files are absent, detect the tech stack from project
     manifests (`package.json`, `composer.json`, `go.mod`, …) instead of erroring.

## Local validation

Validate the plugin before opening a PR:

```bash
claude plugin validate .
```

The hooks under `hooks/` are plain bash and depend on `jq` for JSON parsing. Keep them
POSIX-friendly and test them with the JSON payload shape Claude Code passes on the relevant
lifecycle event (`PreToolUse`, `SubagentStop`).

## Pull request process

- Branch off `main`.
- Write commit messages and PR descriptions in English.
- Reference the issue your PR addresses.
- Keep diffs focused — one concern per PR. Unrelated cleanups belong in their own PR.
- On any contract change (prompt behavior, frontmatter, tool set, hook behavior):
  - Update `CHANGELOG.md` following the Keep a Changelog format already in use.
  - Bump the affected agent's `version:` (semver) in its frontmatter.
- Confirm read-only agents stay read-only by capability — no write tools, and the
  `PreToolUse` hook gate still applies.
- Run `claude plugin validate .` and confirm it passes.

## Code of Conduct

This project follows the Contributor Covenant. See `CODE_OF_CONDUCT.md`. By participating
you agree to uphold it.

## License

This project is licensed under the MIT License (see `LICENSE`). By contributing, you agree
that your contributions are licensed under the same terms.
