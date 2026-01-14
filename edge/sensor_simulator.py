import time
import json
import random
from kafka import KafkaProducer

DEVICE_ID = "device-001"
KAFKA_TOPIC = "sensor-data"
KAFKA_SERVER = "localhost:9092"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def generate_sensor_data():
    return {
        "device_id": DEVICE_ID,
        "temperature": round(random.uniform(60, 95), 2),
        "timestamp": int(time.time())
    }

if __name__ == "__main__":
    while True:
        data = generate_sensor_data()
        producer.send(KAFKA_TOPIC, data)
        print(f"send to kafka: {data}")
        time.sleep(2)
