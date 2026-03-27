# pipetunes_wrapper.py
import subprocess
import os
import json

# Base dir: adjust depending on your folder structure
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_pipetunes_snapshot():
    """
    Runs pipe_tunes.py in headless mode and returns a list of dicts:
    [{"book": ..., "page": ..., "name": ...}, ...]
    """
    script_path = os.path.join(BASE_DIR, "pipetunes", "pipe_tunes.py")

    logs = []

    # Run headless to output JSON lines
    proc = subprocess.Popen(
        ["python3", script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env={**os.environ, "HEADLESS": "1"}  # ensure HEADLESS mode
    )

    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        try:
            # Expect JSON dict per line
            entry = json.loads(line)
            if isinstance(entry, dict):
                logs.append(entry)
        except json.JSONDecodeError:
            # fallback: comma-separated book,page,name
            parts = line.split(",")
            if len(parts) >= 3:
                logs.append({"book": parts[0], "page": parts[1], "name": parts[2]})

    proc.wait()
    return logs