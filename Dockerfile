FROM python:3.12-slim

LABEL maintainer="Mona"

ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    pip install -r /tmp/requirements.dev.txt

RUN mkdir /app

WORKDIR /app

COPY ./app /app

RUN useradd -m appuser

USER appuser