#!/usr/bin/env python3
"""Sync root SKILL.md → skills/inquisitive/SKILL.md, adding YAML frontmatter."""

import os

BASE = os.path.join(os.path.dirname(__file__), "..")
ROOT = os.path.join(BASE, "SKILL.md")
INSTALLED = os.path.join(BASE, "skills", "inquisitive", "SKILL.md")

FRONTMATTER = """\
---
name: inquisitive
description: >-
  A meta-learning skill that improves the agent's first-try accuracy by analyzing
  every user-initiated file change and plan modification. When the user adjusts the
  agent's work, it asks targeted "why" questions to understand what the original
  suggestion got wrong. Answers are categorized into 12 categories (Intent, UX,
  Styling, Security, Business Logic, Efficiency, Maintainability, Reliability,
  Compatibility, Developer Experience, Data Integrity, Compliance), stored across
  multiple backends, and continuously refined into evolving summaries via auto-refinement.
  When strong patterns emerge, the skill proposes or auto-creates sub-skills that
  encode those preferences — making the agent smarter on every subsequent try.
  If you detect the user likes something, get it wrong, changes something, or provides
  feedback — or when the user says "change this," "actually do it differently,"
  "refine," "revise" — activate this skill to ask why. When a plan annotation has
  follow-up instructions or changes, activate this skill to ask about the plan change.
  Do NOT activate for typos, formatting-only changes, or rename-only refactors.
license: MIT
compatibility: opencode
metadata:
  audience: agents
  workflow: meta-learning
---"""


def main():
    if os.path.realpath(ROOT) == os.path.realpath(INSTALLED):
        print("SKILL.md is a symlink to skills/inquisitive/SKILL.md — "
              "break the symlink first (rm SKILL.md && cp ...)")
        return 1

    with open(ROOT) as f:
        body = f.read().strip()

    with open(INSTALLED, "w") as f:
        f.write(FRONTMATTER + "\n\n" + body + "\n")

    print("OK synced")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
