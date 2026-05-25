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
- **Dual personality** — Professional mode (detailed, articulate) or Pug mode (token-efficient, fun — George or Phoebe)
- **Multiple storage backends** — JSON, Markdown (Obsidian-friendly), SQLite (with 25-line CLI script), optional Milvus
- **Auto-refining summaries** — Every 10 entries per category, the skill reviews, consolidates, and prunes memory
- **Sub-skill generation** — When strong patterns emerge, suggests/drafts/auto-creates refinement skills
- **Bootstrap repo scan** — Seeds understanding on first run in a new repo

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

List available skills without installing:
```bash
npx skills add coma-toast/inquisitive --list
```

### Option 2: Clone and Symlink

```bash
git clone https://github.com/coma-toast/inquisitive.git ~/git/inquisitive
ln -s ~/git/inquisitive ~/.agents/skills/inquisitive
```

### Optional: SQLite backend

After installing, initialize the SQLite backend for queryable memory:

```bash
cd ~/git/inquisitive
python scripts/inquisitive-sqlite.py init
```

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
| "George mode" | Switch to George the Pug personality |
| "Phoebe mode" | Switch to Phoebe the Pug personality |
| "Professional mode" | Switch to professional personality |

## How it works

```
User adjusts agent's work
  → Inquisitive detects the gap (suggestion vs. choice)
  → Asks targeted "why" question
  → Categorizes answer into memory
  → Updates summaries (auto-refined every 10 entries/category)
  → Every ~15 entries: checks for patterns
  → Pattern found? Suggests/drafts/creates a refinement skill
```

## Storage

| Backend | Location | Active by default |
|---------|----------|------------------|
| JSON | `data/memory/entries/*.json` + `index.json` | Yes |
| Markdown | `data/memory/entries/*.md` | Yes |
| SQLite | `data/memory/inquisitive.db` | On `init` |
| Milvus | Via researcher subagent | Optional |

## License

MIT
