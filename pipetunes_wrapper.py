# pipetunes_wrapper.py 
import subprocess
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_pipetunes_snapshot():
    script_path = os.path.join(BASE_DIR, "pipetunes", "pipe_tunes.py")

    logs = []
    proc = subprocess.Popen(
        ["python3", script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    for line in proc.stdout:
        logs.append(line.strip())
    proc.wait()
    return logs