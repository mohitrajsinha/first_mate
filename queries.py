# queries.py — Coral SQL queries for First Mate (GitHub + Sentry)

# ── Issue Triage ────────────────────────────────────────────────

OPEN_ISSUES = """
SELECT id, number, title, state, labels, created_at, user__login, comments
FROM github.issues
WHERE owner = '{owner}' AND repo = '{repo}'
  AND state = 'open'
  AND created_at >= '2025-01-01'
ORDER BY created_at DESC
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
FROM github.pulls pr
WHERE pr.owner     = '{owner}'
  AND pr.repo      = '{repo}'
  AND pr.state     = 'closed'
  AND pr.merged_at >= '{since}'
ORDER BY pr.merged_at DESC
"""

# ── Error Intelligence ──────────────────────────────────────────

SENTRY_ISSUES = """
SELECT
  id,
  short_id,
  title,
  level,
  status,
  count,
  user_count,
  first_seen,
  last_seen,
  project
FROM sentry.issues
WHERE project = '{sentry_project}'
  AND status  = 'unresolved'
ORDER BY first_seen DESC
LIMIT 10
"""

GITHUB_SENTRY_JOIN = """
SELECT
  g.number       AS pr_number,
  g.title        AS pr_title,
  g.user__login  AS pr_author,
  g.merged_at,
  s.short_id     AS sentry_id,
  s.title        AS error_title,
  s.level        AS error_level,
  s.count        AS error_count,
  s.first_seen   AS error_first_seen
FROM github.pulls g
JOIN sentry.issues s
  ON s.first_seen >= g.merged_at
WHERE g.owner   = '{owner}'
  AND g.repo    = '{repo}'
  AND g.state   = 'closed'
  AND s.project = '{sentry_project}'
  AND s.status  = 'unresolved'
ORDER BY s.first_seen DESC
LIMIT 10
"""

SENTRY_PROJECT_ID = """
SELECT id FROM sentry.projects WHERE slug = '{slug}' LIMIT 1
"""