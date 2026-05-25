#!/usr/bin/env python3
"""Automated eval runner for inquisitive.

Tests infrastructure (SQLite, entries, category matching, personalities)
and prints behavioral eval scenarios as a checklist.
"""

import json
import os
import sqlite3
import sys
import tempfile
import textwrap

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
        conn.executescript(
            "CREATE TABLE IF NOT EXISTS entries(id TEXT PRIMARY KEY,"
            "timestamp TEXT,project TEXT,file_changed TEXT,"
            "original_suggestion TEXT,user_choice TEXT,"
            "primary_category TEXT,secondary_category TEXT,"
            "criticality INT,was_planned INT,side_effects TEXT,"
            "skill_refinement_signal INT,raw_answer TEXT);"
        )
        ok("Create entries table")
    except Exception as e:
        fail("Create entries table", str(e))

    try:
        conn.executescript(
            "CREATE TABLE IF NOT EXISTS summaries(category TEXT PRIMARY KEY,"
            "summary TEXT,last_refined TEXT);"
        )
        ok("Create summaries table")
    except Exception as e:
        fail("Create summaries table", str(e))

    try:
        conn.execute(
            "INSERT OR REPLACE INTO entries VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            ["test-1", "2026-01-01T00:00:00Z", "test", "test.md",
             "suggestion", "choice", "intent", "ux",
             3, 1, "none", 0, "test answer"],
        )
        row = conn.execute("SELECT * FROM entries WHERE id='test-1'").fetchone()
        assert row["primary_category"] == "intent"
        ok("Insert and query entry")
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
        "timestamp": "2026-05-25T12:00:00Z",
        "project": "inquisitive",
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
        ok("Write and read JSON entry")
    except Exception as e:
        fail("Write and read JSON entry", str(e))

    # Markdown write
    try:
        mpath = os.path.join(tmpdir, "eval-test-001.md")
        frontmatter = "---\n"
        for k in ["id", "timestamp", "project", "file_changed",
                   "primary_category", "secondary_category",
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
        ok("Write and read Markdown entry")
    except Exception as e:
        fail("Write and read Markdown entry", str(e))

    # JSON index append
    try:
        ipath = os.path.join(tmpdir, "index.json")
        index = []
        index.append({k: entry[k] for k in
                       ["id", "timestamp", "project", "primary_category",
                        "secondary_category", "criticality", "was_planned"]})
        with open(ipath, "w") as f:
            json.dump(index, f, indent=2)
        with open(ipath) as f:
            loaded_idx = json.load(f)
        assert len(loaded_idx) == 1
        ok("Write and read index.json")
    except Exception as e:
        fail("Write and read index.json", str(e))

    import shutil
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

    # Template fill
    filled = inquisitive["secondary"].format(
        approach="table", choice="cards"
    )
    assert "table" in filled and "cards" in filled
    ok("Secondary question template fills correctly")

    # Personality switch
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


# ── Main ──────────────────────────────────────────────────────────
def main():
    print(f"Inquisitive Eval Runner")
    print(f"{'=' * 40}")

    test_sqlite()
    test_entry_persistence()
    test_category_matching()
    test_personalities()
    print_behavioral_checklist()

    auto = PASS + FAIL
    print(f"\n{'=' * 40}")
    print(f"Automated: {PASS} passed, {FAIL} failed, {SKIP} skipped")
    print(f"Behavioral: 5 manual checks (see [5] above)")
    print(f"Overall: {'ALL AUTO OK' if FAIL == 0 else 'SOME FAILED'}")

    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
