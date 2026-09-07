CONTEXT:
Проект: MVP платформы доставки "Авито.Кухня".
Стек: Python 3.13, FastAPI, PostgreSQL, Docker Compose.
Архитектура системы: SOA (Main API + Mock API). 
Архитектура самого Main API: Модульный монолит.
Текущее состояние: Архитектура спроектирована, README.md готов, схема БД утверждена (4 сущности: restaurants, menu_items, orders, order_items).
Аутентификация: Отсутствует (доверяем клиентскому заголовку X-User-ID).
Транспорт: Синхронный HTTP / Вебхуки. 

ROLE:
Database Administrator, Senior Backend Developer

TASK:
Необходимо заложить базовую инфраструктуру проекта, инициализировать базу данных и настроить миграции. 
Выполни следующие шаги:
1. Создай конфигурацию проекта и зависимостей `pyproject.toml` (Poetry). Укажи основные зависимости (FastAPI, uvicorn, sqlalchemy, asyncpg, alembic, pydantic-settings, pydantic и др.). Добавь develop зависимости (ruff, flake8 и др.).
2. Создай `docker-compose.yml`, который поднимает только сервис БД (PostgreSQL 16) с пробросом портов (5432:5432), томом для данных и healthcheck.
3. Настрой базовую конфигурацию приложения в `app/core/config.py` (через pydantic-settings) и `.env.example`.
4. Настрой асинхронное подключение к БД в `app/core/database.py` (инициализация `async_engine`, `async_sessionmaker` и базового класса `Base` для SQLAlchemy 2.0).
5. Создай SQLAlchemy-модели согласно спроектированной схеме в README.md. Размести их в соответствующих модулях модульного монолита:
   - `app/restaurants/models.py`
   - `app/menu_items/models.py`
   - `app/orders/models.py`
   - `app/order_items/models.py`
6. Инициализируй Alembic (`alembic init -t async alembic`), настрой `alembic/env.py` для поддержки асинхронности и автогенерации.
7. Сгенерируй первую миграцию создания таблиц.

INPUT / REFERENCES:
- @README.md (Ориентируйся на раздел "Схема базы данных" для написания моделей: типы колонок, ограничения, связи).
- @docs/adr/*

CONSTRAINTS & EXECUTION RULES:
- Строгий скоуп: реализуй исключительно то, что явно указано в блоке TASK.
- Не пиши бизнес-логику (сервисы) и роутеры на этом шаге.
- Используй строгий синтаксис SQLAlchemy 2.0 (`Mapped`, `mapped_column`).
- Все внешние ключи (ForeignKey) и отношения (relationship) должны быть прописаны корректно.

WHAT TO AVOID:
- Не используй синхронные драйверы (никакого psycopg2, только asyncpg).
- Не добавляй в `docker-compose.yml` сервисы API на этом этапе (только postgres).
- Не пиши заглушки (TODO/pass). Весь код должен быть рабочим.
- Не взаимодействуй с Git, пока я не попрошу этого напрямую.
- Не добавляй массивных ASCII-форматированных комментариев в код. Максимум небольшие пояснения и разделения на блоки.

DEFINITION OF DONE:
Задача считается завершенной только тогда, когда:
1. Созданы файлы конфигурации инфраструктуры (`pyproject.toml`, `docker-compose.yml`, `.env.example`).
2. Настроено ядро работы с БД (`config.py`, `database.py`).
3. Модели SQLAlchemy строго соответствуют схеме из README.md (включая ограничения и связи).
4. Файлы Alembic настроены для работы с асинхронным движком, и готов скрипт первой миграции.

OUTPUT FORMAT:
1. Полный код сгенерированных и измененных файлов с указанием пути (например: `app/restaurants/models.py`).
2. Краткая инструкция по запуску: как поднять БД через Docker Compose и как применить миграцию.
