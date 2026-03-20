import time
import json
import os
from datetime import datetime, timezone
import psutil

INTERVAL = int(os.getenv("INTERVAL", "10"))


def get_system_metrics():
    """Collects system metrics (CPU, memory, swap, disk, load) and returns a dict."""
    now = datetime.now(timezone.utc).isoformat()
    metrics = {"timestamp": now}

    if psutil is None:
        metrics["error"] = "psutil not installed"
        return metrics

    # CPU
    try:
        metrics["cpu_percent"] = psutil.cpu_percent(interval=None)
        metrics["cpu_percpu_percent"] = psutil.cpu_percent(interval=None, percpu=True)
    except Exception:
        pass

    # Memory
    try:
        vm = psutil.virtual_memory()
        metrics["mem_total"] = vm.total
        metrics["mem_available"] = vm.available
        metrics["mem_used"] = vm.used
        metrics["mem_percent"] = vm.percent
    except Exception:
        pass

    # Swap
    try:
        sw = psutil.swap_memory()
        metrics["swap_total"] = sw.total
        metrics["swap_used"] = sw.used
        metrics["swap_free"] = sw.free
        metrics["swap_percent"] = sw.percent
    except Exception:
        pass

    return metrics


def main():
    print("Starting system metrics forwarder...")

    while True:
        try:
            data = get_system_metrics()
            event = {"source": "system_metrics", **data}
            print(json.dumps(event), flush=True)
        except Exception as e:
            print(json.dumps({"error": str(e)}), flush=True)

        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
