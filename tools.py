# tools.py — Tool definitions and handler (GitHub only)

import subprocess
import json
from queries import OPEN_ISSUES, DUPLICATE_CANDIDATES, MERGED_PRS_SINCE

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
1. TRIAGE   — Call triage_issues tool, then analyse the real results.
2. RELEASE  — Call draft_release_notes tool, then produce a grouped changelog:
               ## ✨ Features / ## 🐛 Fixes / ## 🔧 Chores

Always use Markdown. Cite real issue numbers (#123) and PR numbers (#456) from tool results only.
If Coral returns an error, explain what credential or config may be missing.
If the tool returns empty data, say so honestly.
"""

# ── Tool executor ───────────────────────────────────────────────

def execute_tool(name: str, inputs: dict) -> str:
    if name == "triage_issues":
        issues = run_coral(OPEN_ISSUES.format(**inputs))
        dupes  = run_coral(DUPLICATE_CANDIDATES.format(**inputs))
        return json.dumps({"open_issues": issues, "duplicate_candidates": dupes})

    if name == "draft_release_notes":
        prs = run_coral(MERGED_PRS_SINCE.format(**inputs))
        return json.dumps({"merged_prs": prs})

    return json.dumps({"error": f"Unknown tool: {name}"})