FROM python:3.12-slim

RUN pip install poetry

WORKDIR /

COPY pyproject.toml poetry.lock README.md ./
COPY core ./core
COPY api ./api
COPY bot ./bot
COPY config ./config

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
