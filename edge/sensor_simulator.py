import json
import os
import random
import time

from kafka import KafkaProducer
from kafka.errors import KafkaError

BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "localhost:19092")
TOPIC = os.environ.get("KAFKA_TOPIC", "sensor-data")
INTERVAL = float(os.environ.get("SEND_INTERVAL", "2"))

DEVICES = [
    {"device_id": "device-001", "name": "一号车间传感器", "base": 64, "spread": 4, "spike_p": 0.08},
    {"device_id": "device-002", "name": "二号车间传感器", "base": 71, "spread": 3, "spike_p": 0.15},
    {"device_id": "device-003", "name": "老化测试台", "base": 75, "spread": 3, "spike_p": 0.45},
]


def reading(device):
    if random.random() < device["spike_p"]:
        temperature = round(random.uniform(82, 96), 2)
    else:
        low = device["base"] - device["spread"]
        high = min(device["base"] + device["spread"], 79.5)
        temperature = round(random.uniform(low, high), 2)
    return {
        "device_id": device["device_id"],
        "name": device["name"],
        "temperature": temperature,
        "humidity": round(random.uniform(35, 70), 1),
        "timestamp": int(time.time()),
    }


def connect():
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=BOOTSTRAP,
                value_serializer=lambda value: json.dumps(value, ensure_ascii=False).encode("utf-8"),
                acks="all",
                retries=3,
            )
            print(f"kafka ready at {BOOTSTRAP}")
            return producer
        except KafkaError as exc:
            print(f"waiting for kafka: {exc}")
            time.sleep(2)


def main():
    producer = connect()
    while True:
        for device in DEVICES:
            payload = reading(device)
            try:
                producer.send(TOPIC, payload).get(timeout=10)
            except KafkaError as exc:
                print(f"send failed, reconnecting: {exc}")
                producer.close()
                producer = connect()
                continue
            print(f"send {payload['device_id']} {payload['temperature']}°C")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
