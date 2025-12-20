import subprocess
import yaml
import os
import sys
from services.path_helper import get_file

BOTS_YAML = get_file("data", "bots.yaml")
with open(BOTS_YAML) as f:
    data = yaml.safe_load(f)

processes = []

for bot_info in data["bots"]:
    # Full path to run_single_bot.py  
    script_path = BOTS_YAML = get_file("jobs", "listen_one.py")

    # Start each bot in its own process
    p = subprocess.Popen(
        [sys.executable, script_path, bot_info["data"]["token_env"]],
        stdout=None,   # or redirect to a file for logs
        stderr=None
    )
    processes.append(p)

print("All bots launched.")