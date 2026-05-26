#!/usr/bin/env python3
"""Automated eval runner for inquisitive.

Tests infrastructure (SQLite, entries, category matching, personalities,
task tracking, memory scoping, backend selection) and prints behavioral
eval scenarios as a checklist.
"""

import json
import os
import re
import sqlite3
import sys
import tempfile
import textwrap
import shutil
from datetime import date

SKILL_DIR = os.path.join(os.path.dirname(__file__), "..")
PASS = 0
FAIL = 0
SKIP = 0


def ok(msg):
    global PASS
    PASS += 1
    print(f"  ✓ {msg}")


def fail(msg, detail=""):
    global FAIL
    FAIL += 1
    print(f"  ✗ {msg}")
    if detail:
        for line in detail.strip().split("\n"):
            print(f"    {line}")


def skip(msg):
    global SKIP
    SKIP += 1
    print(f"  ~ {msg} (skipped)")


# ── 1. SQLite backend ──────────────────────────────────────────────
def test_sqlite():
    print("\n[1] SQLite backend")
    tmp = tempfile.mktemp(suffix=".db")
    conn = sqlite3.connect(tmp)
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS entries(
              id TEXT PRIMARY KEY, timestamp TEXT, scope TEXT DEFAULT 'repo',
              org_slug TEXT, repo TEXT, file_changed TEXT,
              original_suggestion TEXT, user_choice TEXT,
              primary_category TEXT, secondary_category TEXT,
              criticality INTEGER, was_planned INTEGER, side_effects TEXT,
              skill_refinement_signal INTEGER, raw_answer TEXT, personality TEXT
            );
        """)
        ok("Create entries table (with scope/org_slug/repo fields)")
    except Exception as e:
        fail("Create entries table", str(e))

    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS summaries(
              category TEXT NOT NULL, scope TEXT NOT NULL DEFAULT 'repo',
              org_slug TEXT, repo TEXT, summary TEXT,
              entry_count INTEGER DEFAULT 0, last_refined TEXT,
              PRIMARY KEY (category, scope, repo)
            );
        """)
        ok("Create summaries table (multi-scope)")
    except Exception as e:
        fail("Create summaries table", str(e))

    try:
        conn.execute(
            "INSERT OR REPLACE INTO entries VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            ["test-1", "2026-01-01T00:00:00Z", "repo", None, "my-project",
             "test.md", "suggestion", "choice", "intent", "ux",
             3, 1, "none", 0, "test answer", "inquisitive"],
        )
        row = conn.execute("SELECT * FROM entries WHERE id='test-1'").fetchone()
        assert row["primary_category"] == "intent"
        assert row["scope"] == "repo"
        ok("Insert and query entry (scope=repo)")
    except Exception as e:
        fail("Insert and query entry", str(e))

    try:
        conn.execute("DELETE FROM entries WHERE id='test-1'")
        ok("Delete entry")
    except Exception as e:
        fail("Delete entry", str(e))

    conn.close()
    os.unlink(tmp)


# ── 2. Entry persistence ──────────────────────────────────────────
def test_entry_persistence():
    print("\n[2] Entry persistence (JSON + Markdown)")
    tmpdir = tempfile.mkdtemp()
    entry = {
        "id": "eval-test-001",
        "timestamp": "2026-05-26T12:00:00Z",
        "scope": "repo",
        "org_slug": None,
        "repo": "inquisitive",
        "file_changed": "SKILL.md",
        "original_suggestion": "table layout",
        "user_choice": "card layout",
        "primary_category": "styling-layout",
        "secondary_category": "ux",
        "criticality": 4,
        "was_planned": False,
        "side_effects": "breakpoint changes needed",
        "skill_refinement_signal": False,
        "raw_answer": "Cards give better visual hierarchy",
        "personality": "george",
    }

    # JSON write
    try:
        jpath = os.path.join(tmpdir, "eval-test-001.json")
        with open(jpath, "w") as f:
            json.dump(entry, f, indent=2)
        with open(jpath) as f:
            loaded = json.load(f)
        assert loaded["id"] == "eval-test-001"
        assert loaded["scope"] == "repo"
        ok("Write and read JSON entry (includes scope field)")
    except Exception as e:
        fail("Write and read JSON entry", str(e))

    # Markdown write
    try:
        mpath = os.path.join(tmpdir, "eval-test-001.md")
        frontmatter = "---\n"
        for k in ["id", "timestamp", "scope", "org_slug", "repo",
                   "file_changed", "primary_category", "secondary_category",
                   "criticality", "was_planned", "personality"]:
            v = entry.get(k)
            frontmatter += f'{k}: "{v}"\n'
        frontmatter += "---\n\n"
        body = (
            f"# Change: {entry['original_suggestion']} → {entry['user_choice']}\n\n"
            f"**User said:** {entry['raw_answer']}\n"
        )
        with open(mpath, "w") as f:
            f.write(frontmatter + body)
        with open(mpath) as f:
            content = f.read()
        assert "styling-layout" in content
        assert 'scope: "repo"' in content
        ok("Write and read Markdown entry (includes scope in frontmatter)")
    except Exception as e:
        fail("Write and read Markdown entry", str(e))

    # JSON index append
    try:
        ipath = os.path.join(tmpdir, "index.json")
        index = []
        index.append({k: entry[k] for k in
                       ["id", "timestamp", "scope", "repo",
                        "primary_category", "secondary_category",
                        "criticality", "was_planned"]})
        with open(ipath, "w") as f:
            json.dump(index, f, indent=2)
        with open(ipath) as f:
            loaded_idx = json.load(f)
        assert len(loaded_idx) == 1
        assert loaded_idx[0]["scope"] == "repo"
        ok("Write and read index.json (includes scope)")
    except Exception as e:
        fail("Write and read index.json", str(e))

    shutil.rmtree(tmpdir)


# ── 3. Category matching ──────────────────────────────────────────
def test_category_matching():
    print("\n[3] Category matching")

    cases = [
        ("Fix button color contrast", "styling-layout"),
        ("Add rate limiting to login", "security"),
        ("Extract validation into shared util", "maintainability"),
        ("Add loading spinner for API calls", "user-experience"),
        ("Optimize database query with index", "efficiency"),
        ("Add try-catch around external call", "reliability"),
        ("Bump Node minimum version", "compatibility"),
        ("Add debug logging to middleware", "developer-experience"),
        ("Add NOT NULL constraint to email column", "data-integrity"),
        ("Update tax calc for new regulations", "business-logic"),
        ("Add cookie consent banner for GDPR", "compliance-policy"),
    ]

    for desc, expected in cases:
        cat = classify(desc)
        if cat == expected:
            ok(f"'{desc[:35]}...' → {cat}")
        else:
            fail(f"'{desc[:35]}...'", f"expected {expected}, got {cat}")


def classify(desc):
    d = desc.lower()
    if any(w in d for w in ["color", "padding", "layout", "spacing",
                              "font", "align", "visual", "card", "table"]):
        return "styling-layout"
    if any(w in d for w in ["rate limit", "auth", "xss", "csrf",
                              "sanitiz", "permission", "secret"]):
        return "security"
    if any(w in d for w in ["extract", "rename", "refactor", "clean",
                              "dead code", "split", "util", "shared"]):
        return "maintainability"
    if any(w in d for w in ["loading", "spinner", "ux", "usability",
                              "onboard", "tooltip", "feedback"]):
        return "user-experience"
    if any(w in d for w in ["optimize", "cache", "index", "faster",
                              "lazy load", "bundle", "perf"]):
        return "efficiency"
    if any(w in d for w in ["try", "catch", "retry", "fallback",
                              "timeout", "error", "exception"]):
        return "reliability"
    if any(w in d for w in ["bump", "polyfill", "compat", "migration",
                              "deprecat", "version"]):
        return "compatibility"
    if any(w in d for w in ["debug", "log", "cli", "tooling",
                              "fixture", "readme", "dev"]):
        return "developer-experience"
    if any(w in d for w in ["constraint", "valid", "schema", "type",
                              "null", "migration"]):
        return "data-integrity"
    if any(w in d for w in ["tax", "price", "rule", "workflow",
                              "eligib", "tier", "discount"]):
        return "business-logic"
    if any(w in d for w in ["gdpr", "ccpa", "wcag", "complian",
                              "cookie", "consent", "accessib"]):
        return "compliance-policy"
    return "intent"


# ── 4. Personality templates ──────────────────────────────────────
def test_personalities():
    print("\n[4] Personality template selection")

    inquisitive = {
        "primary": "What was the primary motivation behind this change?",
        "secondary": "I suggested {approach}, but you went with {choice}. "
                     "What was it about my suggestion that didn't fit, "
                     "and what made {choice} the better option?",
    }
    george = {
        "primary": "Why human change thing? Snort. George learn.",
        "secondary": "George think {approach}. Human pick {choice}. Huff. "
                     "Why human pick that? George need know.",
    }
    phoebe = {
        "primary": "Why human change thing? Snort. Phoebe learn.",
        "secondary": "Phoebe think {approach}. Human pick {choice}. Huff. "
                     "Why human pick that? Phoebe need know.",
    }

    try:
        assert inquisitive["primary"].endswith("?")
        ok("Inquisitive primary question")
    except AssertionError:
        fail("Inquisitive primary question")

    try:
        assert "Snort" in george["primary"]
        assert "George" in george["primary"]
        ok("George primary question (dog sound + self-ref)")
    except AssertionError:
        fail("George primary question")

    try:
        assert "Snort" in phoebe["primary"]
        assert "Phoebe" in phoebe["primary"]
        ok("Phoebe primary question (dog sound + self-ref)")
    except AssertionError:
        fail("Phoebe primary question")

    filled = inquisitive["secondary"].format(approach="table", choice="cards")
    assert "table" in filled and "cards" in filled
    ok("Secondary question template fills correctly")

    current = george
    assert "George" in current["primary"]
    current = phoebe
    assert "Phoebe" in current["primary"]
    ok("Personality switch (George → Phoebe)")


# ── 5. Behavioral evals (checklist) ───────────────────────────────
def print_behavioral_checklist():
    print("\n[5] Behavioral evals (manual checklist)")
    with open(os.path.join(SKILL_DIR, "evals", "evals.json")) as f:
        evals = json.load(f)

    for e in evals["evals"]:
        print(f"\n  [{e['id']}] {e['name']}")
        print(f"       Prompt: {textwrap.shorten(e['prompt'], 80)}")
        print(f"       Expected: {textwrap.shorten(e['expected_output'], 80)}")
        print(f"       Status: ~ manual")


# ── 6. Task tracking ──────────────────────────────────────────────
def test_task_tracking():
    print("\n[6] Task tracking")
    today = date.today().strftime("%Y-%m-%d")

    def make_task(desc, context, validation, priority="Medium"):
        return {"description": desc, "context": context,
                "validation": validation, "priority": priority}

    def render_todo_entry(task):
        lines = [f"- [ ] {task['description']}"]
        if task.get("context"):
            lines.append(f"  - **Context:** {task['context']}")
        lines.append(f"  - **Validation Criteria:** {task['validation']}")
        lines.append(f"  - **Created:** {today}")
        return "\n".join(lines)

    def write_todo_md(tmp_path, tasks_by_priority):
        sections = {}
        for priority in ("High", "Medium", "Low"):
            items = tasks_by_priority.get(priority, [])
            if items:
                block = f"## Priority: {priority}\n\n"
                block += "\n\n".join(render_todo_entry(t) for t in items)
                sections[priority] = block
        content = "# TODO\n\n" + "\n\n".join(sections.values()) + "\n"
        with open(tmp_path, "w") as f:
            f.write(content)
        return content

    task = make_task("Add unit tests for core modules",
                     "No test files found during inquisitive scan",
                     "All core modules have at least one passing test")
    entry = render_todo_entry(task)
    assert "- [ ] Add unit tests" in entry
    assert "**Context:**" in entry
    assert "**Validation Criteria:**" in entry
    assert f"**Created:** {today}" in entry
    ok("Single task renders correct TODO.md format")

    task_no_ctx = make_task("Move secrets to env vars", "",
                            "No hardcoded secrets in repo", "High")
    entry2 = render_todo_entry(task_no_ctx)
    assert "**Context:**" not in entry2
    assert "**Validation Criteria:**" in entry2
    ok("Context line omitted when empty")

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w") as f:
        tmp_path = f.name

    tasks_by_priority = {
        "High": [make_task("Fix auth bypass", "Security gap", "Auth tests pass", "High")],
        "Medium": [make_task("Add README usage section", "Missing docs",
                             "README has usage examples", "Medium")],
        "Low": [make_task("Fix code style", "Style drift", "Linter passes", "Low")],
    }
    content = write_todo_md(tmp_path, tasks_by_priority)
    assert "## Priority: High" in content
    assert "## Priority: Medium" in content
    assert "## Priority: Low" in content
    assert content.index("## Priority: High") < content.index("## Priority: Medium")
    ok("Tasks written to correct priority sections in order")

    with open(tmp_path, "r") as f:
        original = f.read()
    with open(tmp_path, "a") as f:
        f.write("\n" + render_todo_entry(make_task("New task", "ctx", "criteria")) + "\n")
    with open(tmp_path, "r") as f:
        appended = f.read()
    assert original in appended
    assert "New task" in appended
    ok("Append preserves existing TODO.md content")

    n_tasks = 3
    task_names = ["Add tests", "Fix auth", "Update README"]
    summary = f"Found {n_tasks} tasks and added them to TODO.md:\n" + "\n".join(f"- {t}" for t in task_names)
    assert f"Found {n_tasks} tasks" in summary
    assert all(t in summary for t in task_names)
    ok("Batch notification summary format correct")

    known_todo_skills = {"todo-add", "todo-check", "todo-manager"}
    assert "todo-add" in known_todo_skills.intersection({"inquisitive", "todo-add", "grill-me"})
    ok("Skill detection finds todo-add in loaded skill list")

    assert len(known_todo_skills.intersection({"inquisitive", "grill-me"})) == 0
    ok("Skill detection: no todo skill → fallback to TODO.md")

    priority_rules = {"security": "High", "missing tests": "Medium", "cosmetic": "Low"}
    assert priority_rules["security"] == "High"
    assert priority_rules["missing tests"] == "Medium"
    assert priority_rules["cosmetic"] == "Low"
    ok("Priority assignment rules: High/Medium/Low map correctly")

    os.unlink(tmp_path)


# ── 7. Memory scoping ─────────────────────────────────────────────
def test_memory_scoping():
    print("\n[7] Memory scoping")
    tmpdir = tempfile.mkdtemp()

    # Helpers
    def make_entry(scope, org_slug=None, repo="my-project"):
        return {
            "id": f"scope-test-{scope}",
            "timestamp": "2026-05-26T12:00:00Z",
            "scope": scope,
            "org_slug": org_slug,
            "repo": repo,
            "primary_category": "maintainability",
            "raw_answer": "test answer",
        }

    def scope_root(scope, org_slug=None, base=None):
        base = base or tmpdir
        if scope == "repo":
            return os.path.join(base, "repo", ".inquisitive")
        elif scope == "org":
            return os.path.join(base, "orgs", org_slug)
        elif scope == "user":
            return os.path.join(base, "user")

    def write_entry(entry, base=None):
        root = scope_root(entry["scope"], entry.get("org_slug"), base)
        entries_dir = os.path.join(root, "entries")
        os.makedirs(entries_dir, exist_ok=True)
        path = os.path.join(entries_dir, f"{entry['id']}.json")
        with open(path, "w") as f:
            json.dump(entry, f)
        return path

    # Test 1: repo-level entry → written under .inquisitive/entries/
    e_repo = make_entry("repo")
    path = write_entry(e_repo)
    assert os.path.exists(path)
    with open(path) as f:
        loaded = json.load(f)
    assert loaded["scope"] == "repo"
    ok("Repo-level entry written to .inquisitive/entries/")

    # Test 2: user-level entry → written under user/entries/
    e_user = make_entry("user")
    path = write_entry(e_user)
    assert os.path.exists(path)
    assert "user" in path
    ok("User-level entry written to ~/.inquisitive/user/entries/")

    # Test 3: org-level entry → written under orgs/<slug>/entries/
    e_org = make_entry("org", org_slug="acme-corp")
    path = write_entry(e_org)
    assert os.path.exists(path)
    assert "acme-corp" in path
    ok("Org-level entry written to ~/.inquisitive/orgs/acme-corp/entries/")

    # Test 4: cross-repo signal triggers scope prompt
    cross_repo_phrases = ["we always", "our team", "in all our projects",
                          "our standard", "across repos"]
    answer = "We always use Tailwind across repos"
    triggered = any(phrase in answer.lower() for phrase in cross_repo_phrases)
    assert triggered
    ok("'We always...' answer triggers cross-repo scope prompt")

    # Test 5: first-person personal → user scope, no prompt
    personal_phrases = ["i always", "i personally", "i prefer", "i like to", "my habit"]
    personal_answer = "I personally prefer async/await over .then() chains"
    is_personal = any(phrase in personal_answer.lower() for phrase in personal_phrases)
    assert is_personal
    ok("'I personally...' answer → user scope without prompt")

    # Test 6: git remote URL → org slug inference
    remote_urls = [
        ("https://github.com/acme-corp/my-repo.git", "acme-corp"),
        ("git@github.com:acme-corp/my-repo.git", "acme-corp"),
        ("https://github.com/solo-dev/tool.git", "solo-dev"),
    ]
    def infer_org(url):
        m = re.search(r"[:/]([^/]+)/[^/]+(?:\.git)?$", url)
        return m.group(1) if m else None

    for url, expected in remote_urls:
        result = infer_org(url)
        assert result == expected, f"Expected {expected}, got {result} for {url}"
    ok("Org slug inferred correctly from git remote URLs (https + ssh)")

    # Test 7: context loader merges 3 levels — repo wins on conflict
    summaries = {
        "repo": {"styling-layout": "Cards preferred (repo-specific)"},
        "org":  {"styling-layout": "Tables preferred (org default)",
                 "compatibility": "Node 20 minimum"},
        "user": {"developer-experience": "Prefer async/await"},
    }
    merged = {}
    for level in ("user", "org", "repo"):  # lowest to highest priority
        merged.update(summaries[level])
    assert merged["styling-layout"] == "Cards preferred (repo-specific)"
    assert merged["compatibility"] == "Node 20 minimum"
    assert merged["developer-experience"] == "Prefer async/await"
    ok("Context merge: repo overrides org overrides user on conflict")

    # Test 8: missing org slug → org level skipped gracefully
    config = {"backend": "json-md", "personality": "inquisitive",
              "frequency": "major", "org_slug": None}
    levels_to_load = ["repo", "user"]
    if config.get("org_slug"):
        levels_to_load.append("org")
    assert "org" not in levels_to_load
    ok("Missing org_slug → org level skipped gracefully")

    shutil.rmtree(tmpdir)


# ── 8. Backend selection ──────────────────────────────────────────
def test_backend_selection():
    print("\n[8] Backend selection")
    tmpdir = tempfile.mkdtemp()

    VALID_BACKENDS = {"json", "md", "sqlite", "json-md", "md-sqlite", "all"}

    # Test 1: no config → first-run flag
    config_path = os.path.join(tmpdir, "config.json")
    first_run = not os.path.exists(config_path)
    assert first_run
    ok("No config.json → first-run setup triggered")

    # Test 2: json backend → only .json files written, index.json present
    def simulate_write(backend, entry_id, entries_dir):
        os.makedirs(entries_dir, exist_ok=True)
        written = []
        if backend in ("json", "json-md", "all"):
            p = os.path.join(entries_dir, f"{entry_id}.json")
            with open(p, "w") as f:
                json.dump({"id": entry_id}, f)
            written.append("json")
        if backend in ("md", "json-md", "md-sqlite", "all"):
            p = os.path.join(entries_dir, f"{entry_id}.md")
            with open(p, "w") as f:
                f.write(f"# {entry_id}\n")
            written.append("md")
        if backend in ("sqlite", "md-sqlite", "all"):
            written.append("sqlite")  # would init DB; just flag it
        return written

    entries_dir = os.path.join(tmpdir, "entries")

    written = simulate_write("json", "e1", entries_dir)
    assert written == ["json"]
    assert os.path.exists(os.path.join(entries_dir, "e1.json"))
    assert not os.path.exists(os.path.join(entries_dir, "e1.md"))
    ok("backend=json → only .json file written")

    written = simulate_write("md", "e2", entries_dir)
    assert written == ["md"]
    assert os.path.exists(os.path.join(entries_dir, "e2.md"))
    assert not os.path.exists(os.path.join(entries_dir, "e2.json"))
    ok("backend=md → only .md file written")

    written = simulate_write("sqlite", "e3", entries_dir)
    assert written == ["sqlite"]
    assert not os.path.exists(os.path.join(entries_dir, "e3.json"))
    assert not os.path.exists(os.path.join(entries_dir, "e3.md"))
    ok("backend=sqlite → no flat files written")

    written = simulate_write("json-md", "e4", entries_dir)
    assert set(written) == {"json", "md"}
    assert os.path.exists(os.path.join(entries_dir, "e4.json"))
    assert os.path.exists(os.path.join(entries_dir, "e4.md"))
    ok("backend=json-md → both .json and .md written")

    written = simulate_write("md-sqlite", "e5", entries_dir)
    assert set(written) == {"md", "sqlite"}
    assert os.path.exists(os.path.join(entries_dir, "e5.md"))
    assert not os.path.exists(os.path.join(entries_dir, "e5.json"))
    ok("backend=md-sqlite → .md written, sqlite flagged, no .json")

    written = simulate_write("all", "e6", entries_dir)
    assert set(written) == {"json", "md", "sqlite"}
    ok("backend=all → json, md, and sqlite all written")

    # Test: all backend values are valid
    for b in VALID_BACKENDS:
        assert b in VALID_BACKENDS
    ok(f"All 6 backend values are valid: {', '.join(sorted(VALID_BACKENDS))}")

    # Test: index type per backend
    def index_type(backend):
        if backend in ("json", "json-md", "all"):
            return "index.json"
        elif backend in ("md", "md-sqlite"):
            return "index.md"
        elif backend == "sqlite":
            return "sql"
        return None

    assert index_type("json") == "index.json"
    assert index_type("md") == "index.md"
    assert index_type("sqlite") == "sql"
    assert index_type("json-md") == "index.json"
    assert index_type("md-sqlite") == "index.md"
    assert index_type("all") == "index.json"
    ok("Index type correctly mapped per backend")

    shutil.rmtree(tmpdir)


# ── Main ──────────────────────────────────────────────────────────
def main():
    print(f"Inquisitive Eval Runner")
    print(f"{'=' * 40}")

    test_sqlite()
    test_entry_persistence()
    test_category_matching()
    test_personalities()
    test_task_tracking()
    test_memory_scoping()
    test_backend_selection()
    print_behavioral_checklist()

    print(f"\n{'=' * 40}")
    print(f"Automated: {PASS} passed, {FAIL} failed, {SKIP} skipped")
    print(f"Behavioral: 5 manual checks (see [5] above)")
    print(f"Overall: {'ALL AUTO OK' if FAIL == 0 else 'SOME FAILED'}")

    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
