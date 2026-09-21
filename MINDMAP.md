---
title: CreoSkills
markmap:
  colorFreezeLevel: 2
  initialExpandLevel: 3
  maxWidth: 300
---

# CreoSkills — наборы скиллов-инструкций для ИИ-агентов: спеки до кода, DAG-планирование, карта кодовой базы, малые задачи

## Слои и домены

### Набор mindcode — ментальная карта кодовой базы

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
- spec-6-archive — архив в specs/archive/, дельты требований в specs/_system

#### Витрина specs/dashboard.html

- build-dashboard.py — скан активных и архива, вся сборка детерминирована
- dashboard_parts.py — уровни плана (Кан) и SVG-граф зависимостей
- dashboard-template.html — карточки, табы md-документов, граф, MINDMAP-ссылка

#### templates/ — каркасы артефактов изменения

- proposal, spec, plan, tasks, research — источник истины формы

### Набор plan — модуль DAG-планирования

#### `plan.py` — детерминированная механика графа

- validate (ссылки, циклы с цепочкой), next (готовые шаги в топопорядке)
- groups, status, render (SVG-подобный текст), set, sync чекбоксов tasks.md

#### plan.json — формат плана, schemas/plan.schema.json

- шаги: type task/research/milestone, исчерпывающий prompt, criteria, deps, parent
- статусы pending/active/done/skipped/failed; человекочитаемые slug-id

### Набор task — малые задачи

#### `task-loop` — итеративный цикл без спеки

- формулировка до действия: проблема, простейший подход, критерий готового
- вертикальные срезы с проверкой; пороги входа в sdd и в план-модуль

## Ключевые потоки

### Цикл изменения (sdd)

- spec-1 спека → spec-2 техплан → spec-3 задачи → spec-4 код → spec-5 сверка → spec-6 архив
- каждый этап пересобирает витрину dashboard.html

### Мост sdd → план

- spec-3 собирает plan.json (≥3 задач или есть [P]) рядом с tasks.md
- spec-4 в режиме плана: plan.py next → работа → criteria → set → sync

### Сборка витрины

- specs/*/md-артефакты + specs/archive/ + plan.json → build-dashboard.py
- выход: self-contained specs/dashboard.html (offline, табы, граф, архив)

### Жизненный цикл карты

- mindmap-init создаёт MINDMAP.md → mindmap-sync правит после фич
- карта — входной контекст для task-loop, sdd и плана

### Установка наборов

- install.sh [набор] → копия в ~/.agents/skills (источник истины)
- --agents — симлинки в директории агентов из таблицы AGENTS.md

## Кросс-функциональное

### Правила взаимодействия со пользователем

- rules.md в проекте превалирует над любым скиллом, даже противореча ему
- вопросы — только инструментами с вариантами; явные переходы между этапами

### Ограничения артефактов и кода

- скрипты — только Python stdlib; HTML-артефакты — self-contained, без CDN
- тексты скиллов на русском, идентификаторы и слаги — латиницей
- брендинг: icon.png инлайнится в дашборд и mindmap-просмотрщик

## Структура файлов

### Корень

- `README.md` — наборы, установка, правила репозитория
- `AGENTS.md` — правила разработки скиллов и таблица директорий агентов
- `install.sh` — установщик: один набор или все, симлинки по --agents
- `.gitignore` — pycache и производные
- `assets/icon.png` — логотип CreoSkills

### `spec/`

- `1_overview.md` … `7_using_scripts.md` — справочник формата Agent Skills

### `mindcode/`

- `mindmap-init/` — SKILL.md, references/format.md, assets/ (шаблон карты, просмотрщик)
- `mindmap-sync/` — SKILL.md, тот же набор assets просмотрщика

### `sdd/`

- `spec-1-specify/` — SKILL.md, assets/ (дашборд, marked.min.js, icon), scripts/ (сборка витрины), templates/
- `spec-2-plan/` — SKILL.md, templates/plan.md
- `spec-3-tasks/` — SKILL.md, templates/tasks.md
- `spec-4-implement/`, `spec-5-verify/`, `spec-6-archive/` — SKILL.md

### `task/`

- `task-loop/SKILL.md` — единственный скилл набора

### `plan/`

- `plan/SKILL.md` — справочник модуля для потребителей
- `plan/scripts/plan.py` — CLI механики DAG
- `plan/schemas/plan.schema.json` — строгая JSON Schema плана
- `plan/templates/plan.json` — каркас плана
