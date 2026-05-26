# Task Tracking Reference

How inquisitive identifies, delegates, and records tasks discovered during scans or sessions.

## Delegation order

When inquisitive identifies a task, it checks in order:

### 1. Loaded skill list (preferred)
Check the agent's system prompt for any of these skill names:
- `todo-add`
- `todo-check`
- `todo-manager`

If present → load and invoke that skill to add the task. Follow that skill's format and workflow entirely.

### 2. Filesystem fallback
If the system prompt skill list is unavailable (non-OpenCode agents), glob for:
```
~/.agents/skills/todo-*/SKILL.md
~/.opencode/skills/todo-*/SKILL.md
~/.config/opencode/skills/todo-*/SKILL.md
.opencode/skills/todo-*/SKILL.md
```
If any match → read the SKILL.md and follow its instructions.

### 3. MCP tool fallback
If an MCP tool named `todo`, `tasks`, `linear`, or `github_issues` is available in the tool list → use it to create the task.

### 4. Direct write to TODO.md
If none of the above are available → write directly to `TODO.md` in the repo root.

---

## TODO.md format (fallback)

### File structure
```markdown
# TODO

## Priority: High

- [ ] Task description
  - **Context:** Why inquisitive flagged this
  - **Validation Criteria:** How to confirm it's done
  - **Created:** YYYY-MM-DD

## Priority: Medium

- [ ] Task description
  - **Context:** ...
  - **Validation Criteria:** ...
  - **Created:** YYYY-MM-DD

## Priority: Low

- [ ] Task description
  - **Context:** ...
  - **Validation Criteria:** ...
  - **Created:** YYYY-MM-DD
```

### Rules
- If `TODO.md` exists, **append** to the appropriate priority section — never overwrite
- If a priority section heading doesn't exist, create it
- If `TODO.md` doesn't exist, create it with `# TODO` header
- Omit `**Context:**` only if there is genuinely no useful context
- Never omit `**Validation Criteria:**` or `**Created:**`
- Always use today's date in `YYYY-MM-DD` format

### Priority assignment
| Priority | When |
|----------|------|
| High | Security gap, blocking issue, data integrity risk |
| Medium | Missing tests, stale docs, unclear patterns, dead code *(default)* |
| Low | Cosmetic, style, nice-to-have cleanup |

---

## Batching behavior

- **Never** add tasks one-by-one mid-scan or mid-question
- Collect all identified tasks, then write them all at the end of the scan/session
- After writing, notify the user with a summary (see SKILL.md § Task tracking)

---

## Example tasks inquisitive might identify

| Finding | Task | Priority |
|---------|------|----------|
| No test files found | Add unit tests for core modules | Medium |
| README missing usage section | Add usage examples to README | Medium |
| Hardcoded API key in config | Move secrets to environment variables | High |
| Deprecated dependency in package.json | Upgrade `[dep]` to current version | Medium |
| Dead code in `utils/` | Remove unused functions in `utils/helpers.js` | Low |
| No error handling on external calls | Add try/catch to all external API calls | High |
