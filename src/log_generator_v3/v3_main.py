# Directory: log-generator/
# Version: v3
# Goal: Template-driven log generation with realistic fatigue/error injection and modular design

# ----------------------------------------------
# 1. v3_main.py
# ----------------------------------------------
# Entry point. Orchestrates flow generation, error injection, and log writing.

import time

from v3_config_manager import load_workflows_and_templates
from v3_flow_manager import FlowManager
from v3_runtime_controller import RuntimeController
from v3_log_writer import LogWriter
from v3_infra_log_emitter import emit_random_infra_logs
from common.config_loader import load_config

config = load_config()
CONFIG_PATH = config['scenarios_v3']['config']
LOG_FILE_PATH = config['scenarios_v3']['log_file']

workflows, templates, reverse_templates = load_workflows_and_templates(CONFIG_PATH)
flow_manager = FlowManager(workflows)
runtime_controller = RuntimeController(templates, reverse_templates)
log_writer = LogWriter(LOG_FILE_PATH)

import random

def interleave_infra_logs(flow_logs: list, infra_logs: list, ratio: float = 0.3) -> list:
    """
    Interleave infra_logs into flow_logs, maintaining the order of flow_logs.
    Inserts infra logs randomly based on the given ratio.
    """
    combined_logs = []
    infra_index = 0

    for log in flow_logs:
        # Randomly insert infra log before this log
        if infra_logs and random.random() < ratio:
            combined_logs.append(infra_logs[infra_index])
            infra_index += 1
            if infra_index >= len(infra_logs):
                infra_index = len(infra_logs) - 1  # Stop when exhausted

        combined_logs.append(log)

    # Optionally add any leftover infra logs at the end
    for i in range(infra_index + 1, len(infra_logs)):
        combined_logs.append(infra_logs[i])

    return combined_logs

while True:
    flow = flow_manager.pick_random_flow()
    logs = runtime_controller.generate_logs_for_flow(flow)
    infra_logs = emit_random_infra_logs()

    combined_logs = interleave_infra_logs(logs, infra_logs)
    # random.shuffle(combined_logs)  # interleave unpredictably

    for log in combined_logs:
        log_writer.write(log)
        # time.sleep(random.uniform(0.1, 0.2))  # optional: jitter

# Sample config loaded as Python dict
# workflow = {
#     "http_logs": {
#         "ecommerce_cart_checkout": {
#             "endpoint": "/cart/checkout",
#             "api_logs": [
#                 {"INFO": ["api-gateway", "product-service", "cart-service", "order-service"]}
#             ],
#             "infra_logs": [
#                 {"INFO": ["metrics-server", "rdbms-cluster", "rdbms-storage", "kubelet", "hpa-controller"]}
#             ]
#         },
#         "ecommerce_payment": {
#             "endpoint": "/payment/confirm",
#             "api_logs": [
#                 {"INFO": ["api-gateway", "order-service", "payment-gateway", "transaction-engine"]}
#             ],
#             "infra_logs": [
#                 {"INFO": ["metrics-server", "rdbms-cluster", "nosql", "docker-daemon", "rdbms-monitor"]}
#             ]
#         }
#     }
# }
#
# def iterate_loop(services, position):
#     # === FORWARD PRINT ===
#     print(">>>>>>>>>>>>>>>> Forward Order: <<<<<<<<<<<<<<<<")
#
#     seq = 0
#     for index, service in enumerate(services):
#         print(service)
#         seq = index
#         if (position == seq):
#             break
#
#     # === REVERSE PRINT (Java-style index loop) ===
#     print("\n>>>>>>>>>>>>>>>> Reverse Order: <<<<<<<<<<<<<<<<")
#     for i in range(seq - 1, -1, -1):
#         print(services[i])
#
# if __name__ == "__main__":
#
#     # Select one flow to demo
#     flows = ["ecommerce_cart_checkout", "ecommerce_payment"]
#     for flow in flows:
#         flow_name = flow
#         api_log_entry = workflow["http_logs"][flow_name]["api_logs"][0]
#         infra_log_entry = workflow["http_logs"][flow_name]["infra_logs"][0]
#         services = api_log_entry["INFO"]
#         services.extend(infra_log_entry["INFO"])
#         iterate_loop(services, 3)
#
