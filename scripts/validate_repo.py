#!/usr/bin/env python3
"""Consistency validator for the ac-agents plugin repo.

Config-only repo: there is no runtime behavior to test, so CI verifies
*consistency* instead. Every check below encodes an invariant that would
otherwise drift silently (roster counts, version sync, manifest paths).

Dependency-free (stdlib only) so CI needs no pip install. Frontmatter is
parsed line-by-line within the leading `---` fence — every field checked is a
single-line scalar, so this is safe without a YAML parser.

Exit code 0 = all invariants hold, 1 = one or more violations (printed).

The version check pins the latest *released* CHANGELOG header (numeric
`## [x.y.z]`); a `## [Unreleased]` section is intentionally skipped, so
edits to shipped artifacts under `[Unreleased]` are not version-guarded
until they land under a released header.
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
BEST_PRACTICES = REPO / "docs" / "best-practices-agent-creation.md"
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
        fail(f"{path.relative_to(REPO)}: invalid JSON: {exc}")
        return None


def read_text(path: Path) -> str:
    """Read a text file, degrading to a clean fail() (not a traceback) if absent."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"{path.relative_to(REPO)}: cannot read: {exc}")
        return ""


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

# --- 3. roster count consistency (README + marketplace, fail-closed) --------
# Assert the expected count-string is PRESENT rather than scanning for any
# number. This ignores unrelated numbers ("install all 4 subset plugins") and
# fails loudly if the marker is reworded or removed — a scan-and-compare check
# silently stops checking when its pattern no longer matches.
readme = read_text(README).lower()
for marker in (f"all {count} specialist", f"all {count} description"):
    if marker not in readme:
        fail(f"README: expected roster marker '{marker}' not found (count {count})")

if marketplace:
    full = next((e for e in marketplace.get("plugins", []) if e.get("name") == "agents"), None)
    if full and f"All {count} specialist" not in full.get("description", ""):
        fail(f"marketplace 'agents' description: expected 'All {count} specialist' not found")

# --- 4. subset groups partition the roster (exclusive + exhaustive) --------
grouped: dict[str, str] = {}
if marketplace:
    for entry in marketplace.get("plugins", []):
        for rel in entry.get("agents", []):
            if not (REPO / rel).exists():
                fail(f"marketplace plugin '{entry.get('name')}': missing agents path {rel}")
            stem = Path(rel).stem
            if stem in grouped:
                fail(f"agent '{stem}' is in two groups: {grouped[stem]} and {entry.get('name')}")
            else:
                grouped[stem] = entry.get("name")
    orphans = {p.stem for p in agent_files} - set(grouped)
    if orphans:
        fail(f"agents in no subset group: {', '.join(sorted(orphans))}")

# --- 4b. docs bundle-count line matches the roster (fail-closed) -----------
if BEST_PRACTICES.exists() and f"{count}-agent bundle" not in read_text(BEST_PRACTICES):
    fail(f"best-practices: expected '{count}-agent bundle' not found (count {count})")

# --- 5. version sync: CHANGELOG header == marketplace version --------------
cl_match = re.search(r"^## \[(\d+\.\d+\.\d+)\]", read_text(CHANGELOG), re.M)
cl_version = cl_match.group(1) if cl_match else None
mp_version = marketplace.get("version") if marketplace else None
if cl_version and mp_version and cl_version != mp_version:
    fail(f"version drift: CHANGELOG [{cl_version}] != marketplace.json version {mp_version}")
if plugin_json and "version" in plugin_json:
    fail("plugin.json must not carry a version field (SHA-based updates)")

# --- report ----------------------------------------------------------------
if errors:
    print(f"FAIL: {len(errors)} validation error(s):", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)

print(f"OK: all invariants hold ({count} agents, version {mp_version})")
