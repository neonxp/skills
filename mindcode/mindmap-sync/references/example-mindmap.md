# OrderHub — маркетплейс услуг: заказчики находят исполнителей, платформа держит комиссию

## Слои и домены

### Backend — Go-монолит

#### `cmd/server` — точка входа: конфиг, graceful shutdown

#### `internal/api` — HTTP-роутинг, middleware, OpenAPI-спека

#### `internal/orders` — жизненный цикл заказа, saga выплат

##### Order (БД: таблица orders)

- id (string, UUID) — идентификатор заказа
- buyer_id (string) — заказчик
- executor_id (string, nullable) — назначенный исполнитель
- status (enum: new/paid/in_work/done/cancelled) — состояние
- total (int, копейки) — сумма к оплате
- created_at, updated_at (timestamp) — служебные метки

##### CreateOrderRequest (DTO API)

- service_id (string) — услуга из каталога
- comment (string) — пожелания заказчика

#### `internal/billing` — счета, тарифы, эквайринг ЮKassa

##### Invoice (БД: таблица invoices)

- id (string, UUID) — идентификатор счёта
- order_id (string) — заказ-основание
- amount (int, копейки) — сумма
- state (enum: held/captured/refunded) — состояние холда

##### OrderCreated (событие Kafka: топик `orders.events`)

- order_id (string) — заказ
- amount (int, копейки) — сумма
- occurred_at (timestamp) — момент события

#### `internal/users` — регистрация, сессии, роли

#### `internal/catalog` — услуги, категории, поиск

#### `internal/reviews` — оценки и отзывы после заказа

#### `internal/moderation` — премодерация услуг и жалоб

#### `internal/notify` — email/push-рассылка, шаблоны

#### `internal/chat` — чаты покупатель↔исполнитель

#### `internal/files` — загрузка фото и документов в S3

#### `internal/webhooks` — приём событий PSP и внешних интеграций

### Frontend — React SPA

#### Витрина — каталог, поиск, корзина

#### Личный кабинет — заказы, документы, выплаты

#### Админка — модерация, тарифы, отчёты

#### `api-client` — генерируется из OpenAPI-спеки

#### Общее — дизайн-система, i18n, роутинг

### Мобильное приложение — Flutter

#### Покупатель — заказы, чаты, оплата

#### Исполнитель — наряды, статусы, выплаты

### Инфраструктура

#### PostgreSQL — основное хранилище, миграции goose

- схемы: `orders`, `billing`, `users`, `catalog`

#### Kafka — событийная шина

- топики: `orders.events`, `billing.events`, `notify.send`

#### S3 — фото услуг, документы, вложения чатов

#### Redis — кэш каталога, счётчики, сессии

#### Docker Compose (dev) → Kubernetes (staging, prod)

## Ключевые потоки

### Оформление заказа

- Витрина → `internal/api` → `internal/orders`

- `internal/orders` → Kafka `orders.events` → `internal/billing`

- `internal/billing` → PSP → webhook → смена статуса заказа

### Выплата исполнителю

- закрытие заказа → `internal/billing` держит холд 3 дня

- `internal/billing` → PSP выплата → `internal/notify` уведомляет

### Публикация услуги

- исполнитель → `internal/catalog` → `internal/moderation` → витрина

### Онбординг исполнителя

- регистрация → верификация документов → первый тариф → публикация услуги

### Публикация релиза

- CI: тесты → docker build → staging → smoke → prod

## Кросс-функциональное

### Авторизация

- JWT access + refresh, роли buyer/seller/admin

### Наблюдаемость

- OpenTelemetry → Prometheus, Grafana; алерты в Telegram

### Конфигурация

- env + viper; фичефлаги в таблице БД

### Тесты

- Go: unit + integration на testcontainers

- e2e: Playwright по витрине и админке

### Локализация

- i18next, RU/EN, переводы прогоняются в CI

### Данные и бэкапы

- ежедневный pg_dump в S3, retention 30 дней

## Структура файлов

### Корень

- `README.md` — назначение проекта и запуск
- `docker-compose.yml` — локальная инфраструктура: БД, Kafka, приложение
- `Makefile` — типовые команды: сборка, миграции, генерация клиента

### `cmd/server/`

- `main.go` — точка входа: конфигурация, подключение зависимостей

### `internal/api/`

- `router.go` — регистрация маршрутов и middleware
- `handlers_orders.go` — обработчики заказов
- `openapi.yaml` — OpenAPI-спека, из неё генерируется `api-client`

### `internal/orders/`

- `service.go` — жизненный цикл заказа, saga
- `repo.go` — запросы к таблице orders

### `internal/billing/`

- `service.go` — счета и холды
- `psp_yookassa.go` — адаптер эквайринга ЮKassa
- `webhooks.go` — приём колбэков PSP

### `web/`

- `icons/*.svg` (120 шт.) — иконки витрины и кабинета
- `src/api/client.ts` — сгенерированный API-клиент

### `docs/`

- `architecture.md` — решение по saga выплат (ADR)
