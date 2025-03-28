import logging
from datetime import datetime
from common.config_loader import load_config
from common.kafka_client import create_kafka_consumer
from common.db.db_orm import insert_log_batch
from common.ai.ai_service import perform_ai_analysis

keywords = ["error", "warn", "failed", "failure", "exception", "critical"]

def extract_log_metadata(log_line):
    """Parses a single ai line to extract timestamp and message."""
    try:
        if log_line.startswith("["):
            timestamp_str = log_line.split("]")[0].strip("[]")
            ts = datetime.strptime(timestamp_str, "%a %b %d %H:%M:%S %Y")
            rest = "]".join(log_line.split("]")[1:]).strip()
            return ts, rest
    except Exception as e:
        logging.warning(f"Failed to extract timestamp from ai: {log_line}")
    return datetime.utcnow(), log_line  # fallback to current time

# def run_consumer():
#     logging.basicConfig(level=logging.INFO)
#     logger = logging.getLogger("consumer")
#
#     config = load_config()
#     source_name = config['ai'].get('source_name', 'apache')
#     consumer = create_kafka_consumer()
#
#     logger.info("🔄 Kafka Consumer started listening...")
#
#     log_buffer = []  # <-- Buffer incoming logs
#
#     for msg in consumer:
#         log_line = msg.value.get("log")
#         if not log_line:
#             continue
#
#         timestamp, raw_message = extract_log_metadata(log_line)
#         log_line_lower = raw_message.lower()
#
#         if any(kw in log_line_lower for kw in keywords):
#             timestamp, raw_message = extract_log_metadata(log_line)
#             log_buffer.append((timestamp, raw_message))
#         else:
#             logger.debug(f"🚫 Skipped the non-relevant ai: {log_line}")
#
#         if len(log_buffer) >= 5:
#             logger.info(f"🧠 Sending batch of {len(log_buffer)} logs to OpenAI...")
#             ai_results = perform_ai_analysis([line for _, line in log_buffer])
#             logger.info(f"🚫 Skipped the non-relevant ai: {log_line}")
#             insert_log_batch(ai_results);
#
#             log_entries_batch = [];
#             for (timestamp, raw_message), ai_result in zip(log_buffer, ai_results):
#             # for ai_result in ai_results:
#                 if ai_result['log_type'] in ["ERROR", "WARN"]:
#                     log_entries_batch.append({
#                         "timestamp": timestamp,
#                         "log_type": ai_result['log_type'],
#                         "source": source_name,
#                         "raw_message": raw_message,
#                         "ai_tag": ai_result['ai_tag'],
#                         "description": ai_result['description'],
#                         "details": ai_result['details']
#                     })
#                     logger.info(f"✅ Logged {ai_result['log_type']} to DB: {raw_message}")
#                 else:
#                     logger.debug(f"ℹ️ Skipped non-critical ai: {raw_message}")
#
#             if log_entries_batch:
#                 logger.info(f"Persisting {len(log_entries_batch)} log entries to the database")
#                 insert_log_batch(log_entries_batch)
#                 logger.info(f"✅ Persisted {len(log_entries_batch)} log entries to the database")
#             else:
#                 logger.info(f"🚫 No logs to persist to DB")
#
#             log_buffer.clear()  # Clear after processing


def run_consumer():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("consumer")

    config = load_config()
    source_name = config['ai'].get('source_name', 'apache')
    consumer = create_kafka_consumer()

    logger.info("🔄 Kafka Consumer started listening...")

    log_buffer = []

    for msg in consumer:
        log_line = msg.value.get("log")
        if not log_line:
            continue

        # Extract once
        timestamp, raw_message = extract_log_metadata(log_line)
        log_line_lower = raw_message.lower()

        if any(kw in log_line_lower for kw in keywords):
            log_buffer.append((timestamp, raw_message))
        else:
            logger.debug(f"🚫 Skipped the non-relevant ai: {log_line}")

        if len(log_buffer) >= 5:
            logger.info(f"🧠 Sending batch of {len(log_buffer)} logs to AI model...")

            ai_results = perform_ai_analysis([line for _, line in log_buffer])

            if not ai_results or len(ai_results) != len(log_buffer):
                logger.warning("⚠️ Skipping this batch due to AI failure or result mismatch.")
                log_buffer.clear()
                continue

            log_entries_batch = []

            for (timestamp, raw_message), ai_result in zip(log_buffer, ai_results):
                if ai_result.get("log_type") in ["ERROR", "WARN"]:
                    log_entries_batch.append({
                        "timestamp": timestamp,
                        "log_type": ai_result.get('log_type'),
                        "source": source_name,
                        "raw_message": raw_message,
                        "ai_tag": ai_result.get('ai_tag'),
                        "description": ai_result.get('description'),
                        "details": ai_result.get('details') or {}
                    })
                    logger.info(f"✅ Logged {ai_result['log_type']} to DB: {raw_message}")
                else:
                    logger.debug(f"ℹ️ Skipped non-critical ai: {raw_message}")

            if log_entries_batch:
                logger.info(f"💾 Persisting {len(log_entries_batch)} log entries to the database...")
                # logger.info(f"💾 Records: {log_entries_batch} ")
                success = insert_log_batch(log_entries_batch)
                if success:
                    logger.info(f"✅ Successfully persisted {len(log_entries_batch)} log entries.")
                else:
                    logger.error("❌ DB insert failed for current batch.")
            else:
                logger.info("🚫 No critical logs to persist in this batch.")

            log_buffer.clear()

if __name__ == "__main__":
    run_consumer()
