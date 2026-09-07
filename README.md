# 🍽️ Авито.Кухня — MVP платформы доставки еды

[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://www.postgresql.org/)
[![Docker Compose](https://img.shields.io/badge/Docker_Compose-v2-2496ED?logo=docker)](https://docs.docker.com/compose/)

---

## 📌 Описание проекта

**Авито.Кухня** — MVP-сервис доставки еды, встроенный в экосистему Авито.  
Платформа объединяет **клиентов**, **рестораны/кафе/магазины** через единый API.

### Решаемая бизнес-задача

| Участник | Проблема | Решение |
|---|---|---|
| **Клиент** | Нет единого агрегатора еды с доверенными заведениями Авито | Витрина ресторанов с меню, корзиной и трекингом заказа |
| **Заведение** | Нет инструмента для приёма и обработки онлайн-заказов | API и вебхуки для получения и подтверждения заказов |
| **Авито** | Монетизация через комиссию с заказов, удержание пользователей | Нативная интеграция в экосистему |

В рамках MVP реализованы:

- 🔍 Просмотр списка ресторанов и их меню
- 🛒 Создание заказа из позиций меню
- 📡 Передача заказа в ресторан через HTTP-вебхук
- 📦 Обновление статуса заказа рестораном
- 📄 Автоматическая OpenAPI-документация

---

## 🗺️ CJM — Customer Journey Map

### Путь клиента и заведения

```plantuml
@startuml CJM_Avito_Kitchen
!theme plain
skinparam backgroundColor #FAFAFA
skinparam activity {
  BackgroundColor #E8F5E9
  BorderColor #388E3C
  FontColor #1B5E20
  StartColor #43A047
  EndColor #E53935
  ArrowColor #388E3C
}
skinparam swimlaneBackgroundColor #F1F8E9
skinparam swimlaneBorderColor #AED581

title Авито.Кухня — Customer Journey Map

|#DCEDC8| Клиент |
start
:Открывает Авито.Кухня\n(веб-клиент);
:Просматривает список ресторанов\nGET /restaurants;
:Выбирает ресторан;
:Просматривает меню\nGET /restaurants/{id}/menu;
:Добавляет блюда в корзину\n(клиентская логика);

if (Корзина не пуста?) then (да)
  :Оформляет заказ\nPOST /orders;
  :Получает подтверждение\n(order_id, статус PENDING);
  :Отслеживает статус заказа\nGET /orders/{id};

  repeat
    :Проверяет статус;
  repeat while (Статус не DELIVERED?) is (нет, ждёт)
  -> да;

  :Получает заказ!;
  stop
else (нет)
  :Продолжает выбор блюд;
  stop
endif

|#FFF9C4| Заведение (Mock Restaurant API) |
:Получает вебхук\nPOST /webhook/order\n(от Main API);
:Проверяет позиции заказа;

if (Все позиции доступны?) then (да)
  :Подтверждает заказ\n(статус CONFIRMED);
  :Готовит заказ;
  :Уведомляет о готовности\nPATCH /orders/{id}/status\n-> статус READY;
  :Передаёт заказ курьеру;
  :Заказ доставлен\nPATCH /orders/{id}/status\n-> статус DELIVERED;
  stop
else (нет)
  :Отклоняет заказ\n(статус CANCELLED);
  stop
endif

@enduml
```

---

## 🏗️ Архитектура системы — C4 Container Diagram

```plantuml
@startuml C4_Container_Avito_Kitchen
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

LAYOUT_WITH_LEGEND()

title Авито.Кухня — C4 Container Diagram (Level 2)

Person(client, "Клиент", "Пользователь платформы,\nзаказывает еду через браузер")

System_Boundary(avito_kitchen, "Авито.Кухня") {

  Container(web_client, "Web Client", "Browser / SPA", "Пользовательский интерфейс.\nПросмотр меню, оформление\nи отслеживание заказов.")

  Container(main_api, "Main API", "Python 3.13 / FastAPI", "Модульный монолит.\nОбрабатывает запросы клиента,\nуправляет заказами,\nотправляет вебхуки в рестораны.")

  ContainerDb(postgres, "PostgreSQL 16", "Реляционная СУБД", "Хранит рестораны, меню,\nзаказы и их позиции.\nМиграции через Alembic.")

  Container(mock_restaurant, "Mock Restaurant API", "Python 3.13 / FastAPI", "Эмулирует логику\nресторана-партнёра.\nПринимает вебхуки,\nобновляет статус заказа.")
}

Rel(client, web_client, "Открывает", "HTTPS / Browser")
Rel(web_client, main_api, "REST API запросы", "HTTP/JSON")
Rel(main_api, postgres, "Читает / Пишет", "asyncpg / SQLAlchemy")
Rel(main_api, mock_restaurant, "Отправляет вебхук о заказе", "HTTP POST /webhook/order")
Rel(mock_restaurant, main_api, "Обновляет статус заказа", "HTTP PATCH /orders/{id}/status")

@enduml
```

---

## 🧩 Архитектура приложения — Модульный монолит

Выбранная архитектура — **модульный монолит** (Modular Monolith).  
Весь код Main API находится в одном процессе и одном репозитории, но разделён на **независимые модули** с чёткими границами ответственности.

> 📄 Подробное обоснование выбора: [ADR-002](./docs/adr/ADR-002-modular-monolith.md)

### Структура модулей

```
app/
├── restaurants/        # Модуль: заведения
│   ├── router.py       # GET /restaurants, GET /restaurants/{id}
│   ├── service.py      # Бизнес-логика
│   ├── models.py       # SQLAlchemy-модель Restaurant
│   └── schemas.py      # Pydantic-схемы
│
├── menu_items/         # Модуль: позиции меню
│   ├── router.py       # GET /restaurants/{id}/menu
│   ├── service.py
│   ├── models.py       # SQLAlchemy-модель MenuItem
│   └── schemas.py
│
├── orders/             # Модуль: заказы
│   ├── router.py       # POST /orders, GET /orders/{id}, PATCH /orders/{id}/status
│   ├── service.py      # Создание заказа + отправка вебхука
│   ├── models.py       # SQLAlchemy-модель Order
│   └── schemas.py
│
├── order_items/        # Модуль: позиции заказа
│   ├── models.py       # SQLAlchemy-модель OrderItem
│   └── schemas.py
│
├── core/               # Ядро: конфигурация, БД, зависимости
│   ├── config.py       # pydantic-settings
│   ├── database.py     # Async SQLAlchemy engine + session
│   └── dependencies.py
│
└── main.py             # Точка входа FastAPI-приложения
```

### Взаимодействие модулей

```plantuml
@startuml Module_Interaction
!theme plain
skinparam packageStyle rectangle
skinparam backgroundColor #FAFAFA
skinparam component {
  BackgroundColor #E3F2FD
  BorderColor #1565C0
  FontColor #0D47A1
}

title Авито.Кухня — Взаимодействие модулей Main API

package "Main API" {
  [restaurants] as R
  [menu_items] as MI
  [orders] as O
  [order_items] as OI
  [core] as C
}

database "PostgreSQL" as PG

cloud "Mock Restaurant API" as MRA

R --> C : использует DB session
MI --> C : использует DB session
O --> C : использует DB session
OI --> C : использует DB session

MI ..> R : FK: restaurant_id
OI ..> O : FK: order_id
OI ..> MI : FK: menu_item_id

O --> MRA : HTTP POST /webhook/order\n(при создании заказа)
MRA --> O : HTTP PATCH /orders/{id}/status\n(обновление статуса)

C --> PG : asyncpg

@enduml
```

---

## 🗄️ Схема базы данных

> 📄 Подробное обоснование: [ADR-003](./docs/adr/ADR-003-database-schema.md)

### Выбор технологий

| Компонент | Технология | Обоснование |
|---|---|---|
| **СУБД** | PostgreSQL 16 | Надёжность, ACID, JSON-поддержка, зрелая экосистема |
| **ORM** | SQLAlchemy 2.x (async) | Стандарт Python, поддержка asyncio, типобезопасность |
| **Миграции** | Alembic | Нативная интеграция с SQLAlchemy, автогенерация diff |
| **Драйвер** | asyncpg | Высокопроизводительный async PostgreSQL драйвер |

### Таблицы и связи

```plantuml
@startuml Database_Schema
!theme plain
skinparam backgroundColor #FAFAFA
skinparam class {
  BackgroundColor #EDE7F6
  BorderColor #4527A0
  FontColor #1A237E
  HeaderBackgroundColor #7E57C2
  HeaderFontColor #FFFFFF
}

title Авито.Кухня — Схема базы данных

entity "restaurants" as restaurants {
  * id : UUID <<PK>>
  --
  * name : VARCHAR(255) NOT NULL
  * description : TEXT
  * address : VARCHAR(500) NOT NULL
  * is_active : BOOLEAN DEFAULT TRUE
  * created_at : TIMESTAMPTZ DEFAULT NOW()
  * updated_at : TIMESTAMPTZ
}

entity "menu_items" as menu_items {
  * id : UUID <<PK>>
  --
  * restaurant_id : UUID <<FK>>
  * name : VARCHAR(255) NOT NULL
  * description : TEXT
  * price : NUMERIC(10,2) NOT NULL
  * is_available : BOOLEAN DEFAULT TRUE
  * created_at : TIMESTAMPTZ DEFAULT NOW()
  * updated_at : TIMESTAMPTZ
}

entity "orders" as orders {
  * id : UUID <<PK>>
  --
  * user_id : UUID NOT NULL
  * restaurant_id : UUID <<FK>>
  * status : VARCHAR(20) NOT NULL
  * delivery_address : VARCHAR(500) NOT NULL
  * total_price : NUMERIC(10,2) NOT NULL
  * created_at : TIMESTAMPTZ DEFAULT NOW()
  * updated_at : TIMESTAMPTZ
}

entity "order_items" as order_items {
  * id : UUID <<PK>>
  --
  * order_id : UUID <<FK>>
  * menu_item_id : UUID <<FK>>
  * quantity : INTEGER NOT NULL
  * unit_price : NUMERIC(10,2) NOT NULL
}

restaurants ||--o{ menu_items : "1 ресторан\nимеет N позиций меню"
restaurants ||--o{ orders : "1 ресторан\nполучает N заказов"
orders ||--o{ order_items : "1 заказ\nсодержит N позиций"
menu_items ||--o{ order_items : "1 позиция меню\nвходит в N заказов"

@enduml
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

## 🛠️ Технический стек

> 📄 Подробное обоснование: [ADR-001](./docs/adr/ADR-001-tech-stack.md)

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

## 📋 ADR — Architectural Decision Records

Все архитектурные решения задокументированы в директории [`docs/adr/`](./docs/adr/):

| № | Решение | Файл |
|---|---|---|
| ADR-001 | Выбор технического стека (Python, FastAPI, PostgreSQL) | [ADR-001](./docs/adr/ADR-001-tech-stack.md) |
| ADR-002 | Выбор архитектуры модульного монолита | [ADR-002](./docs/adr/ADR-002-modular-monolith.md) |
| ADR-003 | Разработка схемы базы данных | [ADR-003](./docs/adr/ADR-003-database-schema.md) |
| ADR-004 | Использование HTTP Webhooks вместо брокера сообщений | [ADR-004](./docs/adr/ADR-004-webhooks-vs-broker.md) |
| ADR-005 | Отказ от сервиса авторизации (X-User-ID) | [ADR-005](./docs/adr/ADR-005-no-auth-service.md) |

---

## 🚀 Запуск проекта

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

## 📁 Структура репозитория

```
avito-kitchen/
├── app/                          # Main API (модульный монолит)
│   ├── restaurants/              # Модуль: заведения
│   ├── menu_items/               # Модуль: позиции меню
│   ├── orders/                   # Модуль: заказы
│   ├── order_items/              # Модуль: позиции заказа
│   ├── core/                     # Конфигурация, БД, зависимости
│   └── main.py                   # Точка входа
├── mock_restaurant/              # Mock Restaurant API
│   └── main.py
├── alembic/                      # Миграции БД
│   └── versions/
├── tests/                        # Тесты
├── docs/
│   └── adr/                      # Architectural Decision Records
├── .github/
│   └── workflows/                # CI/CD пайплайны
├── docker-compose.yml
├── Dockerfile                    # Main API
├── Dockerfile.mock               # Mock Restaurant API
├── pyproject.toml                # Poetry зависимости
├── alembic.ini
├── .env.example
└── README.md
```

---

## ⚠️ Допустимые упрощения MVP

Следующие вещи намеренно **не реализованы** в MVP и могут быть добавлены при масштабировании:

| Упрощение | Обоснование | Путь к production |
|---|---|---|
| Нет JWT-авторизации | Доверяем заголовку `X-User-ID` | Добавить OAuth2 / JWT-middleware |
| Нет брокера сообщений | HTTP-вебхуки достаточны для MVP | Заменить на Kafka / RabbitMQ |
| Нет пагинации | Небольшой объём данных на MVP | Добавить `limit/offset` или cursor |
| Нет кэширования | Нет требований к производительности | Добавить Redis |
| Нет rate limiting | Нет внешних пользователей | Добавить через API Gateway |
| Mock-ресторан один | Достаточно для демонстрации интеграции | Реализовать полноценный партнёрский API |
