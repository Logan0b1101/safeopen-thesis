# gui/service_control.py

import subprocess

SERVICE_NAME = "safeopen.service"

def start_service():
    subprocess.run(["sudo", "systemctl", "start", SERVICE_NAME])

def stop_service():
    subprocess.run(["sudo", "systemctl", "stop", SERVICE_NAME])

def service_status():
    result = subprocess.run(
        ["systemctl", "is-active", SERVICE_NAME],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()
