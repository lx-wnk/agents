#!/usr/bin/env bash
# SubagentStop gate: enforce the verifier-not-author rule.
#
# When a write-capable agent finishes, inject a reminder that an INDEPENDENT
# reviewer (never the agent that produced the work) should verify the change
# before merge. Hooks cannot dispatch agents directly, so this surfaces the rule
# as additionalContext the orchestrator reads on its next turn.
#
# Requires: jq.
set -euo pipefail

input=$(cat)
agent=$(printf '%s' "$input" | jq -r '.agent_type // empty')

case "$agent" in
  backend|frontend|database|refactor|devops|debug|accessibility|chrome|testing) ;;
  *) exit 0 ;;
esac

jq -n --arg a "$agent" '{
  hookSpecificOutput: {
    hookEventName: "SubagentStop",
    additionalContext: ("Verifier protocol: write-capable agent [" + $a + "] finished. Dispatch an independent reviewer that is NOT [" + $a + "] before merging its work — use review for general changes, or security when auth, crypto, secrets, or dependencies were touched.")
  }
}'

exit 0
