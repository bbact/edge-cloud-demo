FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY edge edge
COPY cloud cloud
COPY web web

ENV PYTHONUNBUFFERED=1
