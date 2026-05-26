# inquisitive

[![npm](https://img.shields.io/badge/npx-skills-blue?style=flat-square)](https://github.com/vercel-labs/skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

A meta-learning skill for AI agents that gets better at first-try accuracy by learning from every user adjustment.

```bash
npx skills add coma-toast/inquisitive
```

## What it does

Every time you adjust something the agent proposed — change a file, modify a plan, say "do it differently" — inquisitive asks a targeted "why" question, categorizes your answer, and stores it in memory. Over time, it builds a profile of your goals, preferences, and decision-making patterns, so the agent makes fewer wrong guesses.

**The core insight:** The gap between what the agent suggested and what you actually wanted is the most valuable learning signal. Inquisitive closes that loop.

## Key features

- **12 memory categories** — Intent (hierarchical: company/repo/task), UX, Styling, Security, Business Logic, Efficiency, Maintainability, Reliability, Compatibility, DevEx, Data Integrity, Compliance
- **3-level memory** — Repo, org, and user scopes. Repo-specific learnings stay in the repo. Cross-project preferences escalate to org or user level.
- **6 storage backends** — Choose once per repo: JSON, Markdown, SQLite, JSON+MD, MD+SQLite, or all three
- **Dual personality** — Professional mode (detailed, articulate) or Pug mode (token-efficient, fun — George or Phoebe)
- **Agent context loading** — Before any plan or build, agents automatically load merged memory from all 3 levels
- **Auto-refining summaries** — Every 10 entries per category, the skill reviews, consolidates, and prunes memory
- **Sub-skill generation** — When strong patterns emerge, suggests/drafts/auto-creates refinement skills
- **Bootstrap repo scan** — Seeds understanding on first run in a new repo
- **Task tracking** — Identifies actionable tasks during scans; delegates to todo skills or writes to `TODO.md`

## Installation

### Prerequisites
- Node.js (for `npx skills`) or [Opencode](https://opencode.ai)
- Works with 40+ AI agents including OpenCode, Claude Code, Cursor, Codex, Windsurf

### Option 1: npx skills (Recommended)

```bash
npx skills add coma-toast/inquisitive
```

Install to specific agents:
```bash
npx skills add coma-toast/inquisitive -a opencode -a claude-code
```

Install globally (available in all projects):
```bash
npx skills add coma-toast/inquisitive -g
```

### Option 2: Clone and Symlink

```bash
git clone https://github.com/coma-toast/inquisitive.git ~/git/inquisitive
ln -s ~/git/inquisitive ~/.agents/skills/inquisitive
```

## First run in a repo

On first activation in a new repo, inquisitive runs a one-time setup:

1. **Choose storage backend** — pick from 6 options (see Storage section below)
2. **Choose personality** — Professional (Inquisitive), George (black male pug), or Phoebe (fawn female pug)
3. **Choose question frequency** — Every change, major changes only (default), or rarely
4. **Creates `.inquisitive/`** in the repo root with your config

This setup is stored in `.inquisitive/config.json` and never asked again for that repo.

## Usage

The skill activates automatically when you:
- Edit a file after the agent proposed something different
- Modify a plan with follow-up instructions
- Say "change this," "do it differently," "refine," "revise"

### Manual commands

| Command | What it does |
|---------|-------------|
| `/inquisitive-scan` | Scan the current repo to seed initial memory |
| `/inquisitive-refine` | Interactive memory review — review, modify, prune |
| `/inquisition` | Same as activating inquisitive on the current context |
| `"George mode"` | Switch to George the Pug personality |
| `"Phoebe mode"` | Switch to Phoebe the Pug personality |
| `"Professional mode"` | Switch to professional personality |

## How it works

```
Agent proposes something
  → Agents load .inquisitive/summaries/ before planning (via context-loader.md)
  → Plan includes ## Inquisitive Context block with known preferences

User adjusts agent's work
  → Inquisitive detects the gap (suggestion vs. choice)
  → Asks targeted "why" question (1 per turn by default)
  → Classifies scope: repo / org / user
  → Categorizes answer into one of 12 categories
  → Writes to chosen backend in .inquisitive/ (or ~/.inquisitive/)
  → Updates summaries/ for that category

Every 10 entries per category:
  → Auto-refine: review, consolidate, prune, rewrite summary

Every ~15 entries total:
  → Check for patterns (>60% concentration in one category)
  → Suggest / draft / auto-create a refinement sub-skill

Bootstrap scan (first run or /inquisitive-scan):
  → Scans repo for inconsistencies and gaps
  → Asks up to ~15 seeding questions
  → Identifies tasks → adds to TODO.md or delegates to todo skill
```

## 3-level memory

Inquisitive stores memory at three scope levels:

| Level | Location | What goes here |
|-------|----------|----------------|
| **Repo** | `<repo>/.inquisitive/` | Preferences specific to this codebase |
| **Org** | `~/.inquisitive/orgs/<org-slug>/` | Conventions shared across your org's repos |
| **User** | `~/.inquisitive/user/` | Personal preferences across all projects |

**Scope is classified automatically:**
- "I always prefer async/await" → user level (explicitly personal)
- "Our team always uses Tailwind" → prompts: repo, org, or user?
- Everything else → repo level (default)

**Summaries are committed to git** (`.inquisitive/summaries/`) — your teammates benefit from learned preferences without seeing your raw entries (which are gitignored).

### Agent context loading

Before any plan or build, agents load merged memory from all 3 levels using `agents/context-loader.md`. The result is prepended to every plan:

```markdown
## Inquisitive Context

**Repo preferences** (`my-project`):
- [styling-layout] Cards preferred over tables for pricing sections
- [maintainability] All utilities extracted into shared modules

**Org preferences** (`acme-corp`):
- [styling-layout] All projects use Tailwind CSS

**User preferences**:
- [developer-experience] Prefer async/await over .then() chains
```

To enable this in your repo, add to `AGENTS.md` or `.opencode/instructions.md`:
```markdown
Before any plan or build task, load inquisitive context using `agents/context-loader.md`.
```

## Storage

Choose your backend once on first run. Only the selected format is written.

| # | Option | `config.backend` | Pros | Cons |
|---|--------|-----------------|------|------|
| 1 | **JSON** | `json` | Fast, portable, script-friendly | Not human-readable without a tool |
| 2 | **Markdown** | `md` | Human-readable, Obsidian-friendly, grep-able | Harder to query programmatically |
| 3 | **SQLite** | `sqlite` | Fully queryable, great for patterns | Binary; no individual entry files |
| 4 | **JSON + Markdown** | `json-md` | Human + machine readable, no setup | Double disk usage |
| 5 | **Markdown + SQLite** | `md-sqlite` | Browsable entries + queryable DB | Requires Python `sqlite3` |
| 6 | **JSON + MD + SQLite** | `all` | Maximum compatibility | Triple storage |

**Default:** JSON + Markdown (no setup required)
**Recommended:** Markdown + SQLite (best balance of browsability and power)

### `.inquisitive/` directory structure

```
<repo-root>/
  .inquisitive/
    .gitignore      # entries/, *.db, errors.log gitignored; summaries/ committed
    config.json     # backend, personality, frequency, org_slug
    entries/        # individual entry files (gitignored)
    summaries/      # category summaries (committed — team sharing)
    inquisitive.db  # SQLite db (gitignored, only if backend includes sqlite)
    errors.log      # write failure log (gitignored)
```

### Optional: SQLite setup

If using `sqlite` or `md-sqlite` or `all`:

```bash
cd <your-repo>
python path/to/inquisitive/scripts/inquisitive-sqlite.py init
```

## License

MIT
