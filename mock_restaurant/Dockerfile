FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn httpx pydantic-settings

COPY mock_restaurant/ ./mock_restaurant/

EXPOSE 8001

CMD ["uvicorn", "mock_restaurant.main:app", "--host", "0.0.0.0", "--port", "8001"]
