# Inquisitive — Learn from Every Adjustment

A meta-skill that makes the agent curious about user intent. Every time the user adjusts something the agent proposed, inquisitive figures out why the original suggestion missed the mark so the agent gets it right on the first try next time.

## What I do

- **Analyze changes** — After every user-initiated file edit or plan modification, analyze what was requested vs. what the agent proposed
- **Ask targeted questions** — Ask context-aware "why" questions that close the learning loop between the agent's suggestion and the user's choice
- **Categorize answers** — Classify into 12 categories with hierarchical intent tracking (company → repo → task)
- **Build memory** — Store answers in multiple backends (JSON, Markdown, SQLite, optionally Milvus)
- **Refine summaries** — Every 10 entries per category, review, consolidate, prune, and update the evolving understanding
- **Create sub-skills** — When strong patterns emerge, suggest, draft, or auto-create refinement skills (user's choice of 3 modes)

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

## Frequency control

On first activation, explain the value and ask:
> "To get it right on the first try, I want to learn from every adjustment. Asking about changes builds a better model of your preferences so I make fewer wrong guesses. How often should I ask?
> **1. Every change** — fastest learning, more questions
> **2. Major changes only** *(default)* — balanced
> **3. Rarely** — minimal interruptions, slower learning"

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
- `company`: The broad business/organizational goal
- `repo`: What this specific project/repo aims to do
- `task`: What the current change is trying to accomplish

## Bootstrap repo scan

On first activation in a new repo:
> "New repo for me! I can scan the project to find inconsistencies or unclear areas and ask about them — this seeds my understanding faster so I make fewer wrong guesses. Also, pick a personality:
> - **Inquisitive** *(professional)* — clear, articulate questions
> - **George** — curious black male pug, short sentences
> - **Phoebe** — curious fawn female pug, same as George
>
> Want me to scan? And which personality?"

If scan accepted:
1. Scan README, configs, package files, directory structure, key source files
2. Identify inconsistencies, ambiguous intent, unclear design patterns
3. Ask up to **3 questions per category** (max ~15 per session)
4. Seed initial memory entries + summaries

Manual trigger: `/inquisitive-scan` or "run the repo scan again"

## Memory architecture

### Layer 1: Individual entries (append-only log)
Every question → answer → categorization → stored as an entry file.

Entry schema:
```json
{
  "id": "2026-05-25-143022",
  "timestamp": "2026-05-25T14:30:22-04:00",
  "project": "inquisitive",
  "file_changed": "SKILL.md",
  "original_suggestion": "description of what agent proposed",
  "user_choice": "description of what user chose instead",
  "primary_category": "intent",
  "secondary_category": "ux",
  "criticality": 3,
  "was_planned": true,
  "side_effects": "none",
  "skill_refinement_signal": false,
  "raw_answer": "full answer from user",
  "personality": "inquisitive"
}
```

### Layer 2: Summaries (curated knowledge)
Each category has a file in `data/summaries/<category>.json`:
```json
{
  "category": "intent",
  "summary": "Continuously refined understanding of user's intent...",
  "hierarchy": {
    "company": "Generate leads from devs visiting docs",
    "repo": "Convert readers into trial users",
    "task": "Fix CTA position above fold"
  },
  "entries": ["id1", "id2", "id3"],
  "entry_count": 3,
  "last_refined": "2026-05-25T14:30:22-04:00"
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

## Skill refinement loop

Every ~15 entries total, review all summaries for strong patterns (>60% concentration in any category).

Three modes — user picks on first trigger, changeable anytime:

| Mode | Behavior |
|------|----------|
| **A — Suggest in chat** *(default)* | "I notice [X% of changes are in 'Maintainability']. Want me to draft a helper skill?" |
| **B — Auto-draft for approval** | Agent drafts the skill silently, then: "I wrote a mini-skill for [pattern]. Save it?" |
| **C — Auto-create** | Agent drafts + saves the skill, then: "I created a skill for [pattern]. It's at [path]." |

Uses `agents/skill-refiner.md` subagent for pattern analysis and skill drafting.

## Storage backends

| Tier | Format | Location | Activation |
|------|--------|----------|------------|
| **Simple** | JSON files + index | `data/memory/entries/*.json`, `data/memory/index.json` | Always active |
| **Readable** | YAML-frontmatter Markdown | `data/memory/entries/*.md` | Always active |
| **Structured** | SQLite | `data/memory/inquisitive.db` | One-time setup (`init`), then always on |
| **Advanced** | Milvus vector DB | Via researcher subagent | Optional — configurable |

See `storage/adapters.md` for detailed documentation of each backend.

### SQLite CLI
A helper script at `scripts/inquisitive-sqlite.py` provides three commands:
```bash
python scripts/inquisitive-sqlite.py init                          # Create tables
python scripts/inquisitive-sqlite.py insert '{"id":"...", ...}'   # Insert an entry
python scripts/inquisitive-sqlite.py query "SELECT * FROM entries" # Query entries
```

This is optional — the skill works without it.

## Development

The root `SKILL.md` is the canonical source. For local development:

- `make init` — Create data dirs and init SQLite
- `make sync-skill` — Sync root SKILL.md → `skills/inquisitive/SKILL.md` (preserves YAML frontmatter)
- `make evals` — Run automated eval tests

For end users, `npx skills update inquisitive` pulls the latest from GitHub.

## Error logging

Backend write failures are logged to `data/memory/errors.log` (appended with timestamp). Failures never block the write pipeline.

## Entry persistence rules

When writing an entry, write to **all active backends** in parallel:
- JSON file + update index.json
- Markdown file
- SQLite (if initialized)
- Milvus (if configured)

Error handling: if one backend fails, log the error and continue with the others. Never block on a failed backend.

## File locations (all relative to skill root `~/.agents/skills/inquisitive/`)

| Resource | Path |
|----------|------|
| Personalities | `personalities/inquisitive.md`, `george.md`, `phoebe.md` |
| Question templates | `references/question-templates.md` |
| Category guide | `references/category-guide.md` |
| Refiner subagent | `agents/skill-refiner.md` |
| Storage docs | `storage/adapters.md` |
| SQLite script | `scripts/inquisitive-sqlite.py` |
| Memory index | `data/memory/index.json` |
| Memory entries | `data/memory/entries/` |
| Category summaries | `data/summaries/<category>.json` |

## Example workflow

```
User: "Actually, don't use a table for the pricing section — use cards instead."

Agent: [detects change from proposal → user's choice]
[Activates inquisitive skill]

> Primary question:
> "What was the primary motivation behind this change? I suggested a table layout
> for the pricing section, but you chose cards. What didn't fit about the table,
> and what made cards the better option?"

User: "Tables feel too spreadsheet-like for pricing. Cards let me add visual
       hierarchy — feature badges, callout buttons, spacing."

Agent: [categorizes as: primary=styling-layout, secondary=ux]
       [stores entry + updates summary]

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
