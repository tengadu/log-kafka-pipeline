# utils/random_utils.py
import random

import random
import string
from uuid import uuid4
from datetime import datetime


def get_random_dynamic_values(end_point, service):
    return {
        "ip_address": get_random_ip(),
        "user_id": get_random_user_id(),
        "latency": str(get_random_latency()),
        "error_message": get_random_error_message(),
        "disk": get_random_disk(),
        "pod": get_random_pod(service),
        "pod_old": get_random_pod(service),
        "shard_id": get_random_shard_id(),
        "replica_id": get_random_replica_id(),
        "resync_node": get_random_replica_id(),
        "cache_hit_ratio": str(get_random_cache_hit_ratio()),
        "qps": str(get_random_qps()),
        "api_endpoint": end_point,
        "timestamp": datetime.utcnow().isoformat(),
        "trace_id": str(uuid4()),
        "route_id": uuid4().hex[:8],
        "amount": random.randint(1000, 99999),
        "product_id": f"P{random.randint(100000000,999999999)}",         # ✅ Add this
        "order_id": f"O{random.randint(1000000000,9999999999)}"          # ✅ Often used
    }


def choose_random_weighted(items):
    if isinstance(items, dict):
        choices, weights = zip(*items.items())
        return random.choices(choices, weights=weights, k=1)[0]
    return random.choice(items)


def get_random_error_message():
    error_messages = [
        "Timeout while connecting to downstream service",
        "Database write failed due to disk saturation",
        "NullPointerException in OrderProcessor",
        "Service Unavailable - circuit breaker open",
        "User authorization failed due to token expiry",
        "Connection reset by peer",
        "502 Bad Gateway",
        "503 Service Unavailable",
        "Insufficient permissions to perform action",
        "Write conflict detected, retry limit exceeded"
    ]
    return random.choice(error_messages)


def maybe(probability):
    return random.random() < probability


def get_random_latency(min_val=100, max_val=5000):
    return random.randint(min_val, max_val)


def get_random_user_id():
    return random.randint(100000000000, 999999999999)


def get_random_ip():
    return '.'.join(str(random.randint(0, 255)) for _ in range(4))


# def get_random_endpoint():
#     return random.choice(["/search", "/product/details", "/cart/add", "/checkout", "/payment", "/order/status"])


def get_random_error():
    return random.choice(["DB_TIMEOUT", "AUTH_FAILED", "SERVICE_UNAVAILABLE", "RUNTIME_EXCEPTION"])


def get_random_pod(service_name: str) -> str:
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{service_name}-{suffix}"

# def get_random_pod():
#     return random.choice(["api-gateway-abc123", "product-service-xyz789", "checkout-service-lmn456"])


def get_random_disk():
    return random.choice(["/mnt/data1", "/data/db", "/mnt/logs"])  # For realism


def get_random_qps():
    return random.randint(400, 1000)


def get_random_cache_hit_ratio():
    return random.randint(85, 99)


def get_random_replica_lag():
    return random.randint(500, 3000)


def get_random_disk_latency():
    return random.randint(200, 1000)


def get_random_product_id():
    return random.randint(100000000,999999999)


def get_random_replica_id():
    return random.choice(["1", "2", "3"])


def get_random_shard_id():
    return random.choice(["0", "1", "2"])


def get_random_node():
    return random.choice(["node-1", "node-2", "node-5"])


def get_random_resync_node():
    return random.choice(["mongo-1", "mongo-2", "mongo-3"])
