FROM python:3.10.5-slim

ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /usr/backend

COPY ./requirements.txt /usr/backend/requirements.txt

RUN apt-get update && apt-get install -y gcc libpq-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /usr/backend/