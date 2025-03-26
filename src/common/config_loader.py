import os
import yaml
import json


def load_config(config_path=None):
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "config", "config.yaml")

    ext = os.path.splitext(config_path)[-1].lower()
    with open(config_path, "r") as f:
        if ext in [".yaml", ".yml"]:
            return yaml.safe_load(f)
        elif ext == ".json":
            return json.load(f)
        else:
            raise ValueError("Unsupported config file format.")