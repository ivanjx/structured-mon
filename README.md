# structured-mon (system metrics)

Simple forwarder that polls system resource usage and emits JSON lines to stdout.

## Files
- [Dockerfile](Dockerfile): builds a minimal image based on `python:3.12-slim` and installs `psutil`.
- [app.py](app.py): Python forwarder; prints JSON events with CPU, memory, and swap metrics to stdout.

## Environment
- `INTERVAL` (optional): polling interval in seconds (default: `10`).

## Build (Docker)
Build the image:

```bash
docker build -t structured-mon:latest .
```

Run the container (example):

```bash
docker run --rm --name structured-mon structured-mon:latest
```

To set a custom interval:

```bash
docker run --rm -e INTERVAL=30 structured-mon:latest
```

## Run locally (for debugging)
Requires `psutil` installed. Then run:

```bash
python app.py
```

## Next steps
- (Optional) Add a simple healthcheck or logging configuration.
- (Optional) Add CI checks to build the image and run the app.
