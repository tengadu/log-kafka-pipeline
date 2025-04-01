# ----------------------------------------------
# 5. v3_log_template_manager.py
# ----------------------------------------------
# Given a service and log level, pick a message and fill in placeholders.

import random
from utils.random_utils import get_random_dynamic_values
from utils.timestamp_utils import current_utc_timestamp


def generate_log_from_template(service, api_endpoint, level, templates,
                               trace_id=None, ip_address=None, user_id=None,
                               product_id=None):
    candidates = templates.get(service, [])
    options = [tpl[level] for tpl in candidates if level in tpl]
    if not options:
        return ""
    template = random.choice(options)
    values = get_random_dynamic_values(api_endpoint, service)

    if ip_address:  # Inject flow-level ip_address for all the calls with just one IP
        values['ip_address'] = ip_address
    if user_id:  # Inject flow-level ip_address for all the calls with just one IP
        values['user_id'] = user_id
    if product_id:  # Inject flow-level ip_address for all the calls with just one IP
        values['product_id'] = product_id


    message = template.format(**values)
    timestamp = current_utc_timestamp()

    trace_part = f"[trace_id={trace_id}]" if trace_id else ""
    return f"[{timestamp}] [{level}] {trace_part} [service={service}] {message}"
