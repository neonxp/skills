# Skills

Репозиторий скиллов в формате [Agent Skills](https://agentskills.io); спецификация
формата — в директории `spec/`. Каждый каталог верхнего уровня — устанавливаемый набор.

## Кому что читать

- **Устанавливаешь скиллы пользователю?** Тебе нужен только раздел «Установка» ниже —
  на практике проще всего `./install.sh` (см. [README.md](README.md)). Раздел
  «Разработка скиллов» к установке не относится и выполняться не должен.
- **Разрабатываешь или обновляешь скиллы в этом репозитории?** Тебе адресован раздел
  «Разработка скиллов».

## Установка скиллов

Так ставится любой набор; из клона это автоматизирует `./install.sh [НАБОР] [--agents …]`:

1. Источник истины — `~/.agents/skills/`: каталог скилла целиком копируется туда.
2. Агенты, которые сами читают `~/.agents/skills/` (Универсальный стандарт, Pi, Gemini CLI,
   Goose, Kimi Code CLI, Warp, OpenClaw, Dexto) — больше ничего не требуется; копия
   в их собственную глобальную директорию создаёт дубли-конфликты.
3. Агенты, которые НЕ читают `~/.agents/skills/`, — в их глобальную директорию из таблицы
   кладётся симлинк на каталог скилла (не копия!), обновления источника подхватываются
   автоматически:

   ```bash
   ln -s ~/.agents/skills/<skill> <глобальная директория агента>/<skill>
   ```

   Пример: `ln -s ~/.agents/skills/mindcode ~/.claude/skills/mindcode`

Проектные директории из таблицы — для установки скилла внутрь конкретного проекта
(в т.ч. проектная `.agents/skills/`, которую читают Cursor, Copilot, Codex CLI, OpenCode),
к системной установке отношения не имеют:

| Агент                               | Глобальная директория                                                        | Установка | Проектная директория                                                   | Примечание                                                                             |
| ----------------------------------- | ---------------------------------------------------------------------------- | --------------------------- | ---------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **Универсальный стандарт (Agents)** | `~/.agents/skills/` | только `~/.agents/skills/` | `.agents/skills/` | Де-факто кросс-агентный стандарт, поддерживается большинством современных инструментов |
| **Claude Code** | `~/.claude/skills/` | симлинк | `.claude/skills/` | Также поднимается вверх по дереву каталогов до корня репозитория |
| **Cursor** | `~/.cursor/skills/` | симлинк | `.cursor/skills/` | Дополнительно читает `.agents/skills`, `.claude/skills`, `.codex/skills` |
| **GitHub Copilot** | `~/.copilot/skills/` | симлинк | `.github/skills/` | Также читает из `.claude/skills` и `.agents/skills` |
| **Cline** | `~/.cline/skills/` | симлинк | `.cline/skills/` | В некоторых источниках также `.clinerules/skills/` |
| **Roo Code** | `~/.roo/skills/` | симлинк | `.roo/skills/` | Скиллы регистрируются как кастомные режимы в `.roomodes` |
| **Continue** | `~/.continue/rules/` (и `~/.continue/skills/`) | симлинк | `.continue/rules/` | Основной путь — `rules/`, но есть и поддержка `skills/` |
| **Windsurf** | `~/.codeium/windsurf/skills/` (или `~/.windsurf/rules/`) | симлинк | `.windsurf/skills/` | Для скиллов используется поддиректория с `.md` файлом |
| **Codex CLI** | `~/.codex/skills/` | симлинк | `.codex/skills/` | Также читает `.agents/skills/` |
| **Aider** | `~/.aider/skills/` | симлинк | — | Нативной поддержки проектных скиллов нет, загружаются вручную |
| **Augment** | `~/.augment/skills/` | симлинк | `.augment/skills/` | Ранее использовал один файл `augment-guidelines.md` |
| **Gemini CLI** | `~/.gemini/skills/` | только `~/.agents/skills/` | `.gemini/skills/` | Также читает из `~/.agents/skills/` |
| **Pi** | `~/.pi/agent/skills/` (и `~/.agents/skills/`) | только `~/.agents/skills/` | `.pi/skills/` (и `.agents/skills/`) | Загружает также из пакетов |
| **Kilo (Kilo Code)** | `~/.kilocode/skills/` (или `~/.kilo/skills/`) | симлинк | `.kilocode/skills/` (или `.kilo/skills/`) | Поддерживает режим-специфичные скиллы |
| **OpenCode** | `~/.config/opencode/skills/` (и `.claude/skills/`, `.agents/skills/`) | симлинк | `.opencode/skills/` (и `.claude/skills/`, `.agents/skills/`) | При поиске поднимается вверх до корня git-репозитория |
| **ZCode** | `~/.zcode/skills/` | симлинк | `.zcode/skills/` | Читает также из `.agents/skills/` |
| **Devin** | `~/.config/devin/skills/` (Linux/macOS); `%APPDATA%\devin\skills\` (Windows) | симлинк | `.devin/skills/` | Рекомендуется `.agents/skills/<skill>/SKILL.md` |
| **Replit** | — | — | `.agents/skills/` | Единственная задокументированная директория — проектная |
| **Amp (Sourcegraph Cody)** | `~/.config/agents/skills/` (и `~/.amp/skills/`) | симлинк | `.agents/skills/` (и `.amp/skills/`) | Cody переименован в Amp в 2026 |
| **Tabnine** | `~/.tabnine/agent/skills/` | симлинк | — | Управление через `tabnine skills` |
| **Amazon Q Developer** | `~/.aws/amazonq/agents/` (конфигурация агентов) | вручную | — | Скиллы маппятся в конфигурацию агента |
| **JetBrains AI Assistant** | `~/.config/JetBrains/skills/` | симлинк | Добавляется через настройки (Settings → Tools → AI Assistant → Skills) | Управление директориями вручную |
| **OpenClaw** | `~/.openclaw/skills/` (и `~/.agents/skills/`) | только `~/.agents/skills/` | `<workspace>/skills/` | Иерархия: workspace → managed → bundled |
| **Trae** | `~/.trae/skills/` (macOS/Linux); `%userprofile%/.trae/skills` (Windows) | симлинк | `.trae/skills/` | Также читает `.agents/skills/` |
| **Kiro CLI** | `~/.kiro/skills/` | симлинк | `.kiro/skills/` | Автоматически загружается из обеих директорий |
| **Goose** | `~/.agents/skills/` (и `~/.config/goose/skills/`) | только `~/.agents/skills/` | `.agents/skills/` (и `.goose/skills/`) | Загружает из `.agents/skills/` и `~/.config/agents/skills/` |
| **Kimi Code CLI** | `~/.agents/skills/` (и `~/.config/agents/skills/`) | только `~/.agents/skills/` | — | Kimi-специфичные скиллы могут лежать в `$KIMI_CODE_HOME/skills/` |
| **Antigravity** | `~/.gemini/antigravity/skills/` (или `~/.gemini/config/skills/`) | симлинк | `.agents/skills/` (или `.agent/skills/`) | По умолчанию используется `.agents/skills` |
| **Dexto** | `~/.agents/skills/` | только `~/.agents/skills/` | `.agents/skills/` | Использует универсальную директорию |
| **Warp** | `~/.agents/skills/` (или `~/.warp/skills/`) | только `~/.agents/skills/` | `.agents/skills/` (или `.warp/skills/`) | Сканирует как универсальные, так и собственные директории |
| **Firebender** | `~/.firebender/skills/` | симлинк | — | Также читает `~/.goose/skills/` и `~/.claude/skills/` |
| **Deep Agents** | `~/.deepagents/<agent>/skills/` (и `~/.agents/skills/`) | только `~/.agents/skills/` | `.deepagents/skills/` (и `.agents/skills/`) | Путь зависит от имени агента |
| **Mistral Vibe** | `~/.vibe/skills/` | симлинк | `.vibe/skills/` (и `.agents/skills/`) | Также поддерживает кастомные пути через `skill_paths` |
| **OpenHands** | `~/.agents/skills/` (и `~/.openhands/skills/`) | только `~/.agents/skills/` | `.agents/skills/` (и `.openhands/skills/`) | Рекомендуется `.agents/skills/` для новых скиллов |
| **Factory Droid** | `~/.factory/skills/` | симлинк | `.factory/skills/` | Скиллы также могут лежать в `skills/` внутри плагинов |
| **ClawdBot** | `~/.clawdbot/skills/` | симлинк | `<workspace>/skills/` | Три уровня: bundled → managed → workspace |
| **Zed** | `~/.agents/skills/` | только `~/.agents/skills/` | `.agents/skills/` | Устанавливаются вручную копированием папки |
| **CodeBuddy** | `~/.codebuddy/skills/` | симлинк | `.codebuddy/skills/` | Каждый скилл — отдельная папка с `SKILL.md` |
| **Command Code** | `~/.commandcode/skills/` | симлинк | `.commandcode/skills/` | Указан в списке поддерживаемых агентов |
| **Bolt** | — | — | `.bolt/skills/` | Проектная директория |
| **PureCode** | — | — | `.agents/skills/` | Предположительно использует универсальный стандарт |
| **Witsy** | — | — | — | Путь задаётся вручную через `skills.paths` |
| **OpenClaw (Claw)** | `~/.openclaw/skills/` | симлинк | `<workspace>/skills/` | См. также ClawdBot |
| **Goose (альт.)** | `~/.config/agents/skills/` | симлинк | `.agents/skills/` | Дублирует универсальную директорию |

## Разработка скиллов

Эти правила адресованы агенту, разрабатывающему скиллы в этом репозитории
(добавление нового набора, изменение существующего) по поручению владельца:

- Структура: один набор = каталог верхнего уровня; скилл = вложенный каталог со `SKILL.md`,
  имя каталога = `name` во frontmatter (требование спецификации в `spec/2_specification.md`).
- После каждого изменения скилла переустанови затронутый набор для владельца:
  `./install.sh <НАБОР>`. Симлинки в директориях агентов пользователя создавай или
  удаляй только по явной просьбе владельца.
- Таблица агентов выше — единственный источник для `install.sh --agents`: правишь здесь —
  установщик подхватывает автоматически.
- Содержание SKILL.md — по `spec/`: описание ≤1024 символов, тело ≤500 строк, детализация
  через `references/`, скрипты в `scripts/`.
- Новый набор добавь в таблицу README.md (набор, скиллы, назначение).

## Ментальная карта кода (mindcode)

В корне репозитория лежат `MINDMAP.md` — карта архитектуры и знаний о проекте
(формат markmap: домены, модули, модели данных с полями, ключевые потоки,
назначение файлов) и `MINDMAP.html` — офлайн-просмотр карты в браузере.

- После завершения крупной фичи, рефакторинга или миграции запускай скилл
  `mindmap-sync` для актуализации карты — даже если про карту никто не просил.
  Крупная = мерж, завершённая задача, дифф примерно от 10 файлов или
  появление/исчезновение модуля; правки комментариев и форматирования — нет.
- Карта — источник знаний о проекте: перед задачей загляни в неё — модели данных
  с полями, назначение файлов и потоки сэкономят чтение кода.
- Планируя изменения, сверяйся с картой: она показывает, где какая ответственность живёт.
- Не правь `MINDMAP.md` в обход `mindmap-sync`, чтобы карта не разошлась с кодом.
