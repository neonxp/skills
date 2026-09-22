---
title: CreoSkills
markmap:
  colorFreezeLevel: 2
  initialExpandLevel: 3
  maxWidth: 300
---

# CreoSkills — наборы скиллов-инструкций для ИИ-агентов: спеки до кода, DAG-планирование, карта кодовой базы, малые задачи

## Слои и домены

### Корень-агрегатор — сервисный репозиторий CreoSkills

- мета, установщик `install.sh`, документация, ассеты
- наборы `mindmap/`, `sdd/`, `task/` — обычные директории монорепы
- каталога `plan/` в корне нет — модуль живёт внутри потребителей

### Набор mindmap — ментальная карта кодовой базы

#### `mindmap-init` — первичное построение карты проекта

- выборочное обследование: манифесты, точки входа, домены — не весь код
- MINDMAP.md по стайлгайду references/format.md, полоса 20–150 узлов
- опции: MINDMAP.html-просмотрщик, сниппет автозапуска sync в AGENTS.md

#### `mindmap-sync` — актуализация карты после изменений

- хирургическая правка затронутых ветвей либо полная пересборка
- обязателен после крупных фич, мержей, миграций — даже без просьбы

#### `assets/` — автономный офлайн-просмотрщик markmap

- template.html + markmap-lib/view/toolbar + d3.min.js — инлайнится целиком
- icon.png — логотип CreoSkills, встраивается data:URI

### Набор sdd — спека до кода (Spec-Driven Development)

#### Шесть скиллов-этапов цикла

- spec-1-specify — proposal и spec.md, уточняющие вопросы до кода
- spec-2-plan — техплан: решения с альтернативами, затрагиваемый код, риски
- spec-3-tasks — tasks.md: фазы, трассировка [R#], параллельные [P], проверки
- spec-4-implement — исполнение по задачам; режим плана через plan.json
- spec-5-verify — сверка кода со спекой, вердикт «готов к закрытию»
- spec-6-archive — архив в .specs/archive/, дельты требований в .specs/_system

#### Витрина .specs/dashboard.html

- build-dashboard.py — скан активных и архива, вся сборка детерминирована
- dashboard_parts.py — уровни плана (Кан) и SVG-граф зависимостей
- dashboard-template.html — карточки, табы md-документов, граф, живое автообновление вкладки

#### templates/ — каркасы артефактов изменения

- proposal, spec, plan, tasks, research — источник истины формы

### Модуль plan (mod-plan) — DAG-планирование

- не набор, а зависимость потребителей: `plan/` внутри `sdd/` и `task/`
- устанавливается вместе с набором-потребителем, сам по себе не ставится

#### `plan.py` — детерминированная механика графа

- validate (ссылки, циклы с цепочкой), next (готовые шаги в топопорядке)
- groups, status, render (SVG-подобный текст), set, sync чекбоксов tasks.md

#### plan.json — формат плана, schemas/plan.schema.json

- шаги: type task/research/milestone, исчерпывающий prompt, criteria, deps, parent
- статусы pending/active/done/skipped/failed; человекочитаемые slug-id

### Набор task — малые задачи

#### `task-loop` — итеративный цикл без спеки

- формулировка до действия: проблема, простейший подход, критерий готового
- вертикальные срезы с проверкой; пороги входа в sdd и в модуль plan

## Ключевые потоки

### Цикл изменения (sdd)

- spec-1 спека → spec-2 техплан → spec-3 задачи → spec-4 код → spec-5 сверка → spec-6 архив
- каждый этап пересобирает витрину .specs/dashboard.html

### Мост sdd → план

- spec-3 собирает plan.json (≥3 задач или есть [P]) рядом с tasks.md
- spec-4 в режиме плана: next → `set <id> active` → работа → criteria →
  `set` → `sync` → пересборка витрины
- plan.py берётся из потребителя (`sdd/plan/`, `task/plan/`) или из `~/.agents/skills/plan`

### Сборка витрины

- .specs/<изменение>/md-артефакты + .specs/archive/ + plan.json → build-dashboard.py
- выход: self-contained .specs/dashboard.html (offline, табы, граф, архив)

### Жизненный цикл карты

- mindmap-init создаёт MINDMAP.md → mindmap-sync правит после фич
- карта — входной контекст для task-loop, sdd и плана

### Установка наборов

- клон репозитория → `install.sh [набор]` → копия в ~/.agents/skills
- `--agents` — симлинки в директории агентов из таблицы AGENTS.md
- модуль plan ставится вместе с набором-потребителем (sdd или task)

## Кросс-функциональное

### Правила взаимодействия со пользователем

- rules.md в проекте превалирует над любым скиллом, даже противореча ему
- вопросы — только инструментами с вариантами; явные переходы между этапами

### Ограничения артефактов и кода

- скрипты — только Python stdlib; HTML-артефакты — self-contained, без CDN
- тексты скиллов на русском, идентификаторы и слаги — латиницей
- брендинг: icon.png инлайнится в дашборд и mindmap-просмотрщик
- артефакты изменений — в скрытой `.specs/`, не коммитятся (в .gitignore)

## Структура файлов

### Корень — только сервисное

- `README.md` — наборы, установка, правила репозитория
- `AGENTS.md` — правила разработки скиллов и таблица директорий агентов
- `install.sh` — установщик: один набор или все, симлинки по --agents
- `.gitignore` — pycache, производные, `.specs/`
- `assets/icon.png` — логотип CreoSkills

### `spec/`

- `1_overview.md` … `7_using_scripts.md` — справочник формата Agent Skills

### `.specs/` — артефакты изменений sdd (не коммитится)

- `<id>-<slug>/` — каталог изменения: proposal, spec, plan, tasks, research, plan.json
- `_system/` — накопительные спеки доменов; `archive/` — закрытые изменения
- `dashboard.html` — витрина, собирается build-dashboard.py

### `mindmap/` — набор mindmap

- `mindmap-init/` — SKILL.md, references/format.md, assets/ (шаблон карты, просмотрщик)
- `mindmap-sync/` — SKILL.md, тот же набор assets просмотрщика

### `sdd/` — набор sdd

- `spec-1-specify/` — SKILL.md, assets/ (дашборд, marked.min.js, icon), scripts/ (сборка витрины, new-change.sh), templates/
- `spec-2-plan/` … `spec-6-archive/` — SKILL.md (+ templates у spec-2/spec-3)
- `plan/` — план-модуль (SKILL.md, scripts/plan.py, schemas/, templates/)

### `task/` — набор task

- `task-loop/SKILL.md` — единственный скилл набора
- `plan/` — план-модуль
