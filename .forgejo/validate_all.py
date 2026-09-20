#!/usr/bin/env python3
"""CI-валидация всех скиллов репозитория через skills-ref (Python API)."""
import sys
from pathlib import Path
from skills_ref import validate

failed = False
skill_dirs = sorted({p.parent for p in Path(".").rglob("SKILL.md") if ".git" not in p.parts})
if not skill_dirs:
    print("Скиллы не найдены — некорректный layout репозитория")
    sys.exit(1)

for d in skill_dirs:
    print("===", d)
    problems = validate(d)
    if problems:
        failed = True
        for problem in problems:
            print("  ПРОБЛЕМА:", problem)
    else:
        print("  OK")

sys.exit(1 if failed else 0)
