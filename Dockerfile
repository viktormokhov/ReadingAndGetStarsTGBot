FROM python:3.12-bullseye

RUN apt-get update && apt-get install -y \
    iputils-ping vim nano curl dnsutils net-tools less procps openssh-server \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src

RUN pip install poetry

COPY pyproject.toml poetry.lock README.md ./
COPY core ./core
COPY api ./api
COPY bot ./bot
COPY config ./config

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
