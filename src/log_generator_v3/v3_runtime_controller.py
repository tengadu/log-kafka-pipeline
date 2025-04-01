# ----------------------------------------------
# 4. v3_runtime_controller.py
# ----------------------------------------------
# Handles log_type overrides, back-propagation on error, dynamic substitutions.

import random
from utils.trace_utils import generate_trace_id
from v3_log_template_manager import generate_log_from_template
from utils.random_utils import get_random_ip
from utils.random_utils import get_random_user_id
from utils.random_utils import get_random_product_id




class RuntimeController:
    def __init__(self, templates, reverse_templates):
        self.templates = templates
        self.reverse_templates = reverse_templates

    def generate_logs_for_flow(self, flow):
        trace_id = generate_trace_id()
        ip_addr = get_random_ip()
        user_id = get_random_user_id()
        product_id = get_random_product_id()
        api_endpoint = flow['endpoint']

        logs = []
        services = self._flatten_services(flow['api_logs'], 'INFO')

        # Decide flow behavior
        severity_level = random.choices([1, 2, 3], weights=[5, 3, 2])[0]
        simulate_error = severity_level == 3
        simulate_warn = severity_level == 2
        error_position = random.randint(1, len(services) - 1) if simulate_error else None

        return self.add_service_logs(services, error_position, simulate_error, simulate_warn,
                     trace_id, ip_addr, user_id, api_endpoint, product_id)

    def add_service_logs(self, services, error_position, simulate_error, simulate_warn,
                         trace_id, ip_addr, user_id, api_endpoint, product_id):

        logs = []
        log_type = 'INFO'
        break_position = -1

        # === FORWARD LOGS ===
        for index, service in enumerate(services):
            if simulate_error and index == error_position:
                log_type = 'ERROR'
            elif simulate_warn:
                log_type = 'WARN'
            else:
                log_type = 'INFO'

            logs.append(generate_log_from_template(
                service, api_endpoint, log_type, self.templates,
                trace_id=trace_id, ip_address=ip_addr, user_id=user_id, product_id=product_id
            ))

            if simulate_error and index == error_position:
                break_position = index  # ✅ always capture current forward index
                # print(f"[DEBUG] ERROR occurred at position={error_position}, last_index={break_position}, total={len(services)}, trace_id={trace_id}")
                break  # stop forward on ERROR

        # === REVERSE LOGS ===
        if break_position >= 1:  # ✅ fix: allow reverse if at least one service before break
            # print(f"[DEBUG] IN REVERSE LOGS: ERROR position={error_position}, last_index={break_position}, total={len(services)}, trace_id={trace_id}")
            for i in range(break_position - 1, -1, -1):
                service = services[i]
                # print(f"[DEBUG] PRINTING REVERSE LOGS: Index: {i} ERROR position={error_position}, last_index={break_position}, total={len(services)}, trace_id={trace_id}; service: {service}")
                logs.append(generate_log_from_template(
                    service, api_endpoint, log_type, self.reverse_templates,
                    trace_id=trace_id, ip_address=ip_addr, user_id=user_id, product_id=product_id
                ))

        return logs

    def _flatten_services(self, api_logs, log_type):
        for group in api_logs:
            if log_type in group:
                return group[log_type]
        return []

    def _decide_flow_type(self):
        return random.choices(
            ['INFO', 'WARN', 'ERROR'],
            weights=[2, 4, 4],
            k=1
        )[0]