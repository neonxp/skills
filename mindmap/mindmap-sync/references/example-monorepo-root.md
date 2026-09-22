# OrderHub — монорепа: маркетплейс услуг

## Подпроекты

### `services/backend` — Go-монолит: заказы, биллинг, каталог

### `apps/web` — React SPA: витрина, кабинет, админка

### `apps/mobile` — Flutter: покупатель и исполнитель

### `packages/ui` — общая дизайн-система компонентов

### `infra` — Terraform, Helm-чарты, окружения

## Межпроектные потоки

### Оформление заказа

- `apps/web` → `services/backend` → Kafka → `apps/mobile` (push исполнителю)

### Выплата исполнителю

- `services/backend` → PSP → webhook → `services/backend` → `apps/mobile`

### Обновление контрактов

- OpenAPI-спека `services/backend` → генерация `api-client` в `apps/web`

## Кросс-функциональное

### CI/CD

- GitHub Actions: тесты → сборка образов → staging → prod, общий пайплайн

### Наблюдаемость

- общая Grafana, метки `project` на всех дашбордах

### Зависимости

- `packages/ui` публикуется в приватный npm-registry, версии через Changesets
