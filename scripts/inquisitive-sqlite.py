#!/usr/bin/env python3
"""inquisitive-sqlite — init | insert <json> | query <sql>

Default DB path: .inquisitive/inquisitive.db (relative to CWD, i.e. the repo being worked in).
Override with INQUISITIVE_DB env var or --db flag.
"""
import sqlite3, json, sys, os

def get_db_path():
    if "--db" in sys.argv:
        idx = sys.argv.index("--db")
        return sys.argv[idx + 1]
    if os.environ.get("INQUISITIVE_DB"):
        return os.environ["INQUISITIVE_DB"]
    return os.path.join(os.getcwd(), ".inquisitive", "inquisitive.db")

D = get_db_path()

def cn():
    c = sqlite3.connect(D)
    c.row_factory = sqlite3.Row
    return c

def i():
    os.makedirs(os.path.dirname(D), exist_ok=True)
    with cn() as c:
        c.executescript("""
CREATE TABLE IF NOT EXISTS entries (
  id TEXT PRIMARY KEY,
  timestamp TEXT,
  scope TEXT DEFAULT 'repo',
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
        """)
    print(f"OK init: {D}")

def insert(d):
    with cn() as c:
        c.execute(
            "INSERT OR REPLACE INTO entries VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            [d.get(k) for k in [
                "id","timestamp","scope","org_slug","repo","file_changed",
                "original_suggestion","user_choice","primary_category",
                "secondary_category","criticality","was_planned",
                "side_effects","skill_refinement_signal","raw_answer","personality"
            ]]
        )

def query(s):
    with cn() as c:
        print(json.dumps([dict(r) for r in c.execute(s).fetchall()], indent=2))

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "init":
        i()
    elif cmd == "insert":
        insert(json.loads(sys.argv[2]))
    elif cmd == "query":
        query(sys.argv[2])
    else:
        print("Usage: inquisitive-sqlite.py [--db PATH] init | insert <json> | query <sql>")
        print("  Default DB: .inquisitive/inquisitive.db (relative to CWD)")
        print("  Override:   --db /path/to/inquisitive.db  or  INQUISITIVE_DB env var")
