# ----------------------------------------------
# 7. v3_infra_log_emitter.py
# ----------------------------------------------
# Periodically emits independent infra logs

import random
from utils.timestamp_utils import current_utc_timestamp

infra_services = ["kubelet", "scheduler", "docker-daemon", "metrics-server", "k8s-master", "rdbms-cluster"]

messages = {
    "kubelet": "All pods running healthy",
    "scheduler": "No pending pods",
    "docker-daemon": "Container restarted successfully",
    "metrics-server": "Cluster CPU usage: 45%",
    "k8s-master": "Control plane is stable",
    "rdbms-cluster": "Replication lag within threshold"
}


def emit_random_infra_logs():
    logs = []
    for service in random.sample(infra_services, 3):
        timestamp = current_utc_timestamp()
        log = f"[{timestamp}] [INFO] [component={service}] {messages[service]}"
        logs.append(log)
    return logs
