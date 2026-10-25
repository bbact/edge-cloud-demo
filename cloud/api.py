import json
import os
import time
from pathlib import Path

import redis
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from cloud.rules import display_status

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
SEND_INTERVAL = float(os.environ.get("SEND_INTERVAL", "2"))
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
    now = time.time()
    items = []
    for key in store.scan_iter("device:*"):
        raw = store.get(key)
        if raw:
            item = json.loads(raw)
            item["status"] = display_status(item, now, SEND_INTERVAL)
            items.append(item)
    items.sort(key=lambda item: item["device_id"])
    return items


@app.get("/api/alerts")
def alerts():
    rows = client().lrange("alerts", 0, 49)
    return [json.loads(row) for row in rows]


app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
