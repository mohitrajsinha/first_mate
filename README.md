# 🏴‍☠️ First Mate — Open Source Maintainer's Assistant

> An AI-powered agent that helps open source maintainers triage issues, draft release notes, and catch bugs introduced by PRs — powered by [Coral SQL](https://withcoral.com), built for the **Pirates of the Coral-bean Hackathon**.

---

## 🎯 What it does

Managing a busy open source repo is overwhelming. Every week brings dozens of new issues — duplicates, unclear reports, no priorities. Writing release notes means manually reading every merged PR. And when production breaks, finding which PR caused it takes hours of cross-referencing GitHub and Sentry.

**First Mate automates all of that.**

| Feature | Sources | What it does |
|---|---|---|
| 🛠️ **Issue Triage** | GitHub | Fetches real open issues, uses Gemini to detect duplicates and suggest P1/P2/P3 priorities |
| 📝 **Release Notes** | GitHub | Fetches merged PRs since any date and auto-drafts a grouped changelog |
| 🔴 **Error Intelligence** | GitHub + Sentry | Cross-joins merged PRs with Sentry errors to find which PRs broke production |

---

## 🪸 How Coral powers it

Coral is the backbone of this project. Instead of writing GitHub and Sentry API pagination code, handling auth, and manually joining data across two APIs — First Mate writes plain SQL:

```sql
-- Find which PR introduced a Sentry error (cross-source JOIN)
SELECT
  g.number      AS pr_number,
  g.title       AS pr_title,
  g.merged_at,
  s.short_id    AS sentry_id,
  s.title       AS error_title,
  s.first_seen  AS error_first_seen
FROM github.pulls g
JOIN sentry.issues s
  ON s.first_seen >= g.merged_at
WHERE g.owner   = 'your-org'
  AND g.repo    = 'your-repo'
  AND s.project = 'your-sentry-project'
  AND s.status  = 'unresolved'
ORDER BY s.first_seen DESC;
```

Coral handles auth, pagination, and rate limits for both APIs automatically. One query. Two APIs. Zero glue code.

---

## 🤖 Architecture

```
User (Streamlit UI)
      ↓
  Gemini Agent  ←──── SYSTEM_PROMPT with analysis rules
      ↓
  Tool Call
  (triage_issues / draft_release_notes / error_intelligence)
      ↓
  Coral SQL  ──────→  GitHub API
             ──────→  Sentry API
      ↓
  Real data returned to Gemini
      ↓
  Triage Report / Release Notes / Error Report rendered in UI
```

---

## 🚀 Getting started

### Prerequisites

- Python 3.9+
- [Coral](https://github.com/withcoral/coral/releases/latest) installed and on PATH
- GitHub token
- Sentry token
- Gemini API key

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/mohitrajsinha/first-mate
cd first-mate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env
# Fill in your keys

# 4. Add Coral sources
coral source add github
coral source add sentry
```

### Running

```bash
# Streamlit UI (recommended)
streamlit run app.py

# CLI mode
python ui.py
python ui.py --model gemini-pro
```

---

## 📁 Project structure

```
first-mate/
├── app.py            # Streamlit web UI
├── agent.py          # Gemini-powered agent with tool calling
├── tools.py          # Tool definitions, Coral runner, system prompt
├── queries.py        # All Coral SQL queries
├── ui.py             # CLI interface
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔑 Environment variables

Create a `.env` file:

```env
GEMINI_API_KEY=AIza...
GITHUB_TOKEN=ghp_...
SENTRY_TOKEN=sntrys_...
SENTRY_ORG=your-org-slug
```

---

## 🎮 Demo

### Live Demo
https://youtu.be/WhXLNnOrSMc

### Issue Triage
```
Enter: any_org/any_repo → click Triage
→ Real open issues fetched via Coral SQL
→ Gemini detects duplicates semantically
→ P1/P2/P3 priorities suggested
```

### Release Notes
```
Enter: any-org/any-repo + date → click Draft Notes
→ Merged PRs fetched via Coral SQL
→ Auto-grouped into Features / Fixes / Chores
```

### Error Intelligence
```
Enter: GitHub repo + Sentry project ID → click Analyse
→ Coral SQL cross-joins GitHub PRs with Sentry errors
→ PRs that likely introduced production errors are surfaced
→ "PR #7 merged at 15:40 → error appeared at 15:45"
```

---

## 🗺️ Roadmap

### Slack integration (coming soon)

Coral PR [#396](https://github.com/withcoral/coral/pull/396) is actively under review and will add `slack.messages` support. Once merged, First Mate will add a fourth feature:

**Slack Pulse** — cross-join Slack messages with open GitHub issues to surface what the community is actively discussing:

```sql
SELECT s.text, s.user__name, g.number, g.title
FROM slack.messages s
JOIN github.issues g
  ON s.text LIKE '%#' || CAST(g.number AS VARCHAR) || '%'
WHERE s.channel_id = 'channel-id'
  AND g.owner      = 'your-org'
  AND g.repo       = 'your-repo'
  AND g.state      = 'open'
```

---

## 🏴‍☠️ Built for

[Pirates of the Coral-bean Hackathon](https://www.wemakedevs.org/hackathons/coral) — WeMakeDevs × Coral

**Track:** Personal Tools (Track 2)

---

## 📄 License

MIT
