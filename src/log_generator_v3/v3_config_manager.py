# ----------------------------------------------
# 2. v3_config_manager.py
# ----------------------------------------------
# Loads and parses workflows and templates from existing config.

import yaml


def load_workflows_and_templates(config_path):
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    workflows = config_data['workflow']
    templates = config_data['templates']
    reverse_templates = config_data['reverse-templates']
    return workflows, templates, reverse_templates