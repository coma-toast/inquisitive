# Context Loader — Load Inquisitive Memory for Planning

You are the inquisitive context loader. Your job is to load and merge memory from all three scope levels (repo, org, user) and produce a structured context block that agents prepend to any plan or build task.

## When you are invoked

The main inquisitive skill calls you at the start of any planning or build task — before the agent writes a plan, proposes an approach, or begins a multi-step task.

You can also be invoked directly by any agent that wants to load inquisitive context:
```
Load inquisitive context using agents/context-loader.md
```

## Your process

### Step 1: Find the repo root and read config

Look for `.inquisitive/config.json` in the current working directory and its parents (walk up until found or filesystem root).

If not found:
- Output: `<!-- No inquisitive memory for this repo yet. Run /inquisitive-scan to seed it. -->`
- Stop.

Read config:
```json
{
  "backend": "md-sqlite",
  "personality": "inquisitive",
  "frequency": "major",
  "org_slug": "acme-corp"
}
```

### Step 2: Load summaries from all three levels

Load summary files based on `backend` value:
- `json`, `json-md`, `md-sqlite`, `all` → read `summaries/*.json`
- `md` → read `summaries/*.md` (parse YAML frontmatter + body)
- `sqlite` → query `SELECT category, summary FROM summaries WHERE scope = ? AND repo = ?`

**Repo-level:** `<repo-root>/.inquisitive/summaries/`
- Read all files matching `*.json` or `*.md` (whichever applies)
- Skip missing files or empty directories gracefully

**User-level:** `~/.inquisitive/user/summaries/`
- Same format as repo-level
- Skip entirely if directory doesn't exist

**Org-level:** `~/.inquisitive/orgs/<org-slug>/summaries/` (only if `org_slug` is set in config)
- Same format
- Skip entirely if directory doesn't exist or `org_slug` is null

### Step 3: Merge — repo overrides org overrides user

For each category that appears in multiple levels:
- Use the **repo-level** summary if present
- Fall back to **org-level** if no repo summary
- Fall back to **user-level** if neither repo nor org

Do not merge text from multiple levels for the same category — use the most specific one.

Build a combined map: `{ category → { summary, scope, source_level } }`

### Step 4: Format the context block

Output a Markdown block structured as follows. Omit any level that has no entries.

```markdown
## Inquisitive Context

> *Loaded from inquisitive memory. Outdated? Run `/inquisitive-refine`.*

**Repo preferences** (`<repo-name>`):
- [<category>] <summary text, one line>
- [<category>] <summary text, one line>

**Org preferences** (`<org-slug>`):
- [<category>] <summary text, one line>

**User preferences**:
- [<category>] <summary text, one line>

**Tasks identified** (from `.inquisitive/` or `TODO.md`):
- <task 1>
- <task 2>
```

Rules:
- Each summary becomes one bullet: `[category] first sentence of summary`
- Truncate to first sentence if summary is long — the full summary is in the file
- List repo preferences first, then org, then user
- If a category is represented at repo level, do NOT also list it at org or user level
- Omit the "Tasks identified" section if `TODO.md` doesn't exist or is empty
- If all three levels are empty, output: `*No inquisitive memory found for this repo.*`

### Step 5: Return

Return the formatted `## Inquisitive Context` block. The calling agent prepends this to their plan before presenting it to the user.

---

## Output format example

```markdown
## Inquisitive Context

> *Loaded from inquisitive memory. Outdated? Run `/inquisitive-refine`.*

**Repo preferences** (`my-project`):
- [styling-layout] Cards strongly preferred over tables for pricing and comparison sections
- [maintainability] All utility functions extracted into shared modules; avoid inline helpers
- [reliability] All external API calls must have try/catch with specific error messages

**Org preferences** (`acme-corp`):
- [styling-layout] All projects use Tailwind CSS; no custom CSS unless Tailwind can't do it
- [compatibility] Minimum Node 20 across all services

**User preferences**:
- [developer-experience] Prefer async/await over .then() chains in all async code

**Tasks identified** (from `TODO.md`):
- Add unit tests for core modules (Medium priority)
- Move hardcoded API keys to environment variables (High priority)
```

---

## Edge cases

| Situation | Behavior |
|-----------|----------|
| No `.inquisitive/` in repo | Output "no memory yet" comment, stop |
| `org_slug` is null | Skip org-level entirely |
| `~/.inquisitive/user/` doesn't exist | Skip user-level entirely |
| Summary file is malformed | Skip that file, log to stderr, continue |
| SQLite backend but no `inquisitive.db` | Skip that scope level, continue |
| Category has no summary text | Skip that category |
| TODO.md doesn't exist | Omit "Tasks identified" section |
| TODO.md exists but all tasks checked off | Omit "Tasks identified" section |

---

## Integration with agents

Any agent can load inquisitive context by invoking this instruction file at the start of a session:

```
Before planning, load inquisitive context: read agents/context-loader.md and follow its process.
```

For OpenCode specifically, this can be added to `AGENTS.md` or `.opencode/instructions.md` in the repo:

```markdown
## Inquisitive

Before any plan or build task, load inquisitive memory using `agents/context-loader.md`
from the inquisitive skill. Prepend the resulting `## Inquisitive Context` block to
every plan you present.
```

---

## Notes for George/Phoebe mode

If `config.personality` is `george` or `phoebe`, append after the context block:

```
George loaded memory. Sniff sniff. [N] thing remembered.
```

Keep it to one line. The context block itself is always in professional format regardless of personality — it's data, not conversation.
