CONTEXT:
Проект: MVP платформы доставки "Авито.Кухня".
Стек: Python 3.13, FastAPI, PostgreSQL, Docker Compose, SQLAlchemy 2.0 (async).
Архитектура системы: SOA (Main API + Mock API). 
Архитектура самого Main API: Модульный монолит.
Текущее состояние: Инфраструктура и БД настроены, модели SQLAlchemy готовы, миграции применены.
Аутентификация: Отсутствует (доверяем клиентскому заголовку X-User-ID).
Транспорт: Синхронный HTTP / Вебхуки (через httpx). 

ROLE:
Senior Backend Developer, API Architect

TASK:
Необходимо реализовать бизнес-логику и REST API (Main API) для ядра приложения. 
Выполни следующие шаги:
1. Создай `app/core/dependencies.py`:
   - Зависимость `get_db` для получения асинхронной сессии БД.
   - Зависимость `get_current_user_id` для извлечения `x_user_id: UUID = Header(...)`.
2. В модуле `restaurants` (`schemas.py`, `service.py`, `router.py`):
   - Эндпоинт `GET /restaurants` — получить список активных заведений.
3. В модуле `menu_items` (`schemas.py`, `service.py`, `router.py`):
   - Эндпоинт `GET /restaurants/{id}/menu` — получить доступные позиции меню конкретного ресторана.
4. В модуле `orders` (`schemas.py`, `service.py`, `router.py`):
   - Эндпоинт `POST /orders` (Создание заказа). Принимает список id блюд и их количество. 
     **Важная логика сервиса:** Бэкенд должен сам достать цены из `menu_items`, проверить доступность блюд (is_available), рассчитать `total_price` и сохранить `Order` и `OrderItem`.
     После коммита в БД — отправить вебхук на `MOCK_RESTAURANT_WEBHOOK_URL` через `FastAPI.BackgroundTasks` (используй асинхронный `httpx.AsyncClient`).
   - Эндпоинт `GET /orders/{id}` — получить информацию о заказе и его позициях.
   - Эндпоинт `PATCH /orders/{id}/status` — обновить статус заказа (этот эндпоинт будет вызывать Mock-ресторан).
5. Создай точку входа `app/main.py`:
   - Инициализируй экземпляр FastAPI с корректными title, description и version.
   - Подключи все роутеры через `app.include_router(...)`.
   - Настрой глобальные обработчики исключений (Exception Handlers) для возврата аккуратных JSON-ответов.

INPUT / REFERENCES:
- @README.md (для сверки логики CJM и статусов заказов).
- @docs/adr/*
- Не взаимодействуй с Git, пока я не попрошу этого напрямую.
- @app/core/config.py (для MOCK_RESTAURANT_WEBHOOK_URL).

CONSTRAINTS & EXECUTION RULES:
- Строгий скоуп: реализуй исключительно то, что явно указано в блоке TASK.
- Используй строгий синтаксис Pydantic v2 (`ConfigDict(from_attributes=True)` вместо `orm_mode`).
- Изолируй работу с БД в `service.py` (роутеры не должны содержать SQLAlchemy-запросов напрямую).
- Возвращай корректные HTTP статусы: 201 Created при создании, 404 Not Found (если сущность не найдена), 400 Bad Request (если блюдо недоступно).
- Вебхук отправляй асинхронно, чтобы не блокировать ответ клиенту.

WHAT TO AVOID:
- Не используй синхронные HTTP-клиенты (никакого requests, только async httpx).
- Не пиши код для Mock Restaurant API (это микросервис Этапа 4).
- Не пиши заглушки (TODO/pass). Весь код должен быть рабочим.
- Не взаимодействуй с Git, пока я не попрошу этого напрямую.
- Не добавляй массивных ASCII-форматированных комментариев в код. Максимум небольшие пояснения и разделения на логические блоки.

DEFINITION OF DONE:
Задача считается завершенной только тогда, когда:
1. Созданы и заполнены файлы `schemas.py`, `service.py`, `router.py` для модулей restaurants, menu_items, orders.
2. Файл `app/main.py` собирает приложение и импортирует все роутеры.
3. Код полностью типизирован (mypy/Pydantic/typing) и готов к локальному запуску.
4. Отсутствуют циклические импорты между моделями и схемами.

OUTPUT FORMAT:
1. Полный код сгенерированных и измененных файлов с указанием пути (например: `app/orders/router.py`).
2. Команда для локального запуска FastAPI сервера (через `uvicorn`) и URL для проверки Swagger UI.
