import json
import os
import time

import redis
from kafka import KafkaConsumer
from kafka.errors import KafkaError

from cloud.rules import judge, next_event, temperature_value

BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "localhost:19092")
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
                auto_offset_reset="earliest",
                enable_auto_commit=True,
            )
            print(f"consuming {TOPIC} from {BOOTSTRAP}")
            return consumer
        except KafkaError as exc:
            print(f"waiting for kafka: {exc}")
            time.sleep(2)


def apply_reading(client, data):
    if temperature_value(data.get("temperature")) is None or "device_id" not in data:
        raise ValueError(f"invalid reading: {data}")
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


def handle_message(client, raw):
    data = json.loads(raw.decode("utf-8"))
    apply_reading(client, data)


def main():
    client = connect_redis()
    consumer = connect_consumer()
    for message in consumer:
        try:
            handle_message(client, message.value)
        except (ValueError, KeyError, TypeError, AttributeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            print(f"skip bad message: {exc}")


if __name__ == "__main__":
    main()
