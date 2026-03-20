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

    # CPU temperature (if available via psutil)
    try:
        temps = psutil.sensors_temperatures()
        cpu_vals = []
        if temps:
            # prefer common sensor keys
            for key in ("coretemp", "cpu_thermal", "acpitz"):
                if key in temps:
                    cpu_sensors = temps[key]
                    break
            else:
                cpu_sensors = next(iter(temps.values()))

            cpu_vals = [t.current for t in cpu_sensors if getattr(t, "current", None) is not None]
            if cpu_vals:
                metrics["cpu_temp_avg_c"] = sum(cpu_vals) / len(cpu_vals)
                for i, v in enumerate(cpu_vals):
                    metrics[f"cpu_temp_core_{i}"] = v
    except Exception:
        cpu_vals = []

    # Fallback: read from /sys/class/thermal/thermal_zone0/temp (Linux)
    if not cpu_vals:
        try:
            path = "/sys/class/thermal/thermal_zone0/temp"
            if os.path.exists(path):
                with open(path, "r") as f:
                    raw = f.read().strip()
                if raw:
                    # common units: millidegrees Celsius
                    val = int(raw)
                    if val > 1000:
                        temp_c = val / 1000.0
                    else:
                        temp_c = float(val)
                    metrics["cpu_temp_avg_c"] = temp_c
                    metrics["cpu_temp_core_0"] = temp_c
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
