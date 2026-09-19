# Skills — мои скиллы для ИИ-агентов

Коллекция скиллов в открытом формате [Agent Skills](https://agentskills.io):
каталог со `SKILL.md` и вспомогательными файлами. Верхняя директория репозитория —
один устанавливаемый **набор** (может содержать несколько связанных скиллов).

| Набор      | Скиллы                           | Назначение                                                                      |
| ---------- | -------------------------------- | ------------------------------------------------------------------------------- |
| `mindcode` | `mindmap-init`, `mindmap-sync` | ментальная карта кодовой базы: построение `MINDMAP.md` + актуализация после фич |

## Как работает установка

По правилам [AGENTS.md](AGENTS.md):

1. Источник истины — `~/.agents/skills/`: установщик копирует туда каталог каждого скилла.
2. Агенты, которые сами читают `~/.agents/skills/` (Pi, Gemini CLI, Goose, Kimi Code CLI,
   Warp, OpenClaw, Dexto), — больше ничего не требуется.
3. Остальным агентам (Claude Code, Cursor, Codex CLI, …) по умолчанию ничего не ставится;
   симлинк `~/.agents/skills/<скилл>` → `<глобальная директория агента>/<скилл>` создаётся
   только по явному `--agents`.

## Быстро: одна команда

```sh
# все наборы, без симлинков
curl -fsSL https://gitrepo.ru/neonxp/skills/raw/branch/master/install.sh | sh

# только набор mindcode
curl -fsSL https://gitrepo.ru/neonxp/skills/raw/branch/master/install.sh | sh -s -- mindcode

# всё + симлинки выбранным агентам (имена — как в --list, через запятую)
curl -fsSL https://gitrepo.ru/neonxp/skills/raw/branch/master/install.sh | sh -s -- --agents "claude code,codex cli"
```

Требуется только POSIX sh (dash/bash), curl и tar.

## Из клона

```sh
git clone https://gitrepo.ru/neonxp/skills && cd skills
./install.sh                          # все наборы
./install.sh mindcode                 # один набор
./install.sh --list                   # какие наборы и агенты есть
./install.sh --agents all             # + симлинки всем агентам-«симлинкам»
./install.sh --remove mindcode        # снять набор (копии и симлинки)
./install.sh --remove --agents all    # снять всё, что ставили
```

Обновление = повторный запуск: копии в `~/.agents/skills/` перезаписываются,
симлинки продолжают указывать на те же пути.

## Силами ИИ-агента (без терминала)

Скопируйте своему агенту:

> Склонируй https://gitrepo.ru/neonxp/skills во временную директорию и установи мне
> набор mindcode, следуя README.md этого репозитория: `./install.sh mindcode`, а если
> моему агенту нужен симлинк (список — `./install.sh --list`) — добавь `--agents "Имя"`.
> В конце отчитайся: что и куда установлено.
