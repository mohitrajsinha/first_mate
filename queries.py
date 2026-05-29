# queries.py — Coral SQL queries for First Mate (GitHub only)

# ── Issue Triage ────────────────────────────────────────────────

OPEN_ISSUES = """
SELECT id, number, title, state, labels, created_at, user__login, comments
FROM github.issues
WHERE owner = '{owner}' AND repo = '{repo}'
  AND state = 'open'
ORDER BY created_at DESC
LIMIT 10
"""

DUPLICATE_CANDIDATES = """
SELECT
  a.number      AS issue_a,
  a.title       AS title_a,
  b.number      AS issue_b,
  b.title       AS title_b,
  a.created_at  AS opened_at
FROM github.issues a
JOIN github.issues b
  ON a.owner = b.owner
  AND a.repo = b.repo
  AND a.number < b.number
WHERE a.owner = '{owner}'
  AND a.repo  = '{repo}'
  AND a.state = 'open'
  AND b.state = 'open'
  AND (
    lower(a.title) LIKE '%' || lower(substr(b.title, 1, 20)) || '%'
    OR lower(b.title) LIKE '%' || lower(substr(a.title, 1, 20)) || '%'
  )
LIMIT 10
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
FROM github.pull_requests pr
WHERE pr.owner     = '{owner}'
  AND pr.repo      = '{repo}'
  AND pr.state     = 'closed'
  AND pr.merged_at >= '{since}'
ORDER BY pr.merged_at DESC
"""