# queries.py — Coral SQL queries for First Mate (GitHub only)

# ── Issue Triage ────────────────────────────────────────────────

OPEN_ISSUES = """
SELECT id, number, title, state, labels, created_at, user__login, comments
FROM github.issues
WHERE owner = '{owner}' AND repo = '{repo}'
  AND state = 'open'
ORDER BY created_at DESC
LIMIT 50
"""


# ── Release Notes ───────────────────────────────────────────────

MERGED_PRS_SINCE = """
SELECT
  pr.number,
  pr.title,
  pr.merged_at,
  pr.user__login  AS author,
  pr.body,
  pr.labels
FROM github.pulls pr
WHERE pr.owner     = '{owner}'
  AND pr.repo      = '{repo}'
  AND pr.state     = 'closed'
  AND pr.merged_at >= '{since}'
ORDER BY pr.merged_at DESC
"""