import subprocess
import yaml
import os
import sys

BOTS_YAML = os.path.join(os.path.dirname(__file__), "../data/bots.yaml")
with open(BOTS_YAML) as f:
    data = yaml.safe_load(f)

processes = []

for bot_info in data["bots"]:
    # Full path to run_single_bot.py
    script_path = os.path.join(os.path.dirname(__file__), "listen_one.py")

    # Start each bot in its own process
    p = subprocess.Popen(
        [sys.executable, script_path, bot_info["token_env"]],
        stdout=None,   # or redirect to a file for logs
        stderr=None
    )
    processes.append(p)

print("All bots launched.")