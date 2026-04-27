# sensor-simulator

A self-contained synthetic sensor data simulator that runs on **AKS** (or any Kubernetes cluster) and publishes sensor readings and health messages to either **Azure Service Bus** (using Managed Identity) or an **MQTT broker**, selected via configuration.

---

## Overview

```
virtual-test-harness/
├── app.py                   # Main application
├── Dockerfile               # Container image definition
├── build-image.sh           # Script to build & push to ACR
├── requirements.txt         # Python runtime dependencies
├── requirements-dev.txt     # Python dev/test dependencies
├── config/
│   └── config.json          # Sensor configuration
├── inbox/
│   └── messages.json        # Synthetic sensor payloads
├── tests/
│   ├── conftest.py          # Pytest fixtures / Azure SDK stubs
│   └── test_app.py          # Automated unit tests
├── helm/
│   └── sensor-simulator/    # Helm chart
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── _helpers.tpl
│           ├── configmap.yaml
│           ├── deployment.yaml
│           ├── mqtt-broker.yaml
│           └── serviceaccount.yaml
├── infra/                   # Terraform – Azure Government AKS infrastructure
│   ├── providers.tf
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── modules/
│   │   ├── aks/             # AKS cluster (workload identity + KV CSI)
│   │   ├── keyvault/        # Azure Key Vault (RBAC auth)
│   │   ├── storage/         # Storage Account (key access disabled)
│   │   └── acr/             # Container Registry (admin disabled)
│   └── scripts/             # Wrapper scripts (init / plan / apply / destroy)
└── docs/
    └── infrastructure.md    # Full infrastructure documentation
```

---

## Infrastructure (Azure Government)

The `infra/` directory contains Terraform modules that deploy a full AKS
testing environment to **Azure Government** (`usgovarizona`):

- **AKS cluster** – with workload identity, OIDC issuer, and Key Vault CSI
  Secret Store driver.
- **Key Vault** – RBAC-based authorization; no legacy access policies.
- **Storage Account** – SAS/key-based access disabled; Azure AD auth only.
- **Container Registry** – admin account disabled; image pulls via
  managed identity.

All inter-service access uses **managed identity and Azure RBAC** – no
secrets are stored in configuration files.

See **[docs/infrastructure.md](docs/infrastructure.md)** for the complete
setup guide, script reference, and variable/output reference.

### Quick start

```bash
# Sign in to Azure Government
az cloud set --name AzureUSGovernment && az login

# Bootstrap state storage (one-time)
bash infra/scripts/create-state-storage.sh

# Init → Plan → Apply
bash infra/scripts/init.sh
bash infra/scripts/plan.sh
bash infra/scripts/apply.sh
```

---

## Configuration (`config/config.json`)

### Common fields (required for all bus types)

| Field | Type | Description |
|---|---|---|
| `sensor_name` | string | Name stamped on every outbound message |
| `message_interval` | number | Seconds between sensor messages |
| `message_topic` | string | Topic / MQTT topic path for sensor data |
| `health_interval` | number | Seconds between health messages |
| `health_topic` | string | Topic / MQTT topic path for health messages |
| `run_continuous` | bool | Restart the inbox list when exhausted |
| `message_bus_type` | string | `"servicebus"` (default) or `"mqtt"` |

### Azure Service Bus (`message_bus_type: "servicebus"`)

| Field | Type | Description |
|---|---|---|
| `service_bus_namespace` | string | FQDN of the Service Bus namespace (e.g. `myns.servicebus.windows.net`) |

```json
{
  "sensor_name": "sensor-alpha-01",
  "message_interval": 5,
  "message_topic": "sensor-data",
  "health_interval": 30,
  "health_topic": "sensor-health",
  "run_continuous": true,
  "message_bus_type": "servicebus",
  "service_bus_namespace": "your-namespace.servicebus.windows.net"
}
```

Authentication is done via **Managed Identity** (`DefaultAzureCredential`). No secrets are stored in the config file.

### MQTT (`message_bus_type: "mqtt"`)

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `mqtt_broker_host` | string | ✅ | – | Hostname or IP of the MQTT broker |
| `mqtt_broker_port` | number | ✅ | – | TCP port of the MQTT broker (typically `1883` or `8883` for TLS) |
| `mqtt_client_id` | string | ❌ | `sensor_name` | MQTT client identifier |
| `mqtt_username` | string | ❌ | `""` | Username for broker authentication |
| `mqtt_password` | string | ❌ | `""` | Password for broker authentication |
| `mqtt_use_tls` | bool | ❌ | `false` | Enable TLS for the broker connection |
| `mqtt_qos` | number | ❌ | `1` | MQTT QoS level (0, 1, or 2) |

```json
{
  "sensor_name": "sensor-alpha-01",
  "message_interval": 5,
  "message_topic": "sensor/data",
  "health_interval": 30,
  "health_topic": "sensor/health",
  "run_continuous": true,
  "message_bus_type": "mqtt",
  "mqtt_broker_host": "mosquitto",
  "mqtt_broker_port": 1883
}
```

> **Tip:** When using the Helm chart with the built-in MQTT broker option (see below), set `mqtt_broker_host` to the broker's Kubernetes Service name (e.g. `<release>-sensor-simulator-mqtt-broker`).

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

### Azure Service Bus – single instance

```bash
helm install sensor-alpha \
  ./helm/sensor-simulator \
  --set image.repository=myregistry.azurecr.io/sensor-simulator \
  --set config.sensor_name=sensor-alpha-01 \
  --set config.message_bus_type=servicebus \
  --set config.service_bus_namespace=myns.servicebus.windows.net
```

### Azure Service Bus – multiple instances

```bash
# Instance 1
helm install sensor-alpha ./helm/sensor-simulator \
  --set config.sensor_name=sensor-alpha-01 \
  --set config.message_bus_type=servicebus \
  --set config.message_topic=sensor-data-alpha

# Instance 2
helm install sensor-beta ./helm/sensor-simulator \
  --set config.sensor_name=sensor-beta-01 \
  --set config.message_bus_type=servicebus \
  --set config.message_topic=sensor-data-beta
```

### MQTT – with built-in Mosquitto broker pod

Set `mqtt.broker.enabled=true` to deploy an [Eclipse Mosquitto](https://mosquitto.org/) broker alongside the simulator in the same namespace.  The sensor-simulator's config is automatically wired to connect to the broker Service.

```bash
helm install sensor-alpha \
  ./helm/sensor-simulator \
  --set image.repository=myregistry.azurecr.io/sensor-simulator \
  --set config.sensor_name=sensor-alpha-01 \
  --set config.message_bus_type=mqtt \
  --set config.mqtt_broker_host=sensor-alpha-sensor-simulator-mqtt-broker \
  --set config.mqtt_broker_port=1883 \
  --set config.message_topic=sensor/data \
  --set config.health_topic=sensor/health \
  --set mqtt.broker.enabled=true
```

#### MQTT with TLS and authentication

```bash
helm install sensor-alpha \
  ./helm/sensor-simulator \
  --set image.repository=myregistry.azurecr.io/sensor-simulator \
  --set config.sensor_name=sensor-alpha-01 \
  --set config.message_bus_type=mqtt \
  --set config.mqtt_broker_host=my-external-broker.example.com \
  --set config.mqtt_broker_port=8883 \
  --set config.mqtt_use_tls=true \
  --set config.mqtt_username=myuser \
  --set config.mqtt_password=mypassword \
  --set config.message_topic=sensor/data \
  --set config.health_topic=sensor/health
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

## Running Tests

Install the development dependencies and run pytest:

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

Tests cover `CircuitBreaker`, config/inbox loading, message builders, publisher implementations (Service Bus and MQTT), factory, and the sensor and health publish loops.  All Azure SDK and paho-mqtt calls are stubbed so no real infrastructure is required.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `CONFIG_PATH` | `/app/config/config.json` | Path to the config file |
| `INBOX_DIR` | `/app/inbox` | Path to the inbox directory |
| `APP_BASE_DIR` | `/app` | Base directory (used when the above are unset) |
