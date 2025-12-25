# src/sandbox_manager/sandbox.py
import subprocess
import datetime
import os
import traceback

def open_in_sandbox(file_path, timeout=60):
    """
    Open a file inside Firejail sandbox and write robust logs to results/sandbox_logs.txt.
    Returns (ok: bool, message: str).
    """
    try:
        # Resolve absolute paths
        project_root = os.path.abspath(os.getcwd())
        results_dir = os.path.join(project_root, "results")
        os.makedirs(results_dir, exist_ok=True)
        log_file = os.path.join(results_dir, "sandbox_logs.txt")

        # Normalize file path
        file_path = os.path.abspath(file_path)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Basic checks
        if not os.path.exists(file_path):
            msg = f"File not found: {file_path}"
            with open(log_file, "a") as log:
                log.write(f"[{timestamp}] ERROR: {msg}\n\n")
            return False, msg

        # Build command: open with LibreOffice inside Firejail, no network, private filesystem
        cmd = [
            "firejail",
            "--quiet",
            "--private",      # private home (limits file access)
            "--net=none",     # no network access
            "--caps.drop=all",# drop capabilities (extra hardening)
            "libreoffice",
            "--norestore",
            "--nolockcheck",
            file_path
        ]

        with open(log_file, "a") as log:
            log.write(f"[{timestamp}] SANDBOX START: {file_path}\n")
            log.write(f"[{timestamp}] CMD: {' '.join(cmd)}\n")
            log.flush()
            try:
                # Run and capture return
                subprocess.run(cmd, stdout=log, stderr=log, timeout=timeout, check=True)
                log.write(f"[{timestamp}] SANDBOX END: {file_path} (exit OK)\n\n")
                return True, "File opened safely in sandbox."
            except subprocess.CalledProcessError as e:
                log.write(f"[{timestamp}] ERROR: CalledProcessError: {e}\n{traceback.format_exc()}\n\n")
                return False, f"Sandbox process error: {e}"
            except subprocess.TimeoutExpired:
                log.write(f"[{timestamp}] ERROR: TimeoutExpired after {timeout}s for {file_path}\n\n")
                return False, "Sandbox session timed out."
            except Exception as ex:
                log.write(f"[{timestamp}] ERROR: Exception: {ex}\n{traceback.format_exc()}\n\n")
                return False, f"Sandbox manager exception: {ex}"

    except Exception as outer_ex:
        # If even logging failed, print to stdout (so you can see it)
        print("Critical sandbox manager failure:", outer_ex)
        print(traceback.format_exc())
        return False, f"Critical sandbox manager failure: {outer_ex}"

