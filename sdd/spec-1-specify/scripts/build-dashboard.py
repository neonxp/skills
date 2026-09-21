#!/usr/bin/env python3
"""Собирает specs/dashboard.html — витрину активных изменений sdd.

Использование (из корня проекта-потребителя):
    python3 <каталог скилла spec-1-specify>/scripts/build-dashboard.py [КОРЕНЬ]

По умолчанию КОРЕНЬ = текущая директория. Сканирует specs/<изменение>/ (кроме
_system/ и archive/), вычисляет фазу, статусы, открытые уточнения и прогресс,
подставляет данные в assets/dashboard-template.html рядом со скриптом.
Только Python 3 stdlib.
"""
import base64
import json
import pathlib
import re
import sys
from datetime import datetime

PHASE_LABELS = {1: "Спека (черновик)", 2: "План", 3: "Задачи",
                4: "Имплементация", 5: "Готов к закрытию"}


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def meta(text: str, field: str) -> str:
    m = re.search(rf"\*\*{field}\*\*:\s*([^\n]+)", text)
    if not m:
        return ""
    return re.sub(r"<!--.*?-->", "", m.group(1)).strip().strip("`")


def checkboxes(text: str) -> dict:
    done = len(re.findall(r"^\s*- \[[xX]\]", text, re.M))
    total = done + len(re.findall(r"^\s*- \[ \]", text, re.M))
    return {"done": done, "total": total}


def title_of(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return re.sub(r"^#\s*", "", line).replace("Proposal:", "").replace("Спецификация:", "").strip()
    return fallback


def gather(change: pathlib.Path) -> dict:
    proposal = read(change / "proposal.md")
    spec = read(change / "spec.md")
    plan = read(change / "plan.md")
    tasks = read(change / "tasks.md")
    proposal_status = meta(proposal, "Статус").lower()
    if tasks:
        phase = 4 if checkboxes(tasks)["done"] < checkboxes(tasks)["total"] else 5
    elif plan:
        phase = 3
    elif proposal_status and proposal_status != "черновик":
        phase = 2
    else:
        phase = 1
    return {
        "id": change.name,
        "dir": change.name,  # дашборд лежит в specs/ — ссылки относительные от него
        "title": title_of(proposal, change.name),
        "phase": phase,
        "phaseLabel": PHASE_LABELS[phase],
        "proposalStatus": meta(proposal, "Статус") or "—",
        "specStatus": meta(spec, "Статус") or "—",
        "specDomain": meta(spec, "Домен"),
        "openQuestions": re.findall(r"\[УТОЧНИТЬ:\s*([^\]]+)\]", spec),
        "tasks": checkboxes(tasks),
        "acceptance": checkboxes(spec),
        "artifacts": [f for f in ("proposal.md", "spec.md", "plan.md", "tasks.md")
                      if (change / f).exists()],
        "proposalMd": proposal,
        "specMd": spec,
    }


def main() -> None:
    root = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path()
    specs_dir = root / "specs"
    here = pathlib.Path(__file__).resolve().parent.parent  # каталог скилла
    template = read(here / "assets" / "dashboard-template.html")
    marked = read(here / "assets" / "marked.min.js")
    logo = "data:image/png;base64," + base64.b64encode(
        (here / "assets" / "icon.png").read_bytes()).decode()
    assert "</script" not in marked, "marked.min.js содержит </script — небезопасно инлайнить"

    changes = sorted(d for d in specs_dir.glob("*/") if d.name not in ("_system", "archive")) \
        if specs_dir.exists() else []
    data = {
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "specs": [gather(c) for c in changes],
    }
    payload = json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")
    html = (template
            .replace("__SDD_MARKED__", marked)
            .replace("__SDD_LOGO__", logo)
            .replace("__SDD_DASHBOARD_DATA__", payload)
            .replace("__SDD_GENERATED__", data["generated"]))
    out = specs_dir / "dashboard.html"
    out.write_text(html, encoding="utf-8")
    print(f"собрано: {out} ({len(data['specs'])} активн.)")


if __name__ == "__main__":
    main()
