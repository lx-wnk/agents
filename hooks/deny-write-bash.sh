#!/usr/bin/env bash
# PreToolUse(Bash) gate: enforce read-only by capability for read-only agents.
#
# Read-only agents (review, security, analysis, research) keep Bash so they can
# run git diff, scanners (semgrep, npm audit), grep/rg and test commands — but
# must not mutate the working tree. Plugin-shipped agents cannot carry their own
# `hooks:` frontmatter (ignored for security), so this gate lives at plugin level
# and scopes itself via the `agent_type` field present in the PreToolUse payload.
#
# Requires: jq.
set -euo pipefail

input=$(cat)
agent=$(printf '%s' "$input" | jq -r '.agent_type // empty')
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty')

# Only gate the read-only agents; everything else uses the normal permission flow.
case "$agent" in
  review|security|analysis|research) ;;
  *) exit 0 ;;
esac

# Drop harmless redirections to the null device and stream merges before testing,
# so read commands like `... 2>/dev/null` are not mistaken for file writes.
scrubbed=$(printf '%s' "$cmd" \
  | sed -E 's@[0-9]?>>?[[:space:]]*/dev/null@@g; s@[0-9]>&[0-9]@@g')

# Write-shaped patterns: file/redirect writes and repo state mutations.
deny_re='>>?|[[:space:]]tee([[:space:]]|$)|sed[[:space:]]+-i|(^|[[:space:]])(rm|mv|cp|dd|truncate|install|mkdir|rmdir|ln|chmod|chown|touch)[[:space:]]|git[[:space:]]+(checkout|reset|restore|clean|commit|push|apply|stash|rebase|merge|am|cherry-pick|tag|branch[[:space:]]+-[dD])'

if printf '%s' "$scrubbed" | grep -Eq "$deny_re"; then
  jq -n --arg a "$agent" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: ("read-only agent (" + $a + ") may not mutate the working tree; write-shaped Bash blocked")
    }
  }'
  exit 0
fi

exit 0
