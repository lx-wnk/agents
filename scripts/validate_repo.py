#!/usr/bin/env python3
"""Consistency validator for the ac-agents plugin repo.

Config-only repo: there is no runtime behavior to test, so CI verifies
*consistency* instead. Every check below encodes an invariant that would
otherwise drift silently (roster counts, version sync, manifest paths).

Dependency-free (stdlib only) so CI needs no pip install. Frontmatter is
parsed line-by-line within the leading `---` fence — every field checked is a
single-line scalar, so this is safe without a YAML parser.

Exit code 0 = all invariants hold, 1 = one or more violations (printed).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO / "agents"
MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"
PLUGIN = REPO / ".claude-plugin" / "plugin.json"
README = REPO / "README.md"
CHANGELOG = REPO / "CHANGELOG.md"
PERSIST_SCHEMA = REPO / "schemas" / "persist-block.schema.json"

ALLOWED_MODELS = {"fable", "opus", "sonnet", "haiku", "inherit"}
ALLOWED_EFFORT = {"low", "medium", "high", "xhigh", "max"}
REQUIRED_KEYS = {"name", "version", "description", "tools", "model", "effort", "maxTurns"}

errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def parse_frontmatter(path: Path) -> dict[str, str]:
    """Return the first-key:value map from the leading --- fenced block."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        fail(f"{path.name}: missing leading frontmatter fence")
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        fail(f"{path.name}: unterminated frontmatter fence")
        return {}
    block = text[3:end]
    fm: dict[str, str] = {}
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ": " in line:
            key, val = line.split(": ", 1)
        elif line.rstrip().endswith(":"):
            key, val = line.rstrip()[:-1], ""
        else:
            continue
        fm[key.strip()] = val.strip().strip('"')
    return fm


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{path.relative_to(REPO)}: invalid JSON — {exc}")
        return None


# --- 1. manifests + schema parse -------------------------------------------
marketplace = load_json(MARKETPLACE)
plugin_json = load_json(PLUGIN)
load_json(PERSIST_SCHEMA)

# --- 2. per-agent frontmatter ----------------------------------------------
agent_files = sorted(AGENTS_DIR.glob("*.md"))
if not agent_files:
    fail("no agent files found under agents/")

for path in agent_files:
    fm = parse_frontmatter(path)
    if not fm:
        continue
    missing = REQUIRED_KEYS - fm.keys()
    if missing:
        fail(f"{path.name}: missing frontmatter keys: {', '.join(sorted(missing))}")
    if fm.get("name") and fm["name"] != path.stem:
        fail(f"{path.name}: name '{fm['name']}' != filename stem '{path.stem}'")
    if fm.get("model") and fm["model"] not in ALLOWED_MODELS:
        fail(f"{path.name}: model '{fm['model']}' not in {sorted(ALLOWED_MODELS)}")
    if fm.get("effort") and fm["effort"] not in ALLOWED_EFFORT:
        fail(f"{path.name}: effort '{fm['effort']}' not in {sorted(ALLOWED_EFFORT)}")

count = len(agent_files)

# --- 3. roster count consistency (README + marketplace) --------------------
readme = README.read_text(encoding="utf-8")
for m in re.finditer(r"all (\d+)", readme):
    if int(m.group(1)) != count:
        fail(f"README: 'all {m.group(1)}' != actual agent count {count}")

if marketplace:
    full = next((p for p in marketplace.get("plugins", []) if p.get("name") == "agents"), None)
    if full:
        m = re.search(r"All (\d+) specialist", full.get("description", ""))
        if m and int(m.group(1)) != count:
            fail(f"marketplace 'agents' description: 'All {m.group(1)}' != actual count {count}")

# --- 4. marketplace agents: paths exist ------------------------------------
if marketplace:
    for plugin in marketplace.get("plugins", []):
        for rel in plugin.get("agents", []):
            if not (REPO / rel).exists():
                fail(f"marketplace plugin '{plugin.get('name')}': missing agents path {rel}")

# --- 5. version sync: CHANGELOG header == marketplace version --------------
cl_match = re.search(r"^## \[(\d+\.\d+\.\d+)\]", CHANGELOG.read_text(encoding="utf-8"), re.M)
cl_version = cl_match.group(1) if cl_match else None
mp_version = marketplace.get("version") if marketplace else None
if cl_version and mp_version and cl_version != mp_version:
    fail(f"version drift: CHANGELOG [{cl_version}] != marketplace.json version {mp_version}")
if plugin_json and "version" in plugin_json:
    fail("plugin.json must not carry a version field (SHA-based updates)")

# --- report ----------------------------------------------------------------
if errors:
    print(f"✗ {len(errors)} validation error(s):", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)

print(f"✓ all invariants hold ({count} agents, version {mp_version})")
