# utils/trace_utils.py
import uuid

def generate_trace_id():
    return str(uuid.uuid4())