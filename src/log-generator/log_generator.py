import os
import random
import time
import uuid
import yaml
from datetime import datetime, timedelta
from common.config_loader import load_config

config = load_config()
CONFIG_PATH = config['scenarios']['config']
LOG_FILE_PATH = config['scenarios']['log_file']


# --- CONFIGURATION ---
# CONFIG_PATH = "log-generator/config/scenario_config.yaml"
# LOG_FILE_PATH = "resources/data/synthetic-logs/synthetic-log.log"


# Load the YAML scenario config
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

scenarios = config["scenarios"]


# --- HELPERS ---
def random_ip():
    return ".".join(str(random.randint(1, 255)) for _ in range(4))


def random_uid():
    return str(random.randint(1000, 9999))


def fill_template(template: str, context: dict) -> str:
    for key, value in context.items():
        template = template.replace(f"{{{key}}}", str(value))
    return template


def write_log(line: str):
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    with open(LOG_FILE_PATH, "a") as f:
        f.write(line + "\n")


# --- FATIGUE LOGIC TRACKING ---
used_fatigues = set()
last_fatigue_time = datetime.now()

# Assume you’ve loaded the config like this:
scenarios = config["scenarios"]
unused_scenarios = [s for s in scenarios]  # or filtered ones
# Select one scenario randomly
scenario = random.choice(unused_scenarios)  # or random.choice(scenarios)

# Now, check the steps within that scenario
if any("[ERROR]" in step["template"] for step in scenario["steps"]):
    fatigue_interval = timedelta(seconds=random.randint(15, 30))
else:
    fatigue_interval = timedelta(seconds=random.randint(45, 90))

# if any("[ERROR]" in step["template"] for step in scenarios["steps"]):
#     fatigue_interval = timedelta(seconds=random.randint(15, 30))
# else:
#     fatigue_interval = timedelta(seconds=random.randint(45, 90))


# --- LOG GENERATORS ---
def generate_normal_log():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [INFO] Health check OK from {random_ip()}"
    write_log(log_line)


def generate_fatigue_log():
    global fatigue_interval, last_fatigue_time

    unused = [s for s in scenarios if s["name"] not in used_fatigues]
    if not unused:
        print("✅ All fatigue scenarios used once.")
        return

    scenario = random.choice(unused)
    used_fatigues.add(scenario["name"])

    now = datetime.now()
    trace_id = str(uuid.uuid4())
    shared_context = {
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "trace_id": trace_id,
        "ip": random_ip(),
        "uid": random_uid(),
        "score": random.randint(1, 10),
        "topic": f"topic-{random.randint(1, 5)}",
        "partition": random.randint(0, 3),
        "lag": random.randint(100, 2000),
        "ms": random.randint(500, 5000),
        "mount_path": f"/mnt/disk{random.randint(1, 3)}",
        "source_ip": random_ip(),
        "target_ip": random_ip()
    }

    print(f"\n\U0001F4A5 Injecting fatigue: {scenario['name']} - {scenario['description']}")
    for step in scenario["steps"]:
        log_line = fill_template(step["template"], shared_context)
        write_log(log_line)
        time.sleep(0.1)

    if any("[ERROR]" in step["template"] for step in scenario["steps"]):
        fatigue_interval = timedelta(seconds=random.randint(15, 30))
    else:
        fatigue_interval = timedelta(seconds=random.randint(45, 90))

    last_fatigue_time = datetime.now()


# --- MAIN LOOP ---
def main():
    print("\U0001F4E1 Synthetic log stream started...\n")
    while True:
        now = datetime.now()
        generate_normal_log()

        if now - last_fatigue_time >= fatigue_interval:
            generate_fatigue_log()

        time.sleep(1)


if __name__ == "__main__":
    main()
