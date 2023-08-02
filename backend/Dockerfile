FROM python:3.11.1-slim AS builder

COPY pyproject.toml poetry.lock ./

RUN pip3 install --no-cache-dir poetry==1.3.2 \
    && poetry export --without-hashes --without dev \
    -f requirements.txt -o requirements.txt

FROM python:3.11.1-slim

WORKDIR /app

COPY --from=builder requirements.txt ./

RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . /app/
