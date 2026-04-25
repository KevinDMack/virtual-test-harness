#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# destroy.sh – Destroy all resources managed by Terraform in Azure Government.
#
# Usage:
#   ./destroy.sh [prefix] [environment]
#
#   prefix      – short label used in resource names (default: vth)
#   environment – deployment label (default: dev)
#
# WARNING: This permanently deletes all infrastructure.  You will be prompted
#          to confirm unless the TF_AUTO_APPROVE=true environment variable is
#          set (use with caution in automation).
#
# Prerequisites:
#   - Terraform initialised (run init.sh first).
#   - Azure CLI signed in to Azure Government.
# ---------------------------------------------------------------------------

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

PREFIX="${1:-vth}"
ENVIRONMENT="${2:-dev}"

echo "==> Setting Azure CLI cloud to AzureUSGovernment …"
az cloud set --name AzureUSGovernment

export ARM_ENVIRONMENT="usgovernment"
export ARM_USE_CLI="true"

AUTO_APPROVE_FLAG=""
if [[ "${TF_AUTO_APPROVE:-false}" == "true" ]]; then
  AUTO_APPROVE_FLAG="-auto-approve"
  echo "  [WARN] TF_AUTO_APPROVE is set – skipping confirmation prompt."
fi

echo "==> Destroying Terraform-managed resources …"
# shellcheck disable=SC2086
terraform -chdir="${INFRA_DIR}" destroy \
  -var="prefix=${PREFIX}" \
  -var="environment=${ENVIRONMENT}" \
  ${AUTO_APPROVE_FLAG}

echo "==> Destroy complete."
