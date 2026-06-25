# Security Policy

## Supported versions

Security fixes target the latest release. Older versions are not maintained — upgrade to the
latest release before reporting an issue.

## Reporting a vulnerability

Report vulnerabilities privately by email to **git@jinnoflife.com**. Please do not open a
public issue for a security report.

Include:

- A clear description of the vulnerability and its impact.
- Steps to reproduce it (a minimal repro, the agent or hook involved, and the Claude Code
  version).

You will receive a best-effort acknowledgement and we will work with you on a fix and
disclosure timeline.

## Scope

This repo ships agent definitions (`agents/*.md`) and bash hooks (`hooks/`). The most
relevant classes of issue to flag:

- A read-only agent (`review`, `security`, `analysis`, `research`) able to mutate state —
  for example a way to bypass the `PreToolUse` write-shaped-Bash gate in
  `hooks/deny-write-bash.sh`.
- A persist block that escapes its allowed paths — writing outside `memory/` or `docs/`, or
  defeating the path-traversal checks in `schemas/persist-block.schema.json`.
- A hook that mishandles untrusted input from its JSON payload (e.g. shell injection through
  unquoted `jq` output).

Reports that demonstrate any of the above are especially valuable.
