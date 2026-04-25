#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# validate.sh – Validate the Terraform configuration.
#
# Usage:
#   ./validate.sh
#
# Prerequisites:
#   - Terraform initialised (run init.sh first).
# ---------------------------------------------------------------------------

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "==> Setting Azure CLI cloud to AzureUSGovernment …"
az cloud set --name AzureUSGovernment

export ARM_ENVIRONMENT="usgovernment"
export ARM_USE_CLI="true"

echo "==> Validating Terraform configuration …"
terraform -chdir="${INFRA_DIR}" validate

echo "==> Validation passed."
