#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

export KAFKA_HOST_PORT="${KAFKA_HOST_PORT:-19092}"
export KAFKA_BOOTSTRAP="localhost:${KAFKA_HOST_PORT}"
export REDIS_HOST="${REDIS_HOST:-localhost}"
export REDIS_PORT="${REDIS_PORT:-6379}"
export SEND_INTERVAL="${SEND_INTERVAL:-2}"
export ALERT_THRESHOLD="${ALERT_THRESHOLD:-80}"
export PYTHONUNBUFFERED=1

docker compose up -d kafka redis

kafka_health=missing
redis_health=missing
for _ in $(seq 1 30); do
  kafka_health=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' edge-cloud-demo-kafka-1 2>/dev/null || echo missing)
  redis_health=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' edge-cloud-demo-redis-1 2>/dev/null || echo missing)
  if [ "$kafka_health" = "healthy" ] && [ "$redis_health" = "healthy" ]; then
    break
  fi
  sleep 2
done

if [ "$kafka_health" != "healthy" ] || [ "$redis_health" != "healthy" ]; then
  echo "Kafka 或 Redis 没有就绪：kafka=${kafka_health} redis=${redis_health}" >&2
  exit 1
fi

if [ -x /opt/homebrew/bin/python3.14 ]; then
  PYTHON=/opt/homebrew/bin/python3.14
elif command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
else
  echo "需要本机 Python 3" >&2
  exit 1
fi

if [ ! -x .venv/bin/python ]; then
  "$PYTHON" -m venv .venv
fi
.venv/bin/pip install -q -r requirements.txt

mkdir -p .demo

stop_recorded() {
  local file="$1"
  if [ -f "$file" ]; then
    local pid
    pid=$(cat "$file")
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
    rm -f "$file"
  fi
}

stop_recorded .demo/simulator.pid
stop_recorded .demo/processor.pid
stop_recorded .demo/api.pid
sleep 1

if lsof -nP -iTCP:8000 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "8000 端口已被占用，先停掉原来的页面进程后再运行。" >&2
  exit 1
fi

nohup .venv/bin/python -m cloud.processor >.demo/processor.log 2>&1 &
echo $! >.demo/processor.pid
nohup .venv/bin/python edge/sensor_simulator.py >.demo/simulator.log 2>&1 &
echo $! >.demo/simulator.pid
nohup .venv/bin/uvicorn cloud.api:app --host 127.0.0.1 --port 8000 >.demo/api.log 2>&1 &
echo $! >.demo/api.pid
disown

echo "监测页面 http://127.0.0.1:8000"
echo "Kafka localhost:${KAFKA_HOST_PORT}    Redis localhost:${REDIS_PORT}"
