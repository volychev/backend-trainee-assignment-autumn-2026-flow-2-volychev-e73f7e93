FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --only main --no-root

COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY app/ ./app/

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
