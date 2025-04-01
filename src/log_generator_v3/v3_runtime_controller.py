# ----------------------------------------------
# 4. v3_runtime_controller.py
# ----------------------------------------------
# Handles log_type overrides, back-propagation on error, dynamic substitutions.

import random
from utils.trace_utils import generate_trace_id
from v3_log_template_manager import generate_log_from_template
from utils.random_utils import get_random_ip
from utils.random_utils import get_random_user_id



class RuntimeController:
    def __init__(self, templates, reverse_templates):
        self.templates = templates
        self.reverse_templates = reverse_templates

    def generate_logs_for_flow(self, flow):
        trace_id = generate_trace_id()
        ip_addr = get_random_ip()
        user_id = get_random_user_id()
        api_endpoint = flow['endpoint']

        logs = []
        forward_log_records = []

        services = self._flatten_services(flow['api_logs'], 'INFO')  # Start with INFO
        error_triggered = False
        last_log_type = 'INFO'  # Default unless overridden

        # === FORWARD FLOW ===
        for service in services:
            # Decide severity
            current_type = 'INFO'
            rand_val = random.random()

            if current_type == 'INFO' and rand_val < 0.6:
                current_type = 'WARN'

            if current_type != 'ERROR' and rand_val < 0.2:
                current_type = 'ERROR'
                error_triggered = True

            log = generate_log_from_template(
                service, api_endpoint, current_type, self.templates,
                trace_id=trace_id, ip_address=ip_addr, user_id=user_id
            )

            if log:
                logs.append(log)
                forward_log_records.append((service, current_type))
                last_log_type = current_type

            if current_type == 'ERROR':
                break  # Stop forward flow on ERROR

        # === REVERSE PROPAGATION ===
        if forward_log_records:
            if error_triggered:
                reverse_type = 'ERROR'
            else:
                reverse_type = last_log_type

            # Always reverse all previous services (excluding the one that broke, if ERROR)
            if error_triggered:
                reverse_services = [s for s, _ in reversed(forward_log_records[:-1])]
            else:
                reverse_services = [s for s, _ in reversed(forward_log_records)]

            for service in reverse_services:
                reverse_log = generate_log_from_template(
                    service, api_endpoint, reverse_type, self.reverse_templates,
                    trace_id=trace_id, ip_address=ip_addr, user_id=user_id
                )
                if reverse_log:
                    logs.append(reverse_log)

        return logs

    # def generate_logs_for_flow(self, flow):
    #     trace_id = generate_trace_id()
    #     ip_addr = get_random_ip()
    #     user_id = get_random_user_id()
    #     api_endpoint = flow['endpoint']
    #
    #     logs = []
    #     forward_log_records = []
    #
    #     flow_type = self._decide_flow_type()
    #     services = self._flatten_services(flow['api_logs'], flow_type)
    #
    #     error_triggered = False
    #
    #     for service in services:
    #         current_type = flow_type
    #
    #         if random.random() < 0.6:
    #             current_type = 'WARN'
    #
    #         # Randomly inject an ERROR (simulate failure)
    #         if not error_triggered and random.random() < 0.3:
    #             current_type = 'ERROR'
    #             error_triggered = True
    #
    #             log = generate_log_from_template(
    #                 service, api_endpoint, current_type, self.templates,
    #                 trace_id=trace_id, ip_address=ip_addr, user_id=user_id
    #             )
    #             if log:
    #                 logs.append(log)
    #                 forward_log_records.append((service, current_type))
    #             break  # stop further forward flow
    #
    #         # Normal forward log
    #         log = generate_log_from_template(
    #             service, api_endpoint, current_type, self.templates,
    #             trace_id=trace_id, ip_address=ip_addr, user_id=user_id
    #         )
    #         if log:
    #             logs.append(log)
    #             forward_log_records.append((service, current_type))
    #
    #     # === Reverse Propagation ===
    #     if forward_log_records:
    #         reverse_type = 'ERROR' if error_triggered else forward_log_records[-1][1]
    #         # 🔁 Always include all services in reverse, including the one that failed
    #         reverse_services = [s for s, _ in reversed(forward_log_records)]
    #
    #         for service in reverse_services:
    #             reverse_log = generate_log_from_template(
    #                 service, api_endpoint, reverse_type, self.reverse_templates,
    #                 trace_id=trace_id, ip_address=ip_addr, user_id=user_id
    #             )
    #             if reverse_log:
    #                 logs.append(reverse_log)
    #
    #     return logs


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