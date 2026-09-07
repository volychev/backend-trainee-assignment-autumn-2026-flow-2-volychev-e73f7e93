CONTEXT:
Проект: MVP платформы доставки "Авито.Кухня".
Стек: Python 3.13, FastAPI, Docker Compose.
Архитектура системы: SOA (Main API + Mock API).
Текущее состояние: Main API полностью реализован и отправляет вебхуки о новых заказах.
Задача этапа: Реализовать второй микросервис — эмулятор ресторана (Mock Restaurant API). Он должен работать как независимое FastAPI-приложение без собственной базы данных (stateless).

ROLE:
Senior Backend Engineer

TASK:
Реализуй микросервис Mock Restaurant API и добавь его в инфраструктуру:
1. Создай файл `mock_restaurant/main.py`.
2. Инициализируй в нем отдельное приложение FastAPI.
3. Настрой получение переменных окружения (можно через `pydantic-settings` в `mock_restaurant/config.py`):
   - `MAIN_API_URL` (базовый URL основного сервиса, куда возвращать статусы).
4. Реализуй эндпоинт `POST /webhook/order`:
   - Принимает JSON от Main API (включающий `order_id` и список позиций).
   - Запускает фоновую задачу (`FastAPI.BackgroundTasks`), которая эмулирует готовку: ждет 5-10 секунд (`asyncio.sleep`), а затем делает асинхронный HTTP PATCH запрос (`httpx.AsyncClient`) на `MAIN_API_URL/orders/{order_id}/status` с телом `{"status": "READY"}`.
   - Сразу возвращает HTTP 200 OK, чтобы не блокировать Main API.
5. Создай `Dockerfile.mock` в корне проекта (на базе `python:3.13-slim`) для сборки этого микросервиса.
6. Обнови корневой `docker-compose.yml`: добавь сервис `mock-restaurant` (собирается из `Dockerfile.mock`, проброс порта 8001:8001, зависит от `main-api`). Добавь в него необходимые переменные окружения.

INPUT / REFERENCES:
- @README.md (для сверки логики CJM и флоу статусов заказа)
- docs/adr/*
- @docker-compose.yml (текущий)

CONSTRAINTS & EXECUTION RULES:
- Строгий скоуп: реализуй исключительно то, что явно указано в блоке TASK.
- Сервис должен быть stateless: не подключай его к PostgreSQL, все данные он получает из вебхука.
- Используй асинхронный HTTP-клиент (`httpx.AsyncClient`) для обратного вызова в Main API.

WHAT TO AVOID:
- Не меняй код Main API на этом шаге.
- Не используй синхронный `time.sleep()`, только `asyncio.sleep()`.
- Не пиши заглушки (TODO/pass). Весь код должен быть рабочим.
- Не взаимодействуй с Git, пока я не попрошу этого напрямую.
- Не добавляй массивных ASCII-форматированных комментариев в код. Максимум небольшие пояснения.

DEFINITION OF DONE:
Задача считается завершенной только тогда, когда:
1. Создан рабочий код `mock_restaurant/main.py`.
2. Создан `Dockerfile.mock`.
3. `docker-compose.yml` обновлен и содержит все три сервиса (`postgres`, `main-api`, `mock-restaurant`).
4. При вызове `docker compose up` поднимаются все сервисы, и Mock API успешно слушает порт 8001.

OUTPUT FORMAT:
1. Полный код файлов `mock_restaurant/main.py`, `mock_restaurant/config.py` и `Dockerfile.mock`.
2. Обновленный код `docker-compose.yml`.
3. Команда терминала для полного перезапуска проекта через Docker Compose.
