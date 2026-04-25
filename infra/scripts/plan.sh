#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# plan.sh – Generate a Terraform execution plan for Azure Government.
#
# Usage:
#   ./plan.sh [prefix] [environment] [extra terraform flags …]
#
#   prefix      – short label used in resource names (default: vth)
#   environment – deployment label (default: dev)
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
shift 2 2>/dev/null || true   # consume the first two positional params

PLAN_FILE="${INFRA_DIR}/${PREFIX}-${ENVIRONMENT}.tfplan"

echo "==> Setting Azure CLI cloud to AzureUSGovernment …"
az cloud set --name AzureUSGovernment

export ARM_ENVIRONMENT="usgovernment"
export ARM_USE_CLI="true"

echo "==> Generating Terraform plan …"
terraform -chdir="${INFRA_DIR}" plan \
  -var="prefix=${PREFIX}" \
  -var="environment=${ENVIRONMENT}" \
  -out="${PLAN_FILE}" \
  "$@"

echo "==> Plan saved to: ${PLAN_FILE}"
