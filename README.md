# sensor-simulator

A self-contained synthetic sensor data simulator that runs on **k3s** (or any Kubernetes cluster) and publishes sensor readings and health messages to **Azure Service Bus** using Managed Identity.

---

## Overview

```
apps/sensor-simulator/
├── app.py                   # Main application
├── Dockerfile               # Container image definition
├── build-image.sh           # Script to build & push to ACR
├── requirements.txt         # Python dependencies
├── config/
│   └── config.json          # Sensor configuration
├── inbox/
│   └── messages.json        # Synthetic sensor payloads
└── helm/
    └── sensor-simulator/    # Helm chart
        ├── Chart.yaml
        ├── values.yaml
        └── templates/
            ├── _helpers.tpl
            ├── configmap.yaml
            ├── deployment.yaml
            └── serviceaccount.yaml
```

---

## Configuration (`config/config.json`)

| Field | Type | Description |
|---|---|---|
| `sensor_name` | string | Name stamped on every outbound message |
| `message_interval` | number | Seconds between sensor messages |
| `message_topic` | string | Azure Service Bus topic for sensor data |
| `health_interval` | number | Seconds between health messages |
| `health_topic` | string | Azure Service Bus topic for health messages |
| `run_continuous` | bool | Restart the inbox list when exhausted |
| `service_bus_namespace` | string | FQDN of the Service Bus namespace (e.g. `myns.servicebus.windows.net`) |

```json
{
  "sensor_name": "sensor-alpha-01",
  "message_interval": 5,
  "message_topic": "sensor-data",
  "health_interval": 30,
  "health_topic": "sensor-health",
  "run_continuous": true,
  "service_bus_namespace": "your-namespace.servicebus.windows.net"
}
```

Authentication to Azure Service Bus is done via **Managed Identity** (`DefaultAzureCredential`). No secrets are stored in the config file.

---

## Inbox (`inbox/messages.json`)

A JSON array of raw sensor reading objects. On startup the application loads every `*.json` file from the inbox directory into memory and sends one reading per `message_interval`.

If `run_continuous` is `true`, the list cycles indefinitely. Otherwise the process exits after all messages have been sent.

---

## Sensor Message Format

```json
{
  "sensor_name": "sensor-alpha-01",
  "date_time": "2024-01-15T10:30:00.123456+00:00",
  "correlation_id": "a1b2c3d4-e5f6-...",
  "content": { /* raw payload from inbox */ }
}
```

---

## Health Message Format

```json
{
  "sensor_name": "sensor-alpha-01",
  "date_time": "2024-01-15T10:30:00.123456+00:00",
  "status": "green",
  "last_error_message": ""
}
```

### Status Codes

| Status | Condition |
|---|---|
| `green` | No errors in the last 10 minutes |
| `yellow` | 1–5 errors in the last 10 minutes (circuit half-open / degraded) |
| `red` | 6 or more errors in the last 10 minutes (circuit open, publishing suspended) |

---

## Circuit Breaker

The application uses a sliding-window circuit breaker that monitors the last **10 minutes** of errors:

| Errors in window | State | Behaviour |
|---|---|---|
| 0 | CLOSED | Normal operation |
| 1–5 | HALF-OPEN | Still publishing, health status = yellow |
| 6+ | OPEN | Sensor publishing suspended, health status = red |

The breaker automatically recovers once all error timestamps fall outside the 10-minute window.

---

## Build & Push to ACR

```bash
# Authenticate to ACR
az acr login --name <registry-name>

# Build and push (tag defaults to "latest")
./build-image.sh myregistry.azurecr.io

# Build and push with a specific tag
./build-image.sh myregistry.azurecr.io v1.0.0
```

---

## Helm Deployment

### Single instance

```bash
helm install sensor-alpha \
  ./helm/sensor-simulator \
  --set image.repository=myregistry.azurecr.io/sensor-simulator \
  --set config.sensor_name=sensor-alpha-01 \
  --set config.service_bus_namespace=myns.servicebus.windows.net
```

### Multiple instances

```bash
# Instance 1
helm install sensor-alpha ./helm/sensor-simulator \
  --set config.sensor_name=sensor-alpha-01 \
  --set config.message_topic=sensor-data-alpha

# Instance 2
helm install sensor-beta ./helm/sensor-simulator \
  --set config.sensor_name=sensor-beta-01 \
  --set config.message_topic=sensor-data-beta
```

### Using externally mounted volumes (PVCs)

```bash
helm install sensor-alpha ./helm/sensor-simulator \
  --set useExternalVolumes=true \
  --set pvcNames.config=sensor-alpha-config-pvc \
  --set pvcNames.inbox=sensor-alpha-inbox-pvc
```

### Workload Identity (recommended for production)

```bash
helm install sensor-alpha ./helm/sensor-simulator \
  --set serviceAccount.annotations."azure\.workload\.identity/client-id"=<client-id>
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `CONFIG_PATH` | `/app/config/config.json` | Path to the config file |
| `INBOX_DIR` | `/app/inbox` | Path to the inbox directory |
| `APP_BASE_DIR` | `/app` | Base directory (used when the above are unset) |
