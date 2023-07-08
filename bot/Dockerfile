FROM python:3.11.1-slim

WORKDIR /app

COPY . /app/

COPY pyproject.toml poetry.lock ./

RUN pip3 install poetry

RUN poetry config virtualenvs.create false

RUN poetry install

CMD python main.py
