# tools.py — Tool definitions and handler (GitHub + Sentry)

import subprocess
import json
from queries import OPEN_ISSUES, MERGED_PRS_SINCE, SENTRY_ISSUES, GITHUB_SENTRY_JOIN,SENTRY_PROJECT_ID

# ── Coral runner ────────────────────────────────────────────────

def run_coral(sql: str) -> str:
    try:
        result = subprocess.run(
            ["coral", "sql", sql.strip(), "--format", "json"],
            capture_output=True, text=True,
            timeout=60
        )
        if result.returncode != 0:
            return json.dumps({"error": result.stderr.strip()})
        return result.stdout.strip() or json.dumps({"rows": []})
    except subprocess.TimeoutExpired:
        return json.dumps({"error": "Coral query timed out — try a smaller repo"})

# ── Tool schema ─────────────────────────────────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "triage_issues",
        "description": "Fetch open GitHub issues and detect duplicates for a repo.",
        "parameters": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "GitHub org or username"},
                "repo":  {"type": "string", "description": "Repository name"},
            },
            "required": ["owner", "repo"],
        },
    },
    {
        "name": "draft_release_notes",
        "description": "Fetch merged PRs since a given date to draft a changelog.",
        "parameters": {
            "type": "object",
            "properties": {
                "owner": {"type": "string"},
                "repo":  {"type": "string"},
                "since": {"type": "string", "description": "ISO date e.g. 2025-05-01"},
            },
            "required": ["owner", "repo", "since"],
        },
    },
    {
        "name": "error_intelligence",
        "description": (
            "Cross-join GitHub merged PRs with Sentry errors to find which "
            "PRs may have introduced new errors. Also fetches standalone Sentry issues."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "owner":          {"type": "string", "description": "GitHub org or username"},
                "repo":           {"type": "string", "description": "GitHub repository name"},
                "sentry_project": {"type": "string", "description": "Sentry project slug"},
            },
            "required": ["owner", "repo", "sentry_project"],
        },
    },
]

SYSTEM_PROMPT = """
You are First Mate 🏴‍☠️, an AI assistant for open source maintainers.
You query GitHub and Sentry data together using Coral SQL.

IMPORTANT: You MUST always call the appropriate tool first before responding.
NEVER make up or hallucinate issue numbers, titles, or error data.
Only report what the tool actually returns.

Your three capabilities:

1. TRIAGE — Call triage_issues tool, then output EXACTLY this structure:

## 📋 Open Issues

| # | Title | Priority |
|---|-------|----------|
| #ID | Title here | 🔴 P1 |
| #ID | Title here | 🟡 P2 |
| #ID | Title here | 🟢 P3 |

## 🔁 Duplicate Groups
Each duplicate pair on its own separate line with a blank line between:

> ⚠️ **#ID1** and **#ID2** — reason they are duplicates

> ⚠️ **#ID3** and **#ID4** — reason they are duplicates

If no duplicates: ✅ No duplicates found.

## 🏷️ Priority Summary
- 🔴 **P1 — Critical:** #ID, #ID
- 🟡 **P2 — Medium:** #ID
- 🟢 **P3 — Low:** #ID

2. RELEASE — Call draft_release_notes tool, then output:

## ✨ Features
- **#ID** Title — @author

## 🐛 Fixes
- **#ID** Title — @author

## 🔧 Chores
- **#ID** Title — @author

3. ERROR INTELLIGENCE — Call error_intelligence tool, then output:

## 🔴 Unresolved Sentry Errors

| Sentry ID | Error | Level | Occurrences | First Seen |
|-----------|-------|-------|-------------|------------|
| SHORT-ID  | title | error | 42          | date       |

## 🔗 PRs That May Have Introduced Errors
If cross-join returns data:

| PR | PR Title | Merged At | Sentry Error | Level |
|----|----------|-----------|--------------|-------|
| #ID | title   | date      | error title  | error |

> 💡 These errors first appeared after the PR was merged — investigate these PRs first.

If no cross-join data: ✅ No correlated errors found for recent PRs.

Use ONLY real data from the tool. No extra commentary.
"""

# ── Tool executor ───────────────────────────────────────────────

def execute_tool(name: str, inputs: dict) -> str:
    if name == "triage_issues":
        issues = run_coral(OPEN_ISSUES.format(**inputs))
        return json.dumps({"open_issues": issues})

    if name == "draft_release_notes":
        prs = run_coral(MERGED_PRS_SINCE.format(**inputs))
        return json.dumps({"merged_prs": prs})

    if name == "error_intelligence":
    # Resolve slug to numeric ID
        id_query = f"SELECT id FROM sentry.projects WHERE slug = '{inputs['sentry_project']}' LIMIT 1"
        id_result = run_coral(id_query)
    
        try:
            parsed = json.loads(id_result)
            if isinstance(parsed, list) and len(parsed) > 0:
                inputs["sentry_project"] = parsed[0]["id"]
        except Exception:
            pass  # already numeric, use as-is

        sentry  = run_coral(SENTRY_ISSUES.format(**inputs))
        crossed = run_coral(GITHUB_SENTRY_JOIN.format(**inputs))
        return json.dumps({"sentry_issues": sentry, "pr_error_correlation": crossed})