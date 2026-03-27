import subprocess
import os
import json
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_pipetunes_snapshot():
    """
    Runs pipe_tunes.py in headless mode and returns a list of dicts:
    [{"book": ..., "page": ..., "name": ...}, ...]
    """
    import os
    import subprocess
    import json

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script_path = os.path.join(BASE_DIR, "pipetunes", "pipe_tunes.py")

    env = os.environ.copy()
    env["HEADLESS"] = "1"  # Force headless

    logs = []
    proc = subprocess.Popen(
        ["python3", script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env
    )

    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
            if isinstance(entry, dict):
                logs.append(entry)
        except json.JSONDecodeError:
            parts = line.split(",")
            if len(parts) >= 3:
                logs.append({"book": parts[0], "page": parts[1], "name": parts[2]})

    proc.wait()
    return logs


    conn.close()
    return results