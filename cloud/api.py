import json
import os
from pathlib import Path

import redis
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
WEB_DIR = Path(__file__).resolve().parent.parent / "web"

app = FastAPI(title="边缘到云端实时监测")


def client():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@app.get("/api/health")
def health():
    client().ping()
    return {"ok": True}


@app.get("/api/devices")
def devices():
    store = client()
    items = []
    for key in store.scan_iter("device:*"):
        raw = store.get(key)
        if raw:
            items.append(json.loads(raw))
    items.sort(key=lambda item: item["device_id"])
    return items


@app.get("/api/alerts")
def alerts():
    rows = client().lrange("alerts", 0, 49)
    return [json.loads(row) for row in rows]


app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
