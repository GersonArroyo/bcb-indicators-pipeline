FROM python:3.9-slim

LABEL maintainer="https://github.com/GersonArroyo"

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN adduser --disabled-password --gecos "" appuser

USER appuser

EXPOSE 9898

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \

CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:9898/').read()" || exit 1

CMD ["hypercorn", "main:app", "--bind", "0.0.0.0:9898"]