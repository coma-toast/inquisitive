#!/usr/bin/env python3
"""inquisitive-sqlite — init | insert <json> | query <sql>"""
import sqlite3, json, sys, os
D = os.path.join(os.path.dirname(__file__),"..","data","memory","inquisitive.db")
def cn():
    c = sqlite3.connect(D)
    c.row_factory = sqlite3.Row
    return c
def i():
    os.makedirs(os.path.dirname(D), exist_ok=True)
    with cn() as c:
        c.executescript("CREATE TABLE IF NOT EXISTS entries(id TEXT PRIMARY KEY,timestamp TEXT,project TEXT,file_changed TEXT,original_suggestion TEXT,user_choice TEXT,primary_category TEXT,secondary_category TEXT,criticality INT,was_planned INT,side_effects TEXT,skill_refinement_signal INT,raw_answer TEXT);CREATE TABLE IF NOT EXISTS summaries(category TEXT PRIMARY KEY,summary TEXT,last_refined TEXT)")
def n(d):
    with cn() as c:
        c.execute("INSERT OR REPLACE INTO entries VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",[d.get(k) for k in["id","timestamp","project","file_changed","original_suggestion","user_choice","primary_category","secondary_category","criticality","was_planned","side_effects","skill_refinement_signal","raw_answer"]])
def q(s):
    with cn() as c: print(json.dumps([dict(r) for r in c.execute(s).fetchall()]))
if __name__=="__main__":
    {"init":i,"insert":lambda:n(json.loads(sys.argv[2])),"query":lambda:q(sys.argv[2])}.get(sys.argv[1],lambda:print("init | insert <json> | query <sql>"))()
