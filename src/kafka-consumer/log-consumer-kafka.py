import logging
from datetime import datetime
from common.config_loader import load_config
from common.kafka_client import create_kafka_consumer
from common.db.db_orm import persist_log_entries
from common.log.log_analyzer_apache import perform_openai_analysis

# Simulated AI response generator (until LangChain is integrated)

def extract_log_metadata(log_line):
    """Parses a single log line to extract timestamp and message."""
    try:
        if log_line.startswith("["):
            timestamp_str = log_line.split("]")[0].strip("[]")
            ts = datetime.strptime(timestamp_str, "%a %b %d %H:%M:%S %Y")
            rest = "]".join(log_line.split("]")[1:]).strip()
            return ts, rest
    except Exception as e:
        logging.warning(f"Failed to extract timestamp from log: {log_line}")
    return datetime.utcnow(), log_line  # fallback to current time

def run_consumer():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("consumer")

    config = load_config()
    source_name = config['log'].get('source_name', 'apache')
    consumer = create_kafka_consumer()

    logger.info("🔄 Kafka Consumer started listening...")

    log_buffer = []  # <-- Buffer incoming logs

    for msg in consumer:
        log_line = msg.value.get("log")
        if not log_line:
            continue

        timestamp, raw_message = extract_log_metadata(log_line)
        log_buffer.append((timestamp, raw_message))

        if len(log_buffer) >= 20:
            logger.info(f"🧠 Sending batch of {len(log_buffer)} logs to OpenAI...")
            ai_results = perform_openai_analysis([line for _, line in log_buffer])

            for (ts, raw), ai_result in zip(log_buffer, ai_results):
                if ai_result['log_type'] in ["ERROR", "WARN"]:
                    persist_log_entries(
                        timestamp=ts,
                        log_type=ai_result['log_type'],
                        source=source_name,
                        raw_message=raw,
                        ai_tag=ai_result['ai_tag'],
                        description=ai_result['description'],
                        details=ai_result['details']
                    )
                    logger.info(f"✅ Logged {ai_result['log_type']} to DB: {raw}")
                else:
                    logger.debug(f"ℹ️ Skipped non-critical log: {raw}")

            log_buffer.clear()  # Clear after processing

if __name__ == "__main__":
    run_consumer()
