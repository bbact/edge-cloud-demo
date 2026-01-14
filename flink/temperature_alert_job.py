ffrom pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource
from pyflink.common.serialization import SimpleStringSchema
import json
import redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379

def handle_abnormal(value):
    data = json.loads(value)
    if data["temperature"] > 80:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        key = f"alert:{data['device_id']}"
        r.set(key, json.dumps(data))
        print(f"ALERT saved to redis: {data}")

env = StreamExecutionEnvironment.get_execution_environment()

source = KafkaSource.builder() \
    .set_bootstrap_servers("localhost:9092") \
    .set_topics("sensor-data") \
    .set_group_id("flink-group") \
    .set_value_only_deserializer(SimpleStringSchema()) \
    .build()

stream = env.from_source(source, watermark_strategy=None, source_name="kafka-source")

stream.map(handle_abnormal)

env.execute("Temperature Alert with Redis")
