# Storage Adapters

Documentation for all four storage backends.

## Quick comparison

| Tier | Format | Pros | Cons | Active by default |
|------|--------|------|------|-------------------|
| Simple | JSON | Zero deps, fast, machine-friendly | Not human-readable | Yes |
| Readable | Markdown | Obsidian-compatible, grep-able, human-reviewable | Larger disk usage | Yes |
| Structured | SQLite | Queryable, aggregatable, CLI tooling | Dependency (sqlite3) | On setup |
| Advanced | Milvus | Semantic search, pattern matching | Heavy, requires researcher subagent | No |

## Tier 1: JSON (always active)

**Location:** `data/memory/entries/<id>.json` and `data/memory/index.json`

**Entry format:**
```json
{
  "id": "2026-05-25-143022",
  "timestamp": "2026-05-25T14:30:22-04:00",
  "project": "my-project",
  "file_changed": "src/components/Pricing.tsx",
  "original_suggestion": "table layout with row striping",
  "user_choice": "card layout with feature badges",
  "primary_category": "styling-layout",
  "secondary_category": "ux",
  "criticality": 4,
  "was_planned": false,
  "side_effects": "need to adjust mobile breakpoints",
  "skill_refinement_signal": false,
  "raw_answer": "Tables feel too spreadsheet-like...",
  "personality": "inquisitive"
}
```

**Index format:** `data/memory/index.json`
```json
[
  {
    "id": "2026-05-25-143022",
    "timestamp": "2026-05-25T14:30:22-04:00",
    "project": "my-project",
    "primary_category": "styling-layout",
    "secondary_category": "ux",
    "criticality": 4,
    "was_planned": false
  }
]
```

The index is an array. Append to it when writing a new entry. Use it for fast scanning without reading all entry files.

## Tier 2: Markdown (always active)

**Location:** `data/memory/entries/<id>.md`

**Format:**
```markdown
---
id: "2026-05-25-143022"
timestamp: "2026-05-25T14:30:22-04:00"
project: "my-project"
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

These files are designed to be opened in Obsidian for manual review.

## Tier 3: SQLite (on setup, then always on)

**Location:** `data/memory/inquisitive.db`

**Setup:** Run `python scripts/inquisitive-sqlite.py init` once. This creates the database and tables.

**Schema:**
```sql
CREATE TABLE entries (
  id TEXT PRIMARY KEY,
  timestamp TEXT,
  project TEXT,
  file_changed TEXT,
  original_suggestion TEXT,
  user_choice TEXT,
  primary_category TEXT,
  secondary_category TEXT,
  criticality INTEGER,
  was_planned INTEGER,
  side_effects TEXT,
  skill_refinement_signal INTEGER,
  raw_answer TEXT
);

CREATE TABLE summaries (
  category TEXT PRIMARY KEY,
  summary TEXT,
  last_refined TEXT
);
```

**Usage:**
```bash
# Initialize
python scripts/inquisitive-sqlite.py init

# Insert an entry
python scripts/inquisitive-sqlite.py insert '{"id":"2026-05-25-143022","timestamp":"2026-05-25T14:30:22-04:00","project":"my-project","file_changed":"src/components/Pricing.tsx","original_suggestion":"table layout","user_choice":"card layout","primary_category":"styling-layout","secondary_category":"ux","criticality":4,"was_planned":0,"side_effects":"breakpoint adjustment needed","skill_refinement_signal":0,"raw_answer":"Tables feel too spreadsheet-like"}'

# Query entries
python scripts/inquisitive-sqlite.py query "SELECT * FROM entries WHERE primary_category = 'styling-layout'"

# Get category counts
python scripts/inquisitive-sqlite.py query "SELECT primary_category, COUNT(*) as count FROM entries GROUP BY primary_category ORDER BY count DESC"
```

## Tier 4: Milvus (optional)

Requires the researcher subagent and a running Milvus instance.

**Collection name:** `inquisitive_memory`

**Schema:**
- `id` (string, primary)
- `project` (string)
- `primary_category` (string)
- `raw_answer` (string) — vectorized for semantic search
- `timestamp` (string)

**Usage:** Invoke the researcher subagent:
```
Use the researcher subagent to:
- Insert into Milvus collection "inquisitive_memory": {id, project, primary_category, raw_answer, timestamp}
- Search for entries semantically similar to: "layout changes for visual hierarchy"
```

## Writing rules

When writing a new entry:
1. Always write JSON and Markdown
2. Always update `index.json` (append)
3. If SQLite is initialized, also insert there
4. If Milvus is configured, also insert there
5. If any backend fails, log the error and continue — never block

## Summary updates

When updating a summary file (`data/summaries/<category>.json`):
1. Read the current summary
2. Update `summary` text
3. Update `entries` array (up to 10 IDs)
4. Update `last_refined` timestamp
5. If SQLite is initialized, update `summaries` table
6. If Milvus is configured, update the collection entry
