#!/usr/bin/env python3
"""plan.py — детерминированная механика DAG-плана модуля plan.

Команды: validate, next, groups, status, set, render, sync.
План — JSON-файл (формат: schemas/plan.schema.json). Только stdlib.
"""
import argparse
import json
import pathlib
import re
import sys

STATUSES = ("pending", "active", "done", "skipped", "failed")
TERMINAL = ("done", "skipped")
TYPES = ("task", "research", "milestone")


def die(msg):
    print(f"ОШИБКА: {msg}", file=sys.stderr)
    sys.exit(1)


def load(path):
    p = pathlib.Path(path)
    if not p.is_file():
        die(f"файл не найден: {p}")
    try:
        plan = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"невалидный JSON: {e}")
    return plan, p


def save(plan, path):
    pathlib.Path(path).write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate(plan):
    if plan.get("version") != 1:
        die("version должен быть 1")
    if not isinstance(plan.get("title"), str) or not plan["title"]:
        die("нет непустого title")
    steps = plan.get("steps")
    if not isinstance(steps, dict) or not steps:
        die("steps должен быть непустым объектом {id: шаг}")
    for sid, s in steps.items():
        if s.get("type") not in TYPES:
            die(f"{sid}: type должен быть одним из {TYPES}")
        if s.get("status", "pending") not in STATUSES:
            die(f"{sid}: status должен быть одним из {STATUSES}")
        if not isinstance(s.get("prompt", ""), str):
            die(f"{sid}: prompt должен быть строкой")
        for ref in ([s["parent"]] if s.get("parent") else []) + s.get("deps", []):
            if ref not in steps:
                die(f"{sid}: ссылка на несуществующий шаг {ref!r}")


def effective_deps(steps):
    """Явные deps + неявное «родитель ждёт всех своих детей»."""
    eff = {sid: sorted(set(s.get("deps", []))) for sid, s in steps.items()}
    for sid, s in steps.items():
        parent = s.get("parent")
        if parent:
            eff[parent] = sorted(set(eff[parent]) | {sid})
    return eff


def parallel_groups(steps, eff):
    """Уровни параллельного исполнения (Кан, tie-break — алфавитный id)."""
    indeg = {v: len([d for d in eff[v] if d in steps]) for v in steps}
    done, levels = set(), []
    while len(done) < len(steps):
        level = sorted(v for v in steps if v not in done and indeg[v] == 0)
        if not level:
            return None
        levels.append(level)
        done |= set(level)
        for v in level:
            for w in steps:
                if w not in done and v in eff[w]:
                    indeg[w] -= 1
    return levels


def order_map(steps, eff):
    levels = parallel_groups(steps, eff)
    if levels is None:
        cycle = find_cycle(steps, eff)
        die("обнаружен цикл: " + " -> ".join(cycle))
    return {sid: i for i, sid in enumerate(sum(levels, []))}


def find_cycle(steps, eff):
    color = dict.fromkeys(steps, 0)  # 0 white, 1 gray, 2 black

    def visit(v, stack):
        color[v] = 1
        for d in eff[v]:
            if color.get(d, 2) == 1:
                return stack[stack.index(d):] + [d]
            if color.get(d, 2) == 0:
                r = visit(d, stack + [d])
                if r:
                    return r
        color[v] = 2
        return None

    for v in steps:
        if color[v] == 0:
            r = visit(v, [v])
            if r:
                return r
    return None


def cmd_validate(args):
    plan, _ = load(args.plan)
    validate(plan)
    eff = effective_deps(plan["steps"])
    if parallel_groups(plan["steps"], eff) is None:
        die("обнаружен цикл: " + " -> ".join(find_cycle(plan["steps"], eff)))
    print(f"OK: {plan['title']} — {len(plan['steps'])} шагов, циклов нет")


def cmd_next(args):
    plan, _ = load(args.plan)
    validate(plan)
    steps = plan["steps"]
    eff = effective_deps(steps)
    order = order_map(steps, eff)
    ready = [
        sid for sid, s in steps.items()
        if s.get("status", "pending") == "pending"
        and all(steps[d].get("status", "pending") in TERMINAL
                for d in eff[sid] if d in steps)
    ]
    ready.sort(key=lambda sid: order[sid])
    remaining = sum(1 for s in steps.values()
                    if s.get("status", "pending") not in TERMINAL)
    state = "done" if remaining == 0 else ("running" if ready else "wait")
    print(json.dumps({
        "state": state,
        "remaining": remaining,
        "steps": [{
            "id": sid,
            "task": s.get("task", sid),
            "title": s["title"],
            "type": s["type"],
            "prompt": s.get("prompt", ""),
            "criteria": s.get("criteria", []),
        } for sid, s in steps.items() if sid in ready],
    }, ensure_ascii=False, indent=2))


def cmd_groups(args):
    plan, _ = load(args.plan)
    validate(plan)
    eff = effective_deps(plan["steps"])
    levels = parallel_groups(plan["steps"], eff)
    if levels is None:
        die("обнаружен цикл: " + " -> ".join(find_cycle(plan["steps"], eff)))
    print(json.dumps(levels, ensure_ascii=False))


def cmd_status(args):
    plan, _ = load(args.plan)
    validate(plan)
    steps = plan["steps"]
    counts = {st: 0 for st in STATUSES}
    for s in steps.values():
        counts[s.get("status", "pending")] += 1
    total = len(steps)
    closed = counts["done"] + counts["skipped"]
    print(f"{plan['title']}: {closed}/{total} закрыто "
          f"({100 * closed // total if total else 100}%)")
    for st in STATUSES:
        ids = sorted(s for s, v in steps.items()
                     if v.get("status", "pending") == st)
        if ids:
            print(f"  {st}: {', '.join(ids)}")


def cmd_set(args):
    plan, p = load(args.plan)
    validate(plan)
    if args.step not in plan["steps"]:
        die(f"шаг {args.step!r} не найден")
    if args.status not in STATUSES:
        die(f"status должен быть одним из {STATUSES}")
    plan["steps"][args.step]["status"] = args.status
    if args.result is not None:
        plan["steps"][args.step]["result"] = args.result
    save(plan, p)
    print(f"{args.step}: {args.status}")


def cmd_render(args):
    plan, _ = load(args.plan)
    validate(plan)
    steps = plan["steps"]
    mark = {"pending": " ", "active": "→", "done": "x", "skipped": "x",
            "failed": "!"}
    print("```mermaid")
    print("graph TD")
    for sid, s in sorted(steps.items()):
        label = f"{sid} · {s['type']} · {s.get('status', 'pending')}"
        print(f'    {sid}["{label}"]')
    for sid, s in sorted(steps.items()):
        for d in s.get("deps", []):
            print(f"    {d} --> {sid}")
        if s.get("parent"):
            print(f"    {s['parent']} -.-> {sid}")
    print("```")
    print()
    for sid, s in sorted(steps.items(), key=lambda kv: kv[1].get("task", kv[0])):
        print(f"- [{mark[s.get('status', 'pending')]}] "
              f"{s.get('task', sid)}. {s['title']} ({s['type']})")


def cmd_sync(args):
    plan, _ = load(args.plan)
    validate(plan)
    tasks = pathlib.Path(args.tasks)
    if not tasks.is_file():
        die(f"файл не найден: {tasks}")
    marks = {s["task"]: s.get("status", "pending")
             for s in plan["steps"].values() if s.get("task")}
    lines = tasks.read_text(encoding="utf-8").splitlines()
    changed, seen = 0, set()
    for i, line in enumerate(lines):
        m = re.match(r"^(\s*)- \[([ x])\] (\S+)[.::]", line)
        if not m or m.group(3) not in marks:
            continue
        mark = marks[m.group(3)]
        want = "x" if mark in TERMINAL else " "
        if m.group(2) != want:
            lines[i] = line[:m.start(2)] + want + line[m.end(2):]
            changed += 1
        seen.add(m.group(3))
    missing = sorted(set(marks) - seen)
    tasks.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"sync: обновлено чекбоксов — {changed}")
    if missing:
        print("не найдены в tasks.md: " + ", ".join(missing), file=sys.stderr)
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, help_ in [("validate", "проверить структуру, ссылки и циклы"),
                        ("next", "готовые шаги в топологическом порядке"),
                        ("groups", "уровни параллельного исполнения"),
                        ("status", "сводка и прогресс"),
                        ("set", "обновить статус шага"),
                        ("render", "mermaid-граф и чеклист"),
                        ("sync", "синхронизировать чекбоксы tasks.md")]:
        p = sub.add_parser(name, help=help_)
        p.add_argument("plan", help="путь к plan.json")
        if name == "set":
            p.add_argument("step", help="id шага")
            p.add_argument("status", help=f"новый статус {STATUSES}")
            p.add_argument("--result", help="итог выполнения")
        if name == "sync":
            p.add_argument("--tasks", required=True, help="путь к tasks.md")
        p.set_defaults(func=globals()[f"cmd_{name}"])
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
