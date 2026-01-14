import time
import json
import random

DEVICE_ID = "device-001"

def generate_sensor_data():
    return {
        "device_id": DEVICE_ID,
        "temperature": round(random.uniform(60, 95), 2),
        "timestamp": int(time.time())
    }

if __name__ == "__main__":
    while True:
        data = generate_sensor_data()
        print(json.dumps(data))
        time.sleep(2)
