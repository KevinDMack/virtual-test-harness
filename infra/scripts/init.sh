#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# init.sh – Initialize Terraform for Azure Government with the remote backend.
#
# Usage:
#   ./init.sh [prefix] [environment]
#
#   prefix      – short label matching the state storage resources (default: vth)
#   environment – deployment label (default: dev)
#
# Prerequisites:
#   - Azure CLI installed and signed in (az login).
#   - State storage created by create-state-storage.sh.
# ---------------------------------------------------------------------------

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

PREFIX="${1:-vth}"
ENVIRONMENT="${2:-dev}"

STATE_RG="rg-${PREFIX}-tfstate"
STATE_SA="${PREFIX}st${ENVIRONMENT}tfstate"
STATE_CONTAINER="tfstate"
STATE_KEY="${PREFIX}-${ENVIRONMENT}.tfstate"

echo "==> Setting Azure CLI cloud to AzureUSGovernment …"
az cloud set --name AzureUSGovernment

# Terraform uses ARM_* env vars to authenticate via the Azure CLI.
export ARM_ENVIRONMENT="usgovernment"
export ARM_USE_CLI="true"

echo "==> Initialising Terraform …"
terraform -chdir="${INFRA_DIR}" init \
  -backend-config="resource_group_name=${STATE_RG}" \
  -backend-config="storage_account_name=${STATE_SA}" \
  -backend-config="container_name=${STATE_CONTAINER}" \
  -backend-config="key=${STATE_KEY}" \
  -backend-config="use_azuread_auth=true" \
  -backend-config="environment=usgovernment"

echo "==> Done.  Terraform initialised successfully."
