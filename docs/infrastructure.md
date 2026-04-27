# Infrastructure – Azure Government AKS Deployment

This document covers the Terraform infrastructure that deploys the
**virtual-test-harness** workload onto an Azure Kubernetes Service (AKS)
cluster in **Azure Government** (`usgovarizona`).

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Directory Layout](#directory-layout)
4. [Modules](#modules)
5. [MQTT Pub/Sub Option](#mqtt-pubsub-option)
6. [Role Assignments](#role-assignments)
7. [Quick Start](#quick-start)
8. [Script Reference](#script-reference)
9. [VS Code Tasks](#vs-code-tasks)
10. [Backend State](#backend-state)
11. [Variables Reference](#variables-reference)
12. [Outputs Reference](#outputs-reference)

---

## Overview

```
Azure Government (usgovarizona)
│
├── Resource Group  rg-<prefix>-<env>
│   ├── AKS Cluster          aks-<prefix>-<env>
│   │   ├── System-assigned managed identity
│   │   ├── OIDC issuer (workload identity)
│   │   └── Key Vault CSI Secret Store driver
│   ├── Key Vault            kv-<prefix>-<env>
│   │   └── RBAC-based authorization (no access policies)
│   ├── Storage Account      <prefix>st<env>
│   │   └── Key-based access disabled (Azure AD auth only)
│   └── Container Registry   <prefix>acr<env>
│       └── Admin account disabled (managed identity pulls)
│
└── Role Assignments
    ├── AKS kubelet identity → AcrPull on Container Registry
    ├── AKS identity         → Key Vault Secrets User on Key Vault
    └── AKS identity         → Storage Blob Data Contributor on Storage Account
```

All authentication between Azure services uses **managed identity** and
**Azure RBAC** – no passwords, connection strings, or access keys are stored
or required.

---

## Prerequisites

| Tool | Minimum version | Notes |
|---|---|---|
| [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli) | 2.55+ | Must be signed in to Azure Government |
| [Terraform](https://developer.hashicorp.com/terraform/downloads) | 1.10.0+ | Included in the dev container |
| Sufficient Azure RBAC | – | Contributor + User Access Administrator on the subscription |

The [dev container](.devcontainer/devcontainer.json) ships with both tools
pre-installed.

---

## Directory Layout

```
infra/
├── providers.tf           # azurerm provider targeting Azure Government
├── main.tf                # Resource group, module calls, role assignments
├── variables.tf           # Root-level input variables
├── outputs.tf             # Root-level outputs
├── modules/
│   ├── aks/               # AKS cluster module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── keyvault/          # Key Vault module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── storage/           # Storage Account module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── acr/               # Container Registry module
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── scripts/
    ├── create-state-storage.sh   # One-time bootstrap for Terraform state
    ├── init.sh                   # terraform init (with remote backend)
    ├── validate.sh               # terraform validate
    ├── plan.sh                   # terraform plan
    ├── apply.sh                  # terraform apply
    └── destroy.sh                # terraform destroy
```

---

## Modules

### `modules/aks`

Deploys an Azure Kubernetes Service cluster with:

* **System-assigned managed identity** – used for control-plane Azure API
  calls and for the role assignments wired in the root module.
* **Kubelet managed identity** – used for container image pulls (AcrPull).
* **OIDC issuer + Workload Identity** – enables individual pods to exchange
  Kubernetes service account tokens for short-lived Azure AD tokens, allowing
  fine-grained, per-workload role assignments without sharing credentials.
* **Key Vault CSI Secret Store driver** – mounts Key Vault secrets as
  Kubernetes volumes, eliminating secret duplication in `Secret` objects.

### `modules/keyvault`

Deploys an Azure Key Vault with:

* **RBAC-based authorization** – data-plane access controlled by Azure role
  assignments rather than legacy access policies.
* **Purge protection** – prevents accidental permanent deletion.
* **Soft-delete retention** – 7 days by default (configurable).

### `modules/storage`

Deploys an Azure Storage Account with:

* `shared_access_key_enabled = false` – SAS tokens and storage account keys
  are disabled; all access must use Azure AD credentials.
* `allow_nested_items_to_be_public = false` – public anonymous blob access
  is blocked.
* TLS 1.2+ enforced; HTTPS-only traffic.
* Soft-delete for blobs and containers (7-day retention).

### `modules/acr`

Deploys an Azure Container Registry with:

* `admin_enabled = false` – the legacy admin username/password is disabled;
  image pulls use the `AcrPull` role assigned to the AKS kubelet identity.

---

## MQTT Pub/Sub Option

The simulator supports **MQTT** as an alternative to Azure Service Bus.  Setting
`message_bus_type: "mqtt"` in `config.json` switches the back-end.  An
[Eclipse Mosquitto](https://mosquitto.org/) broker can be co-deployed inside the
same Kubernetes namespace using the Helm chart's built-in `mqtt.broker` option –
no additional infrastructure outside the cluster is required.

### Architecture (MQTT mode)

```
┌─────────────────────────────────────────────────┐
│  Kubernetes Namespace                           │
│                                                  │
│  ┌──────────────────┐   MQTT (port 1883)  ┌──────────────────────┐
│  │  sensor-simulator│ ──────────────────► │  mosquitto broker    │
│  │  (app.py)        │                     │  (ClusterIP Service) │
│  └──────────────────┘                     └──────────────────────┘
│                                                  │
│  External consumers connect to the broker        │
│  via a LoadBalancer / NodePort Service or        │
│  by subscribing from within the cluster.         │
└─────────────────────────────────────────────────┘
```

### Helm deployment – MQTT with built-in broker

```bash
helm install sensor-alpha ./helm/sensor-simulator \
  --set image.repository=myregistry.azurecr.io/sensor-simulator \
  --set config.sensor_name=sensor-alpha-01 \
  --set config.message_bus_type=mqtt \
  --set config.mqtt_broker_host=sensor-alpha-sensor-simulator-mqtt-broker \
  --set config.mqtt_broker_port=1883 \
  --set config.message_topic=sensor/data \
  --set config.health_topic=sensor/health \
  --set mqtt.broker.enabled=true
```

When `mqtt.broker.enabled=true` the chart creates:

| Resource | Description |
|---|---|
| `Deployment` (`<release>-sensor-simulator-mqtt-broker`) | Runs the Mosquitto container |
| `Service` (`<release>-sensor-simulator-mqtt-broker`) | ClusterIP on port 1883 (and 9001 for WebSocket if enabled) |
| `ConfigMap` (`<release>-sensor-simulator-mqtt-broker-config`) | Mosquitto `mosquitto.conf` |

### Configurable broker values (`values.yaml`)

| Value | Default | Description |
|---|---|---|
| `mqtt.broker.enabled` | `false` | Deploy the Mosquitto broker pod |
| `mqtt.broker.image.repository` | `eclipse-mosquitto` | Broker container image |
| `mqtt.broker.image.tag` | `2.0.18` | Image tag |
| `mqtt.broker.image.pullPolicy` | `IfNotPresent` | Pull policy |
| `mqtt.broker.port` | `1883` | MQTT TCP listener port |
| `mqtt.broker.wsPort` | `9001` | WebSocket listener port (set to `0` to disable) |
| `mqtt.broker.allowAnonymous` | `true` | Allow unauthenticated connections (dev only; set `false` in production) |
| `mqtt.broker.persistence.enabled` | `false` | Mount a PVC for broker persistence |
| `mqtt.broker.persistence.size` | `1Gi` | PVC size when persistence is enabled |
| `mqtt.broker.resources` | (see values.yaml) | CPU/memory requests and limits |
| `mqtt.broker.extraConfig` | `""` | Additional lines appended to `mosquitto.conf` |

### Connecting an external subscriber

After deploying with `mqtt.broker.enabled=true`, expose the broker Service
externally (e.g. by patching to `LoadBalancer` or creating a `NodePort`) and
subscribe using any MQTT client:

```bash
# Port-forward for local testing
kubectl port-forward svc/sensor-alpha-sensor-simulator-mqtt-broker 1883:1883

# Subscribe to all sensor data
mosquitto_sub -h localhost -p 1883 -t "sensor/#" -v
```

### Security considerations

The built-in broker defaults to unauthenticated connections (`allowAnonymous: true`), which is intended for **development and cluster-internal use only**.  For production:

- Set `mqtt.broker.allowAnonymous=false` and supply a Mosquitto password file
  via `mqtt.broker.extraConfig` (e.g. `password_file /mosquitto/config/passwd`).
  Mount the password file into the broker pod by extending the broker's
  `ConfigMap` or using an additional `Secret` + volume in a custom overlay.
- Enable TLS by setting `config.mqtt_use_tls=true` on the sensor-simulator side
  and providing a valid CA/cert/key via `mqtt.broker.extraConfig` pointing to
  mounted certificate files.
- Consider using an external, hardened MQTT broker and leaving
  `mqtt.broker.enabled=false`.

---

## Role Assignments

| Principal | Role | Scope | Purpose |
|---|---|---|---|
| AKS kubelet identity | `AcrPull` | Container Registry | Pull container images |
| AKS system identity | `Key Vault Secrets User` | Key Vault | Read secrets via CSI driver |
| AKS system identity | `Storage Blob Data Contributor` | Storage Account | Read/write blob data |

---

## Quick Start

```bash
# 1. Sign in to Azure Government
az cloud set --name AzureUSGovernment
az login

# 2. Bootstrap Terraform state storage (one-time per deployment)
bash infra/scripts/create-state-storage.sh vth dev

# 3. Initialise Terraform with the remote backend
bash infra/scripts/init.sh vth dev

# 4. Review the plan
bash infra/scripts/plan.sh vth dev

# 5. Apply
bash infra/scripts/apply.sh vth dev
```

To tear down:

```bash
bash infra/scripts/destroy.sh vth dev
```

---

## Script Reference

All scripts target **Azure Government** by calling
`az cloud set --name AzureUSGovernment` and setting
`ARM_ENVIRONMENT=usgovernment` before invoking Terraform.

### `create-state-storage.sh [prefix] [environment]`

Creates the Azure resources needed to store Terraform state remotely:

1. Resource group `rg-<prefix>-tfstate` in `usgovarizona`.
2. Storage account `<prefix>st<env>tfstate` with HTTPS-only and no public
   blob access.
3. Blob container `tfstate`.
4. Assigns **Storage Blob Data Contributor** to the signed-in user so
   Terraform can read/write state without storage account keys.

Run this **once** before the first `init.sh`.

### `init.sh [prefix] [environment]`

Runs `terraform init` pointing at the remote backend created by
`create-state-storage.sh`.  Uses Azure AD authentication
(`use_azuread_auth=true`) – no storage account key is required.

### `validate.sh`

Runs `terraform validate` to check syntax and internal consistency.

### `plan.sh [prefix] [environment] [extra flags…]`

Runs `terraform plan` and saves the plan file to
`infra/<prefix>-<environment>.tfplan`.

### `apply.sh [prefix] [environment]`

Applies the saved plan file from `plan.sh`.  Falls back to an interactive
apply if no plan file is found.

### `destroy.sh [prefix] [environment]`

Destroys all Terraform-managed resources.  Prompts for confirmation unless
`TF_AUTO_APPROVE=true` is set.

---

## VS Code Tasks

The following tasks are available in VS Code (**Terminal → Run Task …**):

| Task | Script |
|---|---|
| Infra: Create State Storage | `infra/scripts/create-state-storage.sh` |
| Infra: Init | `infra/scripts/init.sh` |
| Infra: Validate | `infra/scripts/validate.sh` |
| Infra: Plan | `infra/scripts/plan.sh` |
| Infra: Apply | `infra/scripts/apply.sh` |
| Infra: Destroy | `infra/scripts/destroy.sh` |
| Tests: Run pytest | `python -m pytest tests/ -v` |

---

## Backend State

Terraform state is stored in an Azure Government Storage Account using Azure
AD authentication (no storage account key).

```hcl
# Configured at init time via init.sh
backend "azurerm" {
  resource_group_name  = "rg-<prefix>-tfstate"
  storage_account_name = "<prefix>st<env>tfstate"
  container_name       = "tfstate"
  key                  = "<prefix>-<env>.tfstate"
  use_azuread_auth     = true
  environment          = "usgovernment"
}
```

---

## Variables Reference

| Variable | Default | Description |
|---|---|---|
| `prefix` | `vth` | Short prefix prepended to all resource names (2–8 chars) |
| `environment` | `dev` | Deployment environment label |
| `location` | `usgovarizona` | Azure Government region |
| `tags` | `{}` | Additional tags merged onto every resource |
| `aks_node_count` | `2` | Nodes in the default node pool |
| `aks_vm_size` | `Standard_DS2_v2` | VM SKU for node pool |
| `aks_kubernetes_version` | `null` (latest) | Kubernetes version |
| `kv_soft_delete_retention_days` | `7` | Key Vault soft-delete retention |
| `storage_replication_type` | `LRS` | Storage account redundancy |
| `acr_sku` | `Standard` | Container Registry pricing tier |

---

## Outputs Reference

After a successful `apply`, the following outputs are available
(`terraform output -json`):

| Output | Description |
|---|---|
| `resource_group_name` | Resource group containing all resources |
| `aks_name` | AKS cluster name |
| `aks_oidc_issuer_url` | OIDC issuer URL for workload identity federation |
| `acr_login_server` | ACR login server hostname |
| `keyvault_uri` | Key Vault URI |
| `storage_account_name` | Storage account name |
| `storage_primary_blob_endpoint` | Primary blob endpoint URL |
