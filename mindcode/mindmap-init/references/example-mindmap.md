# OrderHub — маркетплейс услуг: заказчики находят исполнителей, платформа держит комиссию

## Слои и домены

### Backend — Go-монолит

#### `cmd/server` — точка входа: конфиг, graceful shutdown

#### `internal/api` — HTTP-роутинг, middleware, OpenAPI-спека

#### `internal/orders` — жизненный цикл заказа, saga выплат

#### `internal/billing` — счета, тарифы, эквайринг ЮKassa

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
