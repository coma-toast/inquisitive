# Storage Adapters

Documentation for all storage backends. The backend is chosen once per repo on first run and stored in `.inquisitive/config.json`. Only the selected backends are written to — never all of them by default.

## Backend options

| Option | `config.backend` | Files written | Index | Best for |
|--------|-----------------|--------------|-------|----------|
| JSON | `json` | `entries/<id>.json` | `index.json` | Programmatic consumers, pipelines |
| Markdown | `md` | `entries/<id>.md` | `index.md` | Human review, Obsidian, grep |
| SQLite | `sqlite` | `inquisitive.db` only | SQL query | Querying, aggregating, patterns |
| JSON + Markdown | `json-md` | Both file types | `index.json` | Human + machine readable, no setup *(default)* |
| Markdown + SQLite | `md-sqlite` | `.md` files + db | `index.md` + SQL | Browsable entries + queryable DB *(recommended)* |
| JSON + Markdown + SQLite | `all` | All three | Both + SQL | Maximum compatibility |

## Storage locations

All paths are relative to the **scope level** of the entry:

| Scope | Root path |
|-------|-----------|
| Repo | `<repo-root>/.inquisitive/` |
| Org | `~/.inquisitive/orgs/<org-slug>/` |
| User | `~/.inquisitive/user/` |

Within each root:
```
entries/          # individual entry files
summaries/        # one file per category
inquisitive.db    # SQLite (only if backend includes sqlite)
errors.log        # append-only failure log
```

## Entry schema (all backends)

Every entry contains:

```json
{
  "id": "2026-05-26-143022",
  "timestamp": "2026-05-26T14:30:22-04:00",
  "scope": "repo",
  "org_slug": null,
  "repo": "my-project",
  "file_changed": "src/components/Pricing.tsx",
  "original_suggestion": "table layout with row striping",
  "user_choice": "card layout with feature badges",
  "primary_category": "styling-layout",
  "secondary_category": "ux",
  "criticality": 4,
  "was_planned": false,
  "side_effects": "need to adjust mobile breakpoints",
  "skill_refinement_signal": false,
  "raw_answer": "Tables feel too spreadsheet-like for pricing...",
  "personality": "inquisitive"
}
```

`scope`: `"repo"` | `"org"` | `"user"`
`org_slug`: org name string, or `null` for repo/user scope

---

## Backend 1: JSON (`"json"`)

**Entry files:** `entries/<id>.json`
**Index:** `index.json`

Entry file format:
```json
{
  "id": "2026-05-26-143022",
  "timestamp": "2026-05-26T14:30:22-04:00",
  "scope": "repo",
  "org_slug": null,
  "repo": "my-project",
  "file_changed": "src/components/Pricing.tsx",
  "original_suggestion": "table layout with row striping",
  "user_choice": "card layout with feature badges",
  "primary_category": "styling-layout",
  "secondary_category": "ux",
  "criticality": 4,
  "was_planned": false,
  "side_effects": "need to adjust mobile breakpoints",
  "skill_refinement_signal": false,
  "raw_answer": "Tables feel too spreadsheet-like for pricing...",
  "personality": "inquisitive"
}
```

Index format (`index.json`) — lightweight summary for fast scanning:
```json
[
  {
    "id": "2026-05-26-143022",
    "timestamp": "2026-05-26T14:30:22-04:00",
    "scope": "repo",
    "repo": "my-project",
    "primary_category": "styling-layout",
    "secondary_category": "ux",
    "criticality": 4,
    "was_planned": false
  }
]
```

Append to `index.json` array on each new entry. Never rewrite the whole file — read, append, write.

---

## Backend 2: Markdown (`"md"`)

**Entry files:** `entries/<id>.md`
**Index:** `index.md`

Entry file format:
```markdown
---
id: "2026-05-26-143022"
timestamp: "2026-05-26T14:30:22-04:00"
scope: "repo"
org_slug: null
repo: "my-project"
file_changed: "src/components/Pricing.tsx"
primary_category: "styling-layout"
secondary_category: "ux"
criticality: 4
was_planned: false
personality: "inquisitive"
---

# Change: Table to card layout

**Original suggestion:** table layout with row striping
**User choice:** card layout with feature badges

**User's answer:** Tables feel too spreadsheet-like for pricing. Cards let me add visual hierarchy — feature badges, callout buttons, spacing.

**Side effects:** need to adjust mobile breakpoints
**Skill refinement signal:** no
```

Index format (`index.md`) — Markdown table for human scanning:
```markdown
# Inquisitive Entry Index

| ID | Timestamp | Scope | Repo | Category | Criticality |
|----|-----------|-------|------|----------|-------------|
| 2026-05-26-143022 | 2026-05-26T14:30 | repo | my-project | styling-layout | 4 |
```

Append a new row to the index table on each new entry.

---

## Backend 3: SQLite (`"sqlite"`)

**Database:** `inquisitive.db`
**No flat files** — entries and index exist only in the database.

**Schema:**
```sql
CREATE TABLE IF NOT EXISTS entries (
  id TEXT PRIMARY KEY,
  timestamp TEXT NOT NULL,
  scope TEXT NOT NULL DEFAULT 'repo',
  org_slug TEXT,
  repo TEXT,
  file_changed TEXT,
  original_suggestion TEXT,
  user_choice TEXT,
  primary_category TEXT,
  secondary_category TEXT,
  criticality INTEGER,
  was_planned INTEGER,
  side_effects TEXT,
  skill_refinement_signal INTEGER,
  raw_answer TEXT,
  personality TEXT
);

CREATE TABLE IF NOT EXISTS summaries (
  category TEXT NOT NULL,
  scope TEXT NOT NULL DEFAULT 'repo',
  org_slug TEXT,
  repo TEXT,
  summary TEXT,
  entry_count INTEGER DEFAULT 0,
  last_refined TEXT,
  PRIMARY KEY (category, scope, repo)
);
```

**Common queries:**
```bash
# All entries for a repo
python scripts/inquisitive-sqlite.py query \
  "SELECT * FROM entries WHERE repo = 'my-project'"

# Category breakdown
python scripts/inquisitive-sqlite.py query \
  "SELECT primary_category, COUNT(*) as count FROM entries GROUP BY primary_category ORDER BY count DESC"

# High-criticality entries
python scripts/inquisitive-sqlite.py query \
  "SELECT id, primary_category, raw_answer FROM entries WHERE criticality >= 4"

# Entries by scope
python scripts/inquisitive-sqlite.py query \
  "SELECT scope, COUNT(*) FROM entries GROUP BY scope"
```

Setup: `python scripts/inquisitive-sqlite.py init` (creates tables in `.inquisitive/inquisitive.db` of CWD).

---

## Backend 4: JSON + Markdown (`"json-md"`) — default

Writes both `entries/<id>.json` and `entries/<id>.md` per entry.
Index: `index.json` (JSON format).

Follow Backend 1 for `.json` format and Backend 2 for `.md` format.

No SQLite — no setup required beyond creating `.inquisitive/`.

---

## Backend 5: Markdown + SQLite (`"md-sqlite"`) — recommended

Writes `entries/<id>.md` per entry AND inserts into `inquisitive.db`.
Index: `index.md` (Markdown format) + SQL queries on the database.

Follow Backend 2 for `.md` format and Backend 3 for SQLite schema.

Setup: `python scripts/inquisitive-sqlite.py init` once per scope level.

---

## Backend 6: JSON + Markdown + SQLite (`"all"`)

Writes all three formats per entry.
Index: `index.json` + `index.md` + SQL.

Follow Backends 1, 2, and 3 for their respective formats.

---

## Summary files

Summaries are stored per category at each scope level. Format depends on backend:

**JSON/JSON+MD/MD+SQLite/all backends** — `summaries/<category>.json`:
```json
{
  "category": "styling-layout",
  "scope": "repo",
  "repo": "my-project",
  "org_slug": null,
  "summary": "Cards are strongly preferred over tables for pricing and comparison sections. User values visual hierarchy, badge support, and spacing control over data density.",
  "entries": ["2026-05-26-143022", "2026-05-26-150311"],
  "entry_count": 2,
  "last_refined": "2026-05-26T15:30:00-04:00"
}
```

**Markdown-only backend** — `summaries/<category>.md`:
```markdown
---
category: styling-layout
scope: repo
repo: my-project
entry_count: 2
last_refined: "2026-05-26T15:30:00-04:00"
---

# styling-layout Summary

Cards are strongly preferred over tables for pricing and comparison sections. User values visual hierarchy, badge support, and spacing control over data density.

## Entries
- 2026-05-26-143022
- 2026-05-26-150311
```

---

## Config file

`.inquisitive/config.json` (repo-level):
```json
{
  "backend": "md-sqlite",
  "personality": "inquisitive",
  "frequency": "major",
  "org_slug": "acme-corp"
}
```

`~/.inquisitive/config.json` (global):
```json
{
  "orgs": ["acme-corp", "side-project-org"],
  "default_personality": "inquisitive"
}
```

---

## Write pipeline

Before writing any entry:

1. Read `.inquisitive/config.json` → get `backend`
2. Classify scope → `"repo"` | `"org"` | `"user"` (see SKILL.md § Memory scoping)
3. Determine root path from scope
4. Write to **only** the backends specified in config:
   - `json` or `json-md` or `all` → write `.json` entry, update `index.json`
   - `md` or `json-md` or `md-sqlite` or `all` → write `.md` entry, update `index.md`
   - `sqlite` or `md-sqlite` or `all` → insert into `inquisitive.db`
5. Update the corresponding `summaries/<category>` file
6. On any backend failure → append to `errors.log`, continue with remaining backends

Never block on a failed write. Never write to a backend not in `config.backend`.

---

## Error logging

Append-only log at `<scope-root>/errors.log`:

```
2026-05-26T14:30:22Z | SQLite insert failed | OperationalError: no such table: entries
2026-05-26T14:31:05Z | JSON write failed | PermissionError: [Errno 13] Permission denied: '.inquisitive/entries/2026-05-26-143022.json'
```

Format: `ISO timestamp | backend name | error type + message`
