# Авито.Кухня — MVP платформы доставки еды

[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://www.postgresql.org/)
[![Docker Compose](https://img.shields.io/badge/Docker_Compose-v2-2496ED?logo=docker)](https://docs.docker.com/compose/)

---

## Описание проекта

**Авито.Кухня** — MVP-сервис доставки еды, встроенный в экосистему Авито.  
Платформа объединяет **клиентов**, **рестораны/кафе/магазины** через единый API.

### Решаемая бизнес-задача

| Участник | Проблема | Решение |
|---|---|---|
| **Клиент** | Нет единого агрегатора еды с доверенными заведениями Авито | Витрина ресторанов с меню, корзиной и трекингом заказа |
| **Заведение** | Нет инструмента для приёма и обработки онлайн-заказов | API и вебхуки для получения и подтверждения заказов |
| **Авито** | Монетизация через комиссию с заказов, удержание пользователей | Нативная интеграция в экосистему |

В рамках MVP реализованы:

- Просмотр списка ресторанов и их меню
- Создание заказа из позиций меню
- Передача заказа в ресторан через HTTP-вебхук
- Обновление статуса заказа рестораном
- Автоматическая OpenAPI-документация

---

## CJM — Customer Journey Map

### Путь клиента и заведения

```mermaid
flowchart TD
    subgraph CLIENT[" Клиент"]
        C1([Открывает Авито.Кухня])
        C2[GET /restaurants\nПросматривает список ресторанов]
        C3[Выбирает ресторан]
        C4[GET /restaurants/id/menu\nПросматривает меню]
        C5[Добавляет блюда в корзину]
        C6{Корзина не пуста?}
        C7[POST /orders\nОформляет заказ]
        C8[Получает order_id\nСтатус: PENDING]
        C9[GET /orders/id\nОтслеживает статус]
        C10{Статус\nDELIVERED?}
        C11([Получает заказ ])
        C12([Продолжает выбор блюд])
    end

    subgraph RESTAURANT[" Заведение — Mock Restaurant API"]
        R1[POST /webhook/order\nПолучает вебхук от Main API]
        R2{Все позиции\nдоступны?}
        R3[Статус → CONFIRMED\nПодтверждает заказ]
        R4[Готовит заказ]
        R5[PATCH /orders/id/status\nСтатус → READY]
        R6[Передаёт курьеру]
        R7[PATCH /orders/id/status\nСтатус → DELIVERED]
        R8([Статус → CANCELLED\nОтклоняет заказ])
    end

    C1 --> C2 --> C3 --> C4 --> C5 --> C6
    C6 -- да --> C7 --> C8 --> C9 --> C10
    C10 -- нет, ждёт --> C9
    C10 -- да --> C11
    C6 -- нет --> C12

    C7 -- вебхук --> R1
    R1 --> R2
    R2 -- да --> R3 --> R4 --> R5 --> R6 --> R7
    R2 -- нет --> R8
    R7 -- обновляет статус --> C10
```

---

## Архитектура системы — C4 Container Diagram

```mermaid
flowchart TD
    USER([" Клиент\nПользователь платформы,\nзаказывает еду через браузер"])

    subgraph SYSTEM["Авито.Кухня"]
        WEB[" Web Client\n\nBrowser / SPA\n\nПользовательский интерфейс.\nПросмотр меню, оформление\nи отслеживание заказов."]

        API[" Main API\n\nPython 3.13 / FastAPI\n\nМодульный монолит.\nОбрабатывает запросы клиента,\nуправляет заказами,\nотправляет вебхуки в рестораны."]

        DB[(" PostgreSQL 16\n\nРеляционная СУБД\n\nХранит рестораны, меню,\nзаказы и их позиции.\nМиграции через Alembic.")]

        MOCK[" Mock Restaurant API\n\nPython 3.13 / FastAPI\n\nЭмулирует логику\nресторана-партнёра.\nПринимает вебхуки,\nобновляет статус заказа."]
    end

    USER -- "HTTPS / Browser" --> WEB
    WEB -- "HTTP/JSON\nREST API запросы" --> API
    API -- "asyncpg / SQLAlchemy\nЧитает / Пишет" --> DB
    API -- "HTTP POST /webhook/order\nОтправляет вебхук о заказе" --> MOCK
    MOCK -- "HTTP PATCH /orders/id/status\nОбновляет статус заказа" --> API
```

---

## Архитектура приложения — Модульный монолит

Выбранная архитектура — **модульный монолит** (Modular Monolith).  
Весь код Main API находится в одном процессе и одном репозитории, но разделён на **независимые модули** с чёткими границами ответственности.

> Подробное обоснование выбора: [ADR-002](./docs/adr/ADR-002-modular-monolith.md)

### Структура модулей

```
app/
 restaurants/        # Модуль: заведения
    router.py       # GET /restaurants, GET /restaurants/{id}
    service.py      # Бизнес-логика
    models.py       # SQLAlchemy-модель Restaurant
    schemas.py      # Pydantic-схемы

 menu_items/         # Модуль: позиции меню
    router.py       # GET /restaurants/{id}/menu
    service.py
    models.py       # SQLAlchemy-модель MenuItem
    schemas.py

 orders/             # Модуль: заказы
    router.py       # POST /orders, GET /orders/{id}, PATCH /orders/{id}/status
    service.py      # Создание заказа + отправка вебхука
    models.py       # SQLAlchemy-модель Order
    schemas.py

 order_items/        # Модуль: позиции заказа
    models.py       # SQLAlchemy-модель OrderItem
    schemas.py

 core/               # Ядро: конфигурация, БД, зависимости
    config.py       # pydantic-settings
    database.py     # Async SQLAlchemy engine + session
    dependencies.py

 main.py             # Точка входа FastAPI-приложения
```

### Взаимодействие модулей

```mermaid
flowchart LR
    subgraph MAIN_API["Main API"]
        R[restaurants]
        MI[menu_items]
        O[orders]
        OI[order_items]
        C[core]
    end

    PG[(PostgreSQL)]
    MRA["Mock Restaurant API"]

    R -- использует DB session --> C
    MI -- использует DB session --> C
    O -- использует DB session --> C
    OI -- использует DB session --> C

    MI -. FK: restaurant_id .-> R
    OI -. FK: order_id .-> O
    OI -. FK: menu_item_id .-> MI

    O -- "HTTP POST /webhook/order" --> MRA
    MRA -- "HTTP PATCH /orders/id/status" --> O

    C -- asyncpg --> PG
```

---

## Схема базы данных

> Подробное обоснование: [ADR-003](./docs/adr/ADR-003-database-schema.md)

### Выбор технологий

| Компонент | Технология | Обоснование |
|---|---|---|
| **СУБД** | PostgreSQL 16 | Надёжность, ACID, JSON-поддержка, зрелая экосистема |
| **ORM** | SQLAlchemy 2.x (async) | Стандарт Python, поддержка asyncio, типобезопасность |
| **Миграции** | Alembic | Нативная интеграция с SQLAlchemy, автогенерация diff |
| **Драйвер** | asyncpg | Высокопроизводительный async PostgreSQL драйвер |

### Таблицы и связи

```mermaid
erDiagram
    restaurants {
        UUID id PK
        VARCHAR name
        TEXT description
        VARCHAR address
        BOOLEAN is_active
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }

    menu_items {
        UUID id PK
        UUID restaurant_id FK
        VARCHAR name
        TEXT description
        NUMERIC price
        BOOLEAN is_available
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }

    orders {
        UUID id PK
        UUID user_id
        UUID restaurant_id FK
        VARCHAR status
        VARCHAR delivery_address
        NUMERIC total_price
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }

    order_items {
        UUID id PK
        UUID order_id FK
        UUID menu_item_id FK
        INTEGER quantity
        NUMERIC unit_price
    }

    restaurants ||--o{ menu_items : "имеет"
    restaurants ||--o{ orders : "получает"
    orders ||--o{ order_items : "содержит"
    menu_items ||--o{ order_items : "входит в"
```

### Описание таблиц

#### `restaurants` — Заведения

| Поле | Тип | Ограничения | Описание |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Уникальный идентификатор |
| `name` | VARCHAR(255) | NOT NULL | Название заведения |
| `description` | TEXT | | Описание заведения |
| `address` | VARCHAR(500) | NOT NULL | Адрес заведения |
| `is_active` | BOOLEAN | DEFAULT TRUE | Флаг активности на платформе |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Дата регистрации |
| `updated_at` | TIMESTAMPTZ | | Дата последнего обновления |

#### `menu_items` — Позиции меню

| Поле | Тип | Ограничения | Описание |
|---|---|---|---|
| `id` | UUID | PK | Уникальный идентификатор |
| `restaurant_id` | UUID | FK → restaurants.id, NOT NULL | Принадлежность ресторану |
| `name` | VARCHAR(255) | NOT NULL | Название блюда |
| `description` | TEXT | | Описание блюда |
| `price` | NUMERIC(10,2) | NOT NULL, CHECK > 0 | Цена в рублях |
| `is_available` | BOOLEAN | DEFAULT TRUE | Доступность для заказа |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Дата добавления |
| `updated_at` | TIMESTAMPTZ | | Дата последнего обновления |

#### `orders` — Заказы

| Поле | Тип | Ограничения | Описание |
|---|---|---|---|
| `id` | UUID | PK | Уникальный идентификатор |
| `user_id` | UUID | NOT NULL | ID пользователя из заголовка `X-User-ID` |
| `restaurant_id` | UUID | FK → restaurants.id, NOT NULL | Ресторан-исполнитель |
| `status` | VARCHAR(20) | NOT NULL | Статус: PENDING, CONFIRMED, COOKING, READY, DELIVERED, CANCELLED |
| `delivery_address` | VARCHAR(500) | NOT NULL | Адрес доставки |
| `total_price` | NUMERIC(10,2) | NOT NULL | Итоговая сумма заказа |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Дата создания |
| `updated_at` | TIMESTAMPTZ | | Дата последнего обновления |

#### `order_items` — Позиции заказа

| Поле | Тип | Ограничения | Описание |
|---|---|---|---|
| `id` | UUID | PK | Уникальный идентификатор |
| `order_id` | UUID | FK → orders.id, NOT NULL | Принадлежность заказу |
| `menu_item_id` | UUID | FK → menu_items.id, NOT NULL | Блюдо из меню |
| `quantity` | INTEGER | NOT NULL, CHECK > 0 | Количество |
| `unit_price` | NUMERIC(10,2) | NOT NULL | Цена на момент заказа (снимок) |

> **Важно:** `unit_price` в `order_items` сохраняет цену на момент оформления заказа — защита от изменения цен меню постфактум.

### Жизненный цикл заказа

```
PENDING -> CONFIRMED -> COOKING -> READY -> DELIVERED
                                 |
                                 v
                             CANCELLED
```

---

## Технический стек

> Подробное обоснование: [ADR-001](./docs/adr/ADR-001-tech-stack.md)

### Основной стек

| Категория | Технология | Назначение |
|---|---|---|
| **Язык** | Python 3.13 | Основной язык разработки |
| **Фреймворк** | FastAPI | Асинхронный REST API фреймворк |
| **Async runtime** | asyncio | Асинхронное выполнение I/O-операций |
| **БД** | PostgreSQL 16 | Основное хранилище данных |
| **ORM** | SQLAlchemy 2.x (async) | Работа с БД через Python-объекты |
| **Драйвер БД** | asyncpg | Асинхронный PostgreSQL-клиент |
| **Миграции** | Alembic | Версионирование схемы БД |
| **Валидация** | Pydantic v2 | Типизация запросов/ответов API |
| **Конфигурация** | pydantic-settings | Загрузка настроек из `.env` |
| **Управление зависимостями** | Poetry | Детерминированная сборка, `pyproject.toml` |
| **HTTP-клиент** | httpx | Async HTTP-запросы (вебхуки) |
| **Инфраструктура** | Docker Compose | Запуск всей системы одной командой |
| **Тестирование** | Pytest + pytest-asyncio | Unit и интеграционные тесты |
| **Документация API** | OpenAPI (встроен в FastAPI) | Автогенерация `/docs` и `/openapi.json` |
| **Линтер/форматтер** | Ruff | Быстрый Python-линтер и форматтер |
| **Тайп-чекер** | mypy | Статический анализ типов |

### Требования по асинхронности

Все операции с I/O выполняются **асинхронно**:

- FastAPI обрабатывает запросы через `async def` эндпоинты
- SQLAlchemy использует `AsyncSession` + `asyncpg` для неблокирующих запросов к БД
- Отправка вебхуков выполняется через `httpx.AsyncClient`
- Нет блокирующих вызовов в основном потоке событий

### CI/CD

Пайплайн настроен через **GitHub Actions**:

```
Push / PR -> lint (Ruff + mypy) -> test (Pytest) -> build Docker image
```

| Стадия | Инструмент | Описание |
|---|---|---|
| `lint` | Ruff, mypy | Проверка стиля и типов |
| `test` | Pytest | Запуск тестов с тестовой БД |
| `build` | Docker | Сборка образов |

### OpenAPI документация

FastAPI автоматически генерирует интерактивную документацию:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## ADR — Architectural Decision Records

Все архитектурные решения задокументированы в директории [`docs/adr/`](./docs/adr/):

| № | Решение | Файл |
|---|---|---|
| ADR-001 | Выбор технического стека (Python, FastAPI, PostgreSQL) | [ADR-001](./docs/adr/ADR-001-tech-stack.md) |
| ADR-002 | Выбор архитектуры модульного монолита | [ADR-002](./docs/adr/ADR-002-modular-monolith.md) |
| ADR-003 | Разработка схемы базы данных | [ADR-003](./docs/adr/ADR-003-database-schema.md) |
| ADR-004 | Использование HTTP Webhooks вместо брокера сообщений | [ADR-004](./docs/adr/ADR-004-webhooks-vs-broker.md) |
| ADR-005 | Отказ от сервиса авторизации (X-User-ID) | [ADR-005](./docs/adr/ADR-005-no-auth-service.md) |

---

## Запуск проекта

### Предварительные требования

- [Docker](https://docs.docker.com/get-docker/) >= 24.0
- [Docker Compose](https://docs.docker.com/compose/) >= 2.20

### Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone <repository-url>
cd avito-kitchen

# 2. Создать файл окружения
cp .env.example .env

# 3. Запустить все сервисы
docker compose up --build
```

### Конфигурация `.env`

```dotenv
# Main API
DATABASE_URL=postgresql+asyncpg://kitchen:kitchen@postgres:5432/kitchen_db
MOCK_RESTAURANT_WEBHOOK_URL=http://mock-restaurant:8001/webhook/order
APP_HOST=0.0.0.0
APP_PORT=8000

# Mock Restaurant API
MAIN_API_URL=http://main-api:8000
MOCK_HOST=0.0.0.0
MOCK_PORT=8001

# PostgreSQL
POSTGRES_USER=kitchen
POSTGRES_PASSWORD=kitchen
POSTGRES_DB=kitchen_db
```

### Сервисы после запуска

| Сервис | URL | Описание |
|---|---|---|
| **Main API** | http://localhost:8000 | Основной REST API |
| **Main API Docs** | http://localhost:8000/docs | Swagger UI |
| **Mock Restaurant** | http://localhost:8001 | Mock-сервис ресторана |
| **Mock Restaurant Docs** | http://localhost:8001/docs | Swagger UI Mock |
| **PostgreSQL** | localhost:5432 | База данных |

### Структура Docker Compose

```yaml
# docker-compose.yml (упрощённо)
services:
  postgres:        # PostgreSQL 16
  main-api:        # Main API (зависит от postgres)
  mock-restaurant: # Mock Restaurant API (зависит от main-api)
```

### Полезные команды

```bash
# Запустить в фоне
docker compose up -d

# Посмотреть логи Main API
docker compose logs -f main-api

# Применить миграции вручную
docker compose exec main-api alembic upgrade head

# Запустить тесты
docker compose exec main-api pytest

# Остановить все сервисы
docker compose down

# Остановить и удалить volumes (сброс БД)
docker compose down -v
```

---

## Структура репозитория

```
avito-kitchen/
 app/                          # Main API (модульный монолит)
    restaurants/              # Модуль: заведения
    menu_items/               # Модуль: позиции меню
    orders/                   # Модуль: заказы
    order_items/              # Модуль: позиции заказа
    core/                     # Конфигурация, БД, зависимости
    main.py                   # Точка входа
 mock_restaurant/              # Mock Restaurant API
    main.py
 alembic/                      # Миграции БД
    versions/
 tests/                        # Тесты
 docs/
    adr/                      # Architectural Decision Records
 .github/
    workflows/                # CI/CD пайплайны
 docker-compose.yml
 Dockerfile                    # Main API
 Dockerfile.mock               # Mock Restaurant API
 pyproject.toml                # Poetry зависимости
 alembic.ini
 .env.example
 README.md
```

---

## Допустимые упрощения MVP

Следующие вещи намеренно **не реализованы** в MVP и могут быть добавлены при масштабировании:

| Упрощение | Обоснование | Путь к production |
|---|---|---|
| Нет JWT-авторизации | Доверяем заголовку `X-User-ID` | Добавить OAuth2 / JWT-middleware |
| Нет брокера сообщений | HTTP-вебхуки достаточны для MVP | Заменить на Kafka / RabbitMQ |
| Нет пагинации | Небольшой объём данных на MVP | Добавить `limit/offset` или cursor |
| Нет кэширования | Нет требований к производительности | Добавить Redis |
| Нет rate limiting | Нет внешних пользователей | Добавить через API Gateway |
| Mock-ресторан один | Достаточно для демонстрации интеграции | Реализовать полноценный партнёрский API |
