from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource
from pyflink.common.serialization import SimpleStringSchema
import json

def is_abnormal(value):
    data = json.loads(value)
    return data["temperature"] > 80

env = StreamExecutionEnvironment.get_execution_environment()

source = KafkaSource.builder() \
    .set_bootstrap_servers("localhost:9092") \
    .set_topics("sensor-data") \
    .set_group_id("flink-group") \
    .set_value_only_deserializer(SimpleStringSchema()) \
    .build()

stream = env.from_source(source, watermark_strategy=None, source_name="kafka-source")

abnormal_stream = stream.filter(is_abnormal)

abnormal_stream.print()

env.execute("Temperature Alert Job")
