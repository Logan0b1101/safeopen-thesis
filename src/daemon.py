#!/usr/bin/env python3

import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.audit_logger import log_event

WATCH_DIR = "/tmp/safeopen_test"
DEBOUNCE = 0.2


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        path = event.src_path
        print("[SAFEOPEN] Detected:", path)

        time.sleep(DEBOUNCE)

        if not os.path.exists(path):
            print("[SAFEOPEN] File vanished")
            return

        try:
            log_event(
                file_path=path,
                static_label="LOW",
                static_reason="Filesystem create event",
                ml_prob=0.0,
                final_score=0.1,
                final_label="LOW",
                action="NONE",
                action_result="baseline-test"
            )
            print("[SAFEOPEN] Logged:", path)

        except Exception as e:
            print("[SAFEOPEN] LOG FAILED:", e)


def main():
    os.makedirs(WATCH_DIR, exist_ok=True)

    observer = Observer()
    observer.schedule(Handler(), WATCH_DIR, recursive=False)
    observer.start()

    print("[SAFEOPEN] Watching:", WATCH_DIR)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
