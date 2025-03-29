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

# --- LOGIC TRACKING ---
used_fatigues = set()
last_fatigue_time = datetime.now()
fatigue_interval = timedelta(seconds=random.randint(45, 90))

# --- LOG GENERATORS ---
def generate_normal_log():
    """Randomly pick an INFO log from any scenario and inject it."""
    info_scenarios = [s for s in scenarios if any("[INFO]" in step["template"] for step in s["steps"])]
    if not info_scenarios:
        # fallback
        log_line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Health check OK from {random_ip()}"
        write_log(log_line)
        return

    scenario = random.choice(info_scenarios)
    # print(f"\n✅ Injecting Info Logs: {scenario['name']} - {scenario['description']}")
    shared_context = generate_context()

    info_steps = [step for step in scenario["steps"] if "[INFO]" in step["template"] or "[DEBUG]" in step["template"]]
    if not info_steps:
        log_line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Health check OK from {random_ip()}"
        write_log(log_line)
        return

    step = random.choice(info_steps)
    log_line = fill_template(step["template"], shared_context)
    write_log(log_line)

def generate_context():
    now = datetime.now()
    return {
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "trace_id": str(uuid.uuid4()),
        "ip": random_ip(),
        "uid": random_uid(),
        "score": random.randint(1, 10),
        "topic": f"topic-{random.randint(1, 5)}",
        "partition": random.randint(0, 3),
        "lag": random.randint(100, 2000),
        "ms": random.randint(500, 5000),
        "mount_path": f"/mnt/disk{random.randint(1, 3)}",
        "source_ip": random_ip(),
        "target_ip": random_ip(),
        "order_id": str(random.randint(100000, 999999))
    }

def generate_fatigue_log():
    global fatigue_interval, last_fatigue_time

    unused = [s for s in scenarios if s["name"] not in used_fatigues]
    if not unused:
        print("✅ All fatigue scenarios used once. 🔁 Restarting fatigue loop...")
        used_fatigues.clear()
        unused = scenarios[:]

    scenario = random.choice(unused)
    used_fatigues.add(scenario["name"])

    print(f"\n💥 Injecting fatigue: {scenario['name']} - {scenario['description']}")
    shared_context = generate_context()
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
