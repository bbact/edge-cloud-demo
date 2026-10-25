import json
import os
import time

import redis
from kafka import KafkaConsumer
from kafka.errors import KafkaError

from cloud.rules import judge, next_event

BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "localhost:9092")
TOPIC = os.environ.get("KAFKA_TOPIC", "sensor-data")
GROUP = os.environ.get("KAFKA_GROUP", "alert-processor")
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
ALERT_LIMIT = 50


def connect_redis():
    while True:
        client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        try:
            client.ping()
            print(f"redis ready at {REDIS_HOST}:{REDIS_PORT}")
            return client
        except redis.RedisError as exc:
            print(f"waiting for redis: {exc}")
            time.sleep(2)


def connect_consumer():
    while True:
        try:
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=BOOTSTRAP,
                group_id=GROUP,
                auto_offset_reset="latest",
                enable_auto_commit=True,
                value_deserializer=lambda raw: json.loads(raw.decode("utf-8")),
            )
            print(f"consuming {TOPIC} from {BOOTSTRAP}")
            return consumer
        except KafkaError as exc:
            print(f"waiting for kafka: {exc}")
            time.sleep(2)


def apply_reading(client, data):
    device_id = data["device_id"]
    key = f"device:{device_id}"
    previous = client.get(key)
    previous_status = json.loads(previous)["status"] if previous else None
    status = judge(data["temperature"])
    record = {**data, "status": status}
    client.set(key, json.dumps(record, ensure_ascii=False))

    event = next_event(previous_status, data["temperature"])
    if event is None:
        return record

    alert = {**record, "event": event["type"]}
    client.lpush("alerts", json.dumps(alert, ensure_ascii=False))
    client.ltrim("alerts", 0, ALERT_LIMIT - 1)
    if event["type"] == "raise":
        client.set(f"alert:{device_id}", json.dumps(record, ensure_ascii=False))
        print(f"ALERT {device_id} {data['temperature']}°C")
    else:
        client.delete(f"alert:{device_id}")
        print(f"CLEAR {device_id} {data['temperature']}°C")
    return record


def main():
    client = connect_redis()
    consumer = connect_consumer()
    for message in consumer:
        apply_reading(client, message.value)


if __name__ == "__main__":
    main()
