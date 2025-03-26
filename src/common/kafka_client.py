import json
from kafka import KafkaProducer, KafkaConsumer
from common.config_loader import load_config

# Load configuration once at module level
config = load_config()

KAFKA_BOOTSTRAP_SERVERS = config['kafka']['bootstrap_servers']
KAFKA_TOPIC = config['kafka']['topic']
KAFKA_GROUP_ID = config['kafka'].get('group_id', 'default-consumer-group')

def create_kafka_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

def create_kafka_consumer():
    return KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )