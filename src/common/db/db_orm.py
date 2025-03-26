from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.config_loader import load_config
from common.db.models import Base, LogEntry, LogEntryDetail

config = load_config()
DATABASE_URL = f"mysql+pymysql://{config['mysql']['user']}:{config['mysql']['password']}@" \
               f"{config['mysql']['host']}:{config['mysql']['port']}/{config['mysql']['database']}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# One-time init to create tables (if not yet created)
def init_db():
    Base.metadata.create_all(bind=engine)

def persist_log_entries(timestamp, log_type, source, raw_message, ai_tag, description, details):
    session = SessionLocal()
    try:
        entry = LogEntry(
            timestamp=timestamp,
            log_type=log_type,
            source=source,
            raw_message=raw_message,
            ai_tag=ai_tag,
            description=description
        )
        session.add(entry)
        session.flush()  # Get entry.log_id

        for key, value in (details or {}).items():
            session.add(LogEntryDetail(
                log_id=entry.log_id,
                field_name=key,
                field_value=value
            ))

        session.commit()
        return True
    except Exception as e:
        print(f"❌ SQLAlchemy Insert Error: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def insert_log_batch(log_entries_batch):
    """
    log_entries_batch: List of dicts with keys:
    timestamp, log_type, source, raw_message, ai_tag, description, details
    """
    session = SessionLocal()
    try:
        log_entry_objs = []
        log_detail_objs = []

        for entry in log_entries_batch:
            log_entry = LogEntry(
                timestamp=entry["timestamp"],
                log_type=entry["log_type"],
                source=entry["source"],
                raw_message=entry["raw_message"],
                ai_tag=entry["ai_tag"],
                description=entry["description"]
            )
            log_entry_objs.append(log_entry)

        session.add_all(log_entry_objs)
        session.flush()  # Get auto-generated log_ids

        for log_entry, entry in zip(log_entry_objs, log_entries_batch):
            for k, v in (entry.get("details") or {}).items():
                log_detail_objs.append(
                    LogEntryDetail(
                        log_id=log_entry.log_id,
                        field_name=k,
                        field_value=v
                    )
                )

        session.add_all(log_detail_objs)
        session.commit()
        return True

    except Exception as e:
        print(f"❌ Batch insert failed: {e}")
        session.rollback()
        return False
    finally:
        session.close()