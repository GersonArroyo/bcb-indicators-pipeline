FROM python:3.12-slim

LABEL maintainer="https://github.com/GersonArroyo"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/ ./scripts/

RUN adduser --disabled-password --gecos "" bcb_user
USER bcb_user