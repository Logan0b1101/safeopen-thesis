import subprocess

def get_daemon_status():
    try:
        result = subprocess.run(
            ["systemctl", "is-active", "safeopen.service"],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"
