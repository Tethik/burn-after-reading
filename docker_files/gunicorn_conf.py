import os
import time
import threading

# Gunicorn config variables
loglevel = "info"
errorlog = "-"  # stderr
accesslog = "-"  # stdout
worker_tmp_dir = "/dev/shm"
graceful_timeout = 120
timeout = 120
keepalive = 5
workers = 4
threads = 3


def when_ready(server):
    """Periodically purge expired entries, even with no incoming traffic.

    Request handlers already expire entries on every call (see
    burn.api.before_request); this background loop is the no-traffic backstop
    that uWSGI's cron used to provide. It runs once, in the gunicorn master
    process, so it fires a single time regardless of worker count.
    """
    interval = int(os.environ.get("BURN_CLEAN_INTERVAL", 300))

    def loop():
        from burn.cleaner import main as expire
        while True:
            time.sleep(interval)
            try:
                expire()
            except Exception:
                server.log.exception("burn cleaner failed")

    threading.Thread(target=loop, name="burn-cleaner", daemon=True).start()
