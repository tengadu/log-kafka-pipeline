import mysql.connector
from common.config_loader import load_config
from mysql.connector import Error

config = load_config()

def get_connection():
    return mysql.connector.connect(
        host=config['mysql']['host'],
        port=config['mysql']['port'],
        user=config['mysql']['user'],
        password=config['mysql']['password'],
        database=config['mysql']['database']
    )

def save_log_entry(timestamp, log_type, source, raw_message, ai_tag, description, details):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Insert into log_entries
        insert_entry_sql = """
            INSERT INTO log_entries (timestamp, log_type, source, raw_message, ai_tag, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_entry_sql, (timestamp, log_type, source, raw_message, ai_tag, description))
        log_id = cursor.lastrowid

        # Insert into log_entry_details (if any)
        if details:
            insert_detail_sql = """
                INSERT INTO log_entry_details (log_id, field_name, field_value)
                VALUES (%s, %s, %s)
            """
            detail_values = [(log_id, k, v) for k, v in details.items()]
            cursor.executemany(insert_detail_sql, detail_values)

        conn.commit()
        cursor.close()
        conn.close()
        return True

    except Error as e:
        print(f"❌ MySQL Error: {e}")
        return False
