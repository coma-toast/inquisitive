# Inquisitive — Learn from Every Adjustment

A meta-skill that makes the agent curious about user intent. Every time the user adjusts something the agent proposed, inquisitive figures out why the original suggestion missed the mark so the agent gets it right on the first try next time.

## What I do

- **Analyze changes** — After every user-initiated file edit or plan modification, analyze what was requested vs. what the agent proposed
- **Ask targeted questions** — Ask context-aware "why" questions that close the learning loop between the agent's suggestion and the user's choice
- **Categorize answers** — Classify into 12 categories with hierarchical intent tracking (company → repo → task)
- **Build memory** — Store answers at the right scope level (repo, org, or user) in the chosen backend format
- **Refine summaries** — Every 10 entries per category, review, consolidate, prune, and update the evolving understanding
- **Create sub-skills** — When strong patterns emerge, suggest, draft, or auto-create refinement skills (user's choice of 3 modes)
- **Load context for planning** — Before any plan or build task, load merged memory from all 3 levels and surface relevant preferences

## Personalities

Three modes switchable at any time:

| Mode | Name | Tone |
|------|------|------|
| Professional *(default)* | **Inquisitive** | Clear, articulate, full sentences |
| Pug (two flavors) | **George** or **Phoebe** | Black male / fawn female. Short sentences, 1-2 dog sounds, token-efficient |

Personalities are defined in `personalities/`. On first activation, ask the user which they prefer.

## When to trigger

**Activate when:**
- A file was edited/created and the user's instruction caused the edit (not auto-generated content)
- A plan was modified via follow-up instructions or annotations
- The user says "change this," "actually do it differently," "refine," "revise"
- The user provides feedback about something being wrong or needing adjustment
- The user asks the agent to adjust, redo, or rework something

**Skip when:**
- Typos, formatting-only, rename-only refactors
- User has opted out for the session
- Per-turn question limit reached (default 1)
- The change is a direct translation of a clear instruction with no decision
- Do NOT confuse with grill-me — inquisitive asks one targeted "why" after a user change; it does NOT stress-test plans or interview users about their designs

## First run in a repo

On first activation in a repo (no `.inquisitive/` directory found), run this setup flow before anything else.

### Step 1: Choose storage backend

> "First time here — I need to pick a storage format for memory in this repo. Here's what each option means:
>
> **1. JSON** — machine-readable `.json` files. Fast, portable, easy to parse in scripts. Not human-readable without a tool.
> **2. Markdown** — human-readable `.md` files. Browse in Obsidian, read in any editor, grep-able. Harder to query across entries.
> **3. SQLite** — single queryable database. Filter, aggregate, find patterns with SQL. Not readable without tooling; no individual entry files to browse.
> **4. JSON + Markdown** *(default)* — both file types per entry. Human and machine readable, no setup required.
> **5. Markdown + SQLite** *(recommended)* — human-readable entry files AND a queryable database. Best balance of browsability and power. Requires Python's built-in `sqlite3`.
> **6. JSON + Markdown + SQLite** — everything. Maximum compatibility and queryability. Triple storage overhead.
>
> Which format? (1–6, or press enter for default JSON + Markdown)"

Store decision in `.inquisitive/config.json` as `"backend"`:

| Choice | Value |
|--------|-------|
| 1 | `"json"` |
| 2 | `"md"` |
| 3 | `"sqlite"` |
| 4 | `"json-md"` |
| 5 | `"md-sqlite"` |
| 6 | `"all"` |

### Step 2: Choose personality

> "Which personality should I use for questions?
> - **Inquisitive** *(default)* — professional, clear, full sentences
> - **George** — curious black male pug, short sentences, dog sounds
> - **Phoebe** — curious fawn female pug, same as George"

Store as `"personality"` in config.

### Step 3: Choose frequency

> "How often should I ask about changes?
> - **Every change** — fastest learning, more questions
> - **Major changes only** *(default)* — balanced
> - **Rarely** — minimal interruptions, slower learning"

Store as `"frequency"` in config.

### Step 4: Create `.inquisitive/` structure

Create the following in the repo root:

```
.inquisitive/
  .gitignore        # see content below
  config.json       # backend, personality, frequency, org_slug
  entries/          # created empty
  summaries/        # created empty — committed to git
  errors.log        # created empty — gitignored
```

**`.inquisitive/.gitignore` content:**
```gitignore
# Private — not committed
entries/
*.db
errors.log

# Summaries ARE committed (enables team sharing of learned preferences)
# To stop sharing summaries with your team, uncomment:
# summaries/
```

**`.inquisitive/config.json` initial structure:**
```json
{
  "backend": "json-md",
  "personality": "inquisitive",
  "frequency": "major",
  "org_slug": null
}
```

`org_slug` is set when the first org-level entry is stored (see Memory scoping below).

## Frequency control

On first run (after setup), explain:
> "To get it right on the first try, I want to learn from every adjustment. Asking about changes builds a better model of your preferences so I make fewer wrong guesses."

Every 10 entries, re-check: "The questions are helping — I'm getting [category] right more often. Keep the current pace, speed up, or slow down?"

On first run also ask: "Ask about each change in a turn, or just the most significant one?" Default: just the top one.

If 3 consecutive follow-up bundles are fully skipped, auto-offer to stop follow-ups entirely.

### Per-repo boost
In a new repo, first 5 changes always trigger regardless of frequency level.

## Question procedure

### Primary question
> **Inquisitive:** "What was the primary motivation behind this change?"
> **George:** "Why human change thing? Snort. George learn."
> **Phoebe:** "Why human change thing? Snort. Phoebe learn."

### Context-aware secondary (core learning signal)
Identify what the agent originally suggested vs. what the user chose. Ask:
> **Inquisitive:** "I suggested [original approach], but you went with [user choice]. What was it about my suggestion that didn't fit, and what made [user choice] the better option?"
> **George/Phoebe:** "[Name] think [approach]. Human pick [choice]. Huff. Why human pick that? [Name] need know."

### Follow-up bundle (user skips any by saying "skip")
Present as a single block:
> "Quick follow-ups — just say 'skip' to any:
> 1. On a scale of 1-5, how critical was this change?
> 2. Was this change planned in advance or reactive?
> 3. Did you encounter any unexpected side effects?
> 4. Would encoding this preference into a reusable skill be valuable?"

Store the answer for each follow-up in the entry.

### George/Phoebe language rules
- 2–6 words per sentence
- Drop articles and helper verbs where natural
- Simple present tense
- 1–2 dog sounds max per response: snort, grunt, huff, sniff, air chomp
- Third-person self-reference by name
- Curious, earnest, slightly confused tone
- NO doge-specific patterns (no "such X", "much Y", "wow", "very Z")
- Token savings is a bonus — ~50-60% fewer tokens
- Subagents are called a "grumble" (collective noun for pugs)

### Plan intent summary
When submitting or updating a plan, append this section at the bottom:
```markdown
## Agent's Understanding of Your Goals

Your priorities for this project (based on inquisitive memory):
- **[Category]** — [summary of understanding]
- **[Category]** — [summary of understanding]
- **Recent learnings:** [most relevant entry summary, if any]

Does this match your understanding? I'll adjust as we work.
```

## Memory categories

| # | Category | What it captures |
|---|----------|------------------|
| 1 | **Intent** | Hierarchical — company goals, repo purpose, task objective |
| 2 | **User Experience** | Interaction changes, flow, usability, delight |
| 3 | **Styling / Layout** | Visual design, spacing, alignment, aesthetics |
| 4 | **Security** | Threat model, auth, permissions, data protection |
| 5 | **Business Logic** | Domain rules, computation, data flow, algorithms |
| 6 | **Efficiency** | Performance, resource usage, latency, optimization |
| 7 | **Maintainability** | Code clarity, tech debt, organization, naming |
| 8 | **Reliability** | Error handling, edge cases, fault tolerance, retries |
| 9 | **Compatibility** | Cross-platform, API contracts, migration, deps |
| 10 | **Developer Experience** | Tooling, debugging, CI/CD, workflow friction |
| 11 | **Data Integrity** | Validation, consistency, correctness, schema |
| 12 | **Compliance / Policy** | Legal, regulatory, organizational policy |

See `references/category-guide.md` for full definitions with domain-specific examples.

**Intent hierarchy** — entries in the Intent category capture three levels:
- `company`: The broad business/organizational goal → maps to **org-level** memory
- `repo`: What this specific project/repo aims to do → maps to **repo-level** memory
- `task`: What the current change is trying to accomplish → maps to **repo-level** memory

## 3-level memory architecture

Every entry is stored at exactly one scope level: **repo**, **org**, or **user**.

### Storage locations

| Level | Location | What goes here |
|-------|----------|----------------|
| **Repo** | `<repo-root>/.inquisitive/` | Preferences specific to this codebase |
| **Org** | `~/.inquisitive/orgs/<org-slug>/` | Conventions shared across an org's repos |
| **User** | `~/.inquisitive/user/` | Personal preferences across all projects |

Each level has the same internal structure:
```
entries/          # individual entry files (format depends on backend choice)
summaries/        # one file per category — the refined understanding
inquisitive.db    # SQLite db (only if backend includes sqlite)
errors.log        # append-only write failure log
```

For repo-level, `summaries/` is committed to git. For org and user levels, everything lives in `~/.inquisitive/` (never committed).

### Scope classification

When storing an entry, classify scope automatically:

**→ User scope** (no prompt) when the answer is explicitly first-person personal:
- Contains: "I always", "I personally", "I prefer", "I like to", "my habit"
- Write to `~/.inquisitive/user/`

**→ Prompt the user** when the answer sounds cross-repo:
- Contains: "we always", "our team", "in all our projects", "our standard", "across repos"
- Category is `intent` at `company` level
- Same preference has appeared in 2+ different repos (detectable via user-level summary)
- Ask: *"This sounds like it might apply beyond this repo. Save as: (1) Just this repo  (2) Org-wide  (3) Your personal preference?"*
- If they choose org: proceed to org slug resolution (below)

**→ Repo scope** (default, no prompt) for everything else.

### Org slug resolution

Triggered when the user chooses org-level for the first time (or when `org_slug` is null in config).

1. Run `git remote get-url origin` and parse the owner segment:
   - `https://github.com/acme-corp/repo` → `acme-corp`
   - `git@github.com:acme-corp/repo.git` → `acme-corp`
2. Suggest it: *"Looks like your org is `acme-corp` from your git remote — use that, or enter a different name?"*
3. Store confirmed slug in both `.inquisitive/config.json` and `~/.inquisitive/config.json`
4. Create `~/.inquisitive/orgs/<org-slug>/` with same structure as other levels

## Loading memory for planning

**Before any plan or build task**, load inquisitive memory from all 3 levels and surface relevant preferences. Use `agents/context-loader.md` for the full loading procedure.

### Quick reference

1. Read `.inquisitive/config.json` → get `org_slug`, `backend`
2. Load `.inquisitive/summaries/` → repo-level preferences
3. Load `~/.inquisitive/user/summaries/` → user preferences
4. Load `~/.inquisitive/orgs/<org-slug>/summaries/` → org preferences (if `org_slug` set)
5. Merge all three — **repo overrides org overrides user** on any conflict
6. Prepend to plan as:

```markdown
## Inquisitive Context

**Repo preferences** (`<repo-name>`):
- [styling-layout] Cards preferred over tables for pricing sections
- [maintainability] All utilities extracted into shared modules

**Org preferences** (`acme-corp`):
- [styling-layout] All projects use Tailwind CSS
- [compatibility] Minimum Node 20 across all services

**User preferences**:
- [developer-experience] Prefer async/await over .then() chains

*Outdated? Run `/inquisitive-refine` to update.*
```

If no `.inquisitive/` found: skip silently, note "no inquisitive memory for this repo yet" in plan footer.

## Bootstrap repo scan

On first activation in a new repo (after setup flow above):
> "Want me to scan the project to find inconsistencies or unclear areas? This seeds my understanding faster so I make fewer wrong guesses."

If scan accepted:
1. Scan README, configs, package files, directory structure, key source files
2. Identify inconsistencies, ambiguous intent, unclear design patterns
3. Ask up to **3 questions per category** (max ~15 per session)
4. Seed initial memory entries + summaries
5. Collect any tasks identified during scan and emit them all at the end (see Task tracking)

Manual trigger: `/inquisitive-scan` or "run the repo scan again"

## Task tracking

When inquisitive identifies actionable tasks (cleanup, missing tests, missing docs, dead code, etc.) during a bootstrap scan or any session, it tracks them without interrupting the flow.

### Detection

Flag a task when:
- A scan reveals a clear gap (no tests, dead code, missing README section, stale config)
- A question answer implies deferred work (e.g., "that module is outdated")
- The user explicitly mentions something needs fixing

### Delegation order

1. **Check if a todo skill is available** — look for `todo-add`, `todo-check`, or `todo-manager` in the agent's loaded skill list (system prompt). If found, delegate task creation to it.
2. **Check the filesystem** — if the skill list is unavailable, glob for `todo-*/SKILL.md` in common skill paths (`~/.agents/skills/`, `.opencode/skills/`, `~/.config/opencode/skills/`). If found, delegate.
3. **Check if a todo MCP server is available** — if a todo/task MCP tool is registered, use it.
4. **Fall back: write directly to `TODO.md`** in the repo root using the standard format (see `references/task-tracking.md`).

### Batch, don't interrupt

- Collect all tasks identified during a scan; emit them **all at once at the end**
- Do not break question flow to log tasks one-by-one
- After the scan, summarize:
  > "Found [N] tasks and added them to TODO.md [or: via [skill-name]]:"
  > - [brief task list]
  >
  > Take action on any now, or review TODO.md later.

### George/Phoebe variant

> "George find [N] thing to fix. Added to list. Sniff sniff. Look later?"

### Fallback TODO.md format

If writing directly (no todo skill available):

```markdown
- [ ] Task description
  - **Context:** Why this was flagged by inquisitive
  - **Validation Criteria:** How to confirm it's done
  - **Created:** YYYY-MM-DD
```

Priority sections (create if missing): `## Priority: High`, `## Priority: Medium`, `## Priority: Low`

Default priority: **Medium** unless the gap is a security issue or blocking (High) or purely cosmetic (Low).

See `references/task-tracking.md` for full format reference and skill detection details.

## Memory architecture

### Entry schema

Every entry includes these fields regardless of backend:

```json
{
  "id": "2026-05-26-143022",
  "timestamp": "2026-05-26T14:30:22-04:00",
  "scope": "repo",
  "org_slug": null,
  "repo": "my-project",
  "file_changed": "src/components/Pricing.tsx",
  "original_suggestion": "description of what agent proposed",
  "user_choice": "description of what user chose instead",
  "primary_category": "styling-layout",
  "secondary_category": "ux",
  "criticality": 4,
  "was_planned": false,
  "side_effects": "need to adjust mobile breakpoints",
  "skill_refinement_signal": false,
  "raw_answer": "full answer from user",
  "personality": "inquisitive"
}
```

`scope`: `"repo"` | `"org"` | `"user"`
`org_slug`: org name string, or `null` for repo/user scope

### Layer 2: Summaries (curated knowledge)

Each category has a summary file in `<level>/summaries/<category>.json` (or `.md` for markdown-only backends):

```json
{
  "category": "styling-layout",
  "scope": "repo",
  "repo": "my-project",
  "summary": "Continuously refined understanding...",
  "entries": ["id1", "id2", "id3"],
  "entry_count": 3,
  "last_refined": "2026-05-26T14:30:22-04:00"
}
```

For intent category at repo scope, also include:
```json
{
  "hierarchy": {
    "company": "Generate leads from devs visiting docs",
    "repo": "Convert readers into trial users",
    "task": "Fix CTA position above fold"
  }
}
```

### Auto-refinement process

Triggered every **10 entries per category**:
1. Review all entries in the category
2. Fully valid entries → keep as-is
3. Entries needing update → create updated entry, delete old
4. Stale/outdated entries → delete
5. Duplicates covering same ground → merge into 1, delete extras
6. Rewrite summary text to reflect refined understanding
7. Enforce ≤10 entries cap per category — combine multiple into 1 if needed

### Manual interactive refinement

User says `/inquisitive-refine` or "let's review memory":
- Agent presents each category's summary and entries
- "Does this summary still feel accurate?"
- "This entry from [date] — still relevant?"
- "I noticed [pattern] — could you tell me more?"
- User can confirm, modify, merge, or delete entries interactively

## Storage backends

The backend is chosen once per repo on first run and stored in `.inquisitive/config.json`. It is never changed automatically.

| Backend | `config.backend` | Files written | Index |
|---------|-----------------|--------------|-------|
| JSON | `json` | `entries/<id>.json` | `index.json` |
| Markdown | `md` | `entries/<id>.md` | `index.md` |
| SQLite | `sqlite` | `inquisitive.db` | SQL query |
| JSON + Markdown | `json-md` | Both file types | `index.json` |
| Markdown + SQLite | `md-sqlite` | `.md` files + `inquisitive.db` | `index.md` + SQL |
| JSON + Markdown + SQLite | `all` | All three | Both + SQL |

See `storage/adapters.md` for full schema details per backend.

**Write pipeline:** Before writing any entry, read `config.backend` and write only to the selected backends. Never write to a backend not in the config. Log failures to `errors.log` and continue — never block on a failed write.

## Skill refinement loop

Every ~15 entries total, review all summaries for strong patterns (>60% concentration in any category).

Three modes — user picks on first trigger, changeable anytime:

| Mode | Behavior |
|------|----------|
| **A — Suggest in chat** *(default)* | "I notice [X% of changes are in 'Maintainability']. Want me to draft a helper skill?" |
| **B — Auto-draft for approval** | Agent drafts the skill silently, then: "I wrote a mini-skill for [pattern]. Save it?" |
| **C — Auto-create** | Agent drafts + saves the skill, then: "I created a skill for [pattern]. It's at [path]." |

Uses `agents/skill-refiner.md` subagent for pattern analysis and skill drafting.

## Development

The root `SKILL.md` is the canonical source. For local development:

- `make init` — Create `.inquisitive/` dirs and init SQLite (if applicable)
- `make sync-skill` — Sync root SKILL.md → `skills/inquisitive/SKILL.md` (preserves YAML frontmatter)
- `make evals` — Run automated eval tests

For end users, `npx skills update inquisitive` pulls the latest from GitHub.

## Error logging

Backend write failures are logged to `.inquisitive/errors.log` (appended with timestamp). Failures never block the write pipeline.

Format: `ISO timestamp | backend | error type + message`

## File locations

### Repo-level (per working repo)

| Resource | Path |
|----------|------|
| Config | `<repo>/.inquisitive/config.json` |
| Entries | `<repo>/.inquisitive/entries/` |
| Summaries | `<repo>/.inquisitive/summaries/` |
| SQLite DB | `<repo>/.inquisitive/inquisitive.db` |
| Error log | `<repo>/.inquisitive/errors.log` |
| Task list | `<repo>/TODO.md` |

### User-level (global personal preferences)

| Resource | Path |
|----------|------|
| Entries | `~/.inquisitive/user/entries/` |
| Summaries | `~/.inquisitive/user/summaries/` |
| SQLite DB | `~/.inquisitive/user/inquisitive.db` |

### Org-level (shared org conventions)

| Resource | Path |
|----------|------|
| Entries | `~/.inquisitive/orgs/<org-slug>/entries/` |
| Summaries | `~/.inquisitive/orgs/<org-slug>/summaries/` |
| SQLite DB | `~/.inquisitive/orgs/<org-slug>/inquisitive.db` |

### Global config

| Resource | Path |
|----------|------|
| Global config | `~/.inquisitive/config.json` |
| Known org slugs | Listed in global config `orgs` array |

### Skill resources (read-only, installed with skill)

| Resource | Path |
|----------|------|
| Personalities | `personalities/inquisitive.md`, `george.md`, `phoebe.md` |
| Question templates | `references/question-templates.md` |
| Category guide | `references/category-guide.md` |
| Task tracking ref | `references/task-tracking.md` |
| Context loader agent | `agents/context-loader.md` |
| Refiner subagent | `agents/skill-refiner.md` |
| Storage docs | `storage/adapters.md` |
| SQLite script | `scripts/inquisitive-sqlite.py` |

## Example workflow

```
User: "Actually, don't use a table for the pricing section — use cards instead."

Agent: [detects change from proposal → user's choice]
[Activates inquisitive skill]
[Loads .inquisitive/config.json → backend: md-sqlite, personality: inquisitive]

> Primary question:
> "What was the primary motivation behind this change? I suggested a table layout
> for the pricing section, but you chose cards. What didn't fit about the table,
> and what made cards the better option?"

User: "Tables feel too spreadsheet-like for pricing. Cards let me add visual
       hierarchy — feature badges, callout buttons, spacing."

Agent: [classifies scope: repo (no cross-repo signals)]
       [categorizes: primary=styling-layout, secondary=ux]
       [writes .md entry + SQLite row to .inquisitive/]
       [updates .inquisitive/summaries/styling-layout.md]

> "Quick follow-ups — just say 'skip' to any:
> 1. Criticality (1-5)? **4**
> 2. Planned or reactive? **reactive — saw the table and knew cards would look better**
> 3. Side effects? **need to adjust the breakpoint logic for mobile**
> 4. Worth encoding as a skill? **maybe for this project's design system**"

Agent: [stores full entry, updates summary for styling-layout category]
       [revisits this preference next time a pricing section is proposed]
```

## Related skills

- `skill-creator` — For formal skill creation with eval loops if the user wants to go beyond a quick refinement skill
- `todo-manager` — For tracking inquisitive-driven improvement tasks
