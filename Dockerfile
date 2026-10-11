FROM python:3.12-slim

LABEL maintainer="https://github.com/GersonArroyo"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/ ./scripts/
COPY config_bcb/ ./config_bcb/

RUN adduser --disabled-password --gecos "" bcb_user

RUN mkdir -p /data/raw/bcb \
    && chown -R bcb_user:bcb_user /data

USER bcb_user
