import os
import time
import logging
from common.config_loader import load_config
from common.kafka_client import create_kafka_producer

# Load config
logger = logging.getLogger("producer")
config = load_config()
log_file_path = config['log']['file_path']
topic = config['kafka']['topic']

producer = create_kafka_producer()


def read_log_file(file_path):
    """Generator that reads a log file line by line."""
    with open(file_path, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            yield line.strip()


def send_to_kafka(line):
    """Send a single log line to Kafka."""
    message = {"log": line}
    try:
        producer.send(topic, value=message)
        logger.info(f"✅ Sent to Kafka: {message}")
    except Exception as e:
        logger.error(f"❌ Failed to send log: {e}")


def run_producer():
    """Main producer loop."""
    logger.info("🚀 Log Producer started...")
    if not os.path.exists(log_file_path):
        logger.error(f"❌ Log file not found: {log_file_path}")
        return

    for line in read_log_file(log_file_path):
        send_to_kafka(line)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_producer()
