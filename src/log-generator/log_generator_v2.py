import random
import uuid
import yaml
import os
import time
import json
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from common.config_loader import load_config

config = load_config()
CONFIG_PATH = config['scenarios_v2']['config']
LOG_FILE_PATH = config['scenarios_v2']['log_file']

service_categories = {
    "api": ["api-gateway", "user-service", "kyc-service", "confirmation-service", "pin-validation-service", "upi-router", "payment-service", "transaction-engine"],
    "infra": ["disk", "storage-engine", "db-node"],
    "network": ["service-router"],
    "security": ["security-engine", "auth-service"],
    "kafka": ["kafka-broker", "kafka-consumer"]
}

# Add this somewhere at the top or in config
API_ENDPOINTS = [
    "/upi/payment",
    "/upi/balance",
    "/upi/validate",
    "/user/verify",
    "/transaction/history",
    "/auth/token"
]

# ------------------------ Config Loader ------------------------
def load_scenario_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


# ------------------------ Dynamic Data Generator ------------------------
def generate_trace_id():
    return str(uuid.uuid4())


def generate_user_id():
    return str(random.randint(1000, 9999))


def generate_ip():
    return f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"


def generate_latency():
    return str(random.randint(100, 1000))  # in ms


def generate_lag():
    return str(random.randint(500, 2000))  # in ms


def generate_disk_quota():
    return f"{random.randint(65, 99)}%"


# Dynamic topic inference (optional override from message)
def infer_topic(service):
    if "kafka" in service:
        return "topic-upi-events"
    if "auth" in service:
        return "topic-auth-events"
    if "security" in service:
        return "topic-security"
    return "topic-generic"


def get_log_level(msg_template):
    error_keywords = ["error", "503", "failure", "unavailable", "denied", "unauthorized"]
    warn_keywords = ["critical", "slow", "lag", "quota", "retry", "degraded"]

    msg_lower = msg_template.lower()
    if any(word in msg_lower for word in error_keywords):
        level = "ERROR"
    elif any(word in msg_lower for word in warn_keywords):
        level = "WARN"
    else:
        level = "INFO"

    return level


def get_service_category(service):
    if service in ["api-gateway", "auth-service", "user-service", "kyc-service",
                   "confirmation-service", "pin-validation-service", "upi-router",
                   "payment-service", "transaction-engine"]:
        return "api"
    elif service in ["storage-engine", "db-node", "disk"]:
        return "infra"
    elif service in ["kafka-broker", "kafka-consumer"]:
        return "kafka"
    elif service in ["security-engine", "firewall"]:
        return "security"
    elif service in ["service-router"]:
        return "network"
    return "generic"

# ------------------------ Log Generator ------------------------
class LogSimulator:

    def __init__(self, config):
        self.config = config
        self.dynamic_fields = config.get("dynamic_fields", {})
        self.manual_mode = config.get("manual_mode", {}).get("enabled", False)
        self.manual_scenarios = config.get("manual_mode", {}).get("scenarios_to_run", [])
        self.scenarios = [s for s in config["scenarios"] if s.get("enabled", True)]

    def pick_scenario(self):
        if self.manual_mode:
            return [s for s in self.scenarios if s["id"] in self.manual_scenarios]
        choices = [s for s in self.scenarios]
        weights = [s.get("weight", 1) for s in choices]
        return [random.choices(choices, weights=weights, k=1)[0]]

    def substitute(self, text, values):
        for key, val in values.items():
            text = text.replace(f"{{{key}}}", val)
        return text

    def generate_flow_logs(self, flow, log_level, trace_id, dynamic_values, correlated_services):
        logs = []
        timestamp = datetime.now()

        for service in flow:
            if service in correlated_services:
                continue  # Skip, since correlated log already exists
            level = log_level if isinstance(log_level, str) else random.choice(log_level)
            msg = f"Generic log from {service}"
            log = self.format_log(timestamp, level, service, trace_id, msg, False)
            logs.append(log)
            timestamp += timedelta(seconds=1)

        return logs

    def generate_correlated_logs(self, correlated_logs, trace_id, dynamic_values):
        logs = []
        correlated_services = set()
        timestamp = datetime.now()

        for entry in correlated_logs:
            for service, msg_template in entry.items():
                category = get_service_category(service)

                # Enhance message template if it's too generic or needs category styling
                if "Generic log" in msg_template or msg_template.strip() == "":
                    if category == "infra":
                        msg_template = "infraLog: service={service}, diskQuota={disk_quota}, lag={lag_ms}, latency={latency_ms}"
                    elif category == "kafka":
                        msg_template = "kafkaLog: service={service}, topic=topic-upi-events, lag={lag_ms}ms"
                    elif category == "security":
                        msg_template = "SECURITY ALERT: suspicious activity from IP {ip_address}"
                    elif category == "network":
                        msg_template = "networkEvent: latency to endpoint {ip_address} is {latency_ms}ms"
                    else:  # fallback
                        msg_template = "Generic log from {service}"

                # Fill in placeholders
                dynamic_values["service"] = service
                message = self.substitute(msg_template, dynamic_values)
                level = get_log_level(message)

                log = self.format_log(timestamp, level, service, trace_id, message, True)
                logs.append(log)
                correlated_services.add(service)
                timestamp += timedelta(milliseconds=random.randint(100, 800))

        return logs, correlated_services

    def get_service_category(self, service):
        for category, services in service_categories.items():
            if service in services:
                return category
        return "generic"



    def format_log(self, timestamp, level, service, trace_id, message, is_correlated=False):
        category = self.get_service_category(service)
        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Millisecond precision
        iso_timestamp = timestamp.isoformat(timespec='milliseconds') + "Z"

        if category == "api":
            return f"[{iso_timestamp}] [{level}] [trace_id={trace_id}] [service={service}] {message}"

        elif category == "infra":
            return f"[{iso_timestamp}] [{level}] [disk={service}] :: {message}"

        elif category == "database":
            return f"[{iso_timestamp}] [{level}] [db={service}] - {message}"

        elif category == "network":
            return f"[{timestamp_str}] [{level}] [device={service}] ::: {message}"

        elif category == "security":
            return f"[{timestamp_str}] [{level}] [module={service}] >>> {message}"


        elif category == "kafka":
            # Infer topic name from service or message
            topic_name = infer_topic(service)

            log_entry = {
                "ts": timestamp_str,
                "component": service,
                "level": level,
                "message": message
            }

            if topic_name:
                log_entry["topic"] = topic_name

            if self.dynamic_fields.get("enable_trace_id"):
                log_entry["trace_id"] = trace_id

            return json.dumps(log_entry)

        else:  # fallback
            return f"[{iso_timestamp}] [{level}] [component={service}] {message}"

    def simulate(self):
        selected_scenarios = self.pick_scenario()
        api_endpoint = random.choice(API_ENDPOINTS)
        all_logs = []

        for scenario in selected_scenarios:
            trace_id = generate_trace_id() if self.dynamic_fields.get("enable_trace_id") else "static-trace"
            user_id = generate_user_id() if self.dynamic_fields.get("enable_user_id") else "0000"
            ip_address = generate_ip() if self.dynamic_fields.get("enable_ip") else "127.0.0.1"
            latency_ms = generate_latency() if self.dynamic_fields.get("enable_latency") else "0"
            lag_ms = generate_lag() if self.dynamic_fields.get("enable_lag") else "0"
            disk_quota = generate_disk_quota() if self.dynamic_fields.get("enable_disk_quota") else "0%"

            dynamic_values = {
                "trace_id": trace_id,
                "user_id": user_id,
                "ip_address": ip_address,
                "latency_ms": latency_ms,
                "lag_ms": lag_ms,
                "disk_quota": disk_quota,
                "api_endpoint": api_endpoint
            }

            correlated = scenario.get("correlated_logs", [])
            correlated_logs, correlated_services = self.generate_correlated_logs(correlated, trace_id, dynamic_values)
            flow_logs = self.generate_flow_logs(scenario["flow"], scenario["log_level"], trace_id, dynamic_values, correlated_services)

            all_logs.extend(flow_logs + correlated_logs)

        return all_logs

    def write_logs_to_file(self, logs):
        os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
        with open(LOG_FILE_PATH, "a") as f:
            for log in logs:
                f.write(log + "\n")


# ------------------------ Runner ------------------------
if __name__ == "__main__":
    config = load_scenario_config()
    simulator = LogSimulator(config)

    manual_mode = config.get("manual_mode", {}).get("enabled", False)
    if manual_mode:
        for log in simulator.simulate():
            print(log)
    else:
        while True:
            simulator.write_logs_to_file(simulator.simulate())
            time.sleep(1)
