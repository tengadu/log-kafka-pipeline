# ----------------------------------------------
# 3. v3_flow_manager.py
# ----------------------------------------------
# Picks a random flow (e.g., ecommerce_checkout) and parses services.

import random


class FlowManager:
    def __init__(self, workflows):
        self.flows = workflows['http_logs']

    def pick_random_flow(self):
        flow_name = random.choice(list(self.flows.keys()))
        return {
            'name': flow_name,
            'endpoint': self.flows[flow_name]['endpoint'],
            'api_logs': self.flows[flow_name]['api_logs'],
            'infra_logs': self.flows[flow_name]['infra_logs']
        }