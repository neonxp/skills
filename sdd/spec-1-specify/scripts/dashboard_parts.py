"""Части витрины для build-dashboard.py: уровни плана и его SVG-граф."""
import xml.sax.saxutils as sx

NODE_W, NODE_H, X_GAP, Y_GAP, PAD = 172, 46, 58, 12, 10
STROKE = {"pending": "var(--muted)", "active": "var(--accent)",
          "done": "var(--ok)", "skipped": "var(--ok)", "failed": "var(--bad)"}


def _esc(text):
    return sx.escape(str(text), {'"': "&quot;"})


def _cut(text, limit):
    return text if len(text) <= limit else text[:limit - 1] + "…"


def plan_levels(steps):
    """Уровни параллельного исполнения (Кан, tie-break — алфавитный id).

    Эффективные зависимости: deps + «родитель ждёт всех своих детей».
    Возвращает (levels, eff) или None при цикле.
    """
    eff = {sid: sorted(set(s.get("deps", []))) for sid, s in steps.items()}
    for sid, s in steps.items():
        parent = s.get("parent")
        if parent and parent in steps:
            eff[parent] = sorted(set(eff[parent]) | {sid})
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
    return levels, eff


def plan_svg(steps):
    """Inline SVG плана: колонки — уровни, стрелки — зависимости."""
    parsed = plan_levels(steps)
    if not parsed:
        return ""
    levels, eff = parsed
    pos = {}
    for col, level in enumerate(levels):
        for row, sid in enumerate(level):
            pos[sid] = (col, row)
    cols, rows = len(levels), max(len(l) for l in levels)
    width = PAD * 2 + cols * NODE_W + (cols - 1) * X_GAP
    height = PAD * 2 + rows * NODE_H + (rows - 1) * Y_GAP

    def top_left(sid):
        col, row = pos[sid]
        return (PAD + col * (NODE_W + X_GAP), PAD + row * (NODE_H + Y_GAP))

    out = [f'<svg viewBox="0 0 {width} {height}" role="img" '
           f'font-family="inherit" fill="var(--fg)">']
    for vid in sorted(steps):
        _, vy = top_left(vid)
        y_mid = vy + NODE_H / 2
        for dep in eff[vid]:
            if dep not in pos:
                continue
            dx, dy = top_left(dep)
            x1, y1 = dx + NODE_W, dy + NODE_H / 2
            x2 = PAD + pos[vid][0] * (NODE_W + X_GAP)
            bend = X_GAP / 2
            out.append(f'<path d="M {x1} {y1} C {x1 + bend} {y1}, '
                       f'{x2 - bend} {y_mid}, {x2} {y_mid}" fill="none" '
                       f'stroke="var(--muted)" stroke-opacity=".55" '
                       f'stroke-width="1.5"/>')
    for sid in sorted(steps):
        s = steps[sid]
        status = s.get("status", "pending")
        x, y = top_left(sid)
        stroke = STROKE.get(status, "var(--line)")
        bold = 2 if status in ("active", "failed") else 1.2
        out.append(f'<rect x="{x}" y="{y}" width="{NODE_W}" height="{NODE_H}" '
                   f'rx="9" fill="var(--card)" stroke="{stroke}" '
                   f'stroke-width="{bold}"/>')
        out.append(f'<text x="{x + 10}" y="{y + 19}" font-size="11.5" '
                   f'font-weight="600">{_esc(_cut(s.get("title") or sid, 26))}'
                   f'</text>')
        sub = f"{_cut(sid, 14)} · {s.get('type', 'task')} · {status}"
        out.append(f'<text x="{x + 10}" y="{y + 35}" font-size="10.5" '
                   f'fill="var(--muted)">{_esc(sub)}</text>')
    out.append("</svg>")
    return "".join(out)
