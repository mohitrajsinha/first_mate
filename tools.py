# tools.py — Tool definitions and handler (GitHub only)

import subprocess
import json
from queries import OPEN_ISSUES, MERGED_PRS_SINCE

# ── Coral runner ────────────────────────────────────────────────

def run_coral(sql: str) -> str:
    try:
        result = subprocess.run(
            ["coral", "sql", sql.strip(), "--format", "json"],
            capture_output=True, text=True,
            timeout=30  # ← add this
        )
        if result.returncode != 0:
            return json.dumps({"error": result.stderr.strip()})
        return result.stdout.strip() or json.dumps({"rows": []})
    except subprocess.TimeoutExpired:
        return json.dumps({"error": "Coral query timed out after 30 seconds"})
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
]

SYSTEM_PROMPT = """
You are First Mate 🏴‍☠️, an AI assistant for open source maintainers.
You query GitHub data using Coral SQL.

IMPORTANT: You MUST always call the appropriate tool first before responding.
NEVER make up or hallucinate issue numbers, titles, or PR data.
Only report what the tool actually returns.

Your two capabilities:

1. TRIAGE — Call triage_issues tool, then:
   - List all real issues from the tool result
   - Use YOUR OWN JUDGMENT to detect duplicates — compare titles semantically,
     not just by string matching. Two issues are duplicates if they describe the
     same bug, feature, or problem even if worded differently.
   - Assign priorities based on severity keywords in titles/labels (crash, fail,
     broken = P1 / slow, missing = P2 / typo, cosmetic = P3)

   Output EXACTLY this structure:

## 📋 Open Issues

| # | Title | Priority |
|---|-------|----------|
| #ID | Title here | 🔴 P1 |
| #ID | Title here | 🟡 P2 |
| #ID | Title here | 🟢 P3 |

## 🔁 Duplicate Groups
If duplicates found, output EACH duplicate pair on its own separate line like this:

> ⚠️ **#ID1** and **#ID2** — reason

> ⚠️ **#ID3** and **#ID4** — reason

Make sure there is a blank line between each blockquote. Never put multiple duplicates in the same blockquote.

If no duplicates:
✅ No duplicates found.

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

Use ONLY real data from the tool. No extra commentary.
"""

# ── Tool executor ───────────────────────────────────────────────

def execute_tool(name: str, inputs: dict) -> str:
    if name == "triage_issues":
        issues = run_coral(OPEN_ISSUES.format(**inputs))
        print(issues)  # Log the raw issues data for debugging
        return json.dumps({"open_issues": issues})

    if name == "draft_release_notes":
        prs = run_coral(MERGED_PRS_SINCE.format(**inputs))
        return json.dumps({"merged_prs": prs})

    return json.dumps({"error": f"Unknown tool: {name}"})