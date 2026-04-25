#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# create-state-storage.sh – Bootstrap the Azure Government Storage Account
#                           used to hold Terraform remote state.
#
# What this script does:
#   1. Switches the active Azure CLI cloud to AzureUSGovernment.
#   2. Creates (or confirms) a resource group and storage account.
#   3. Creates a blob container named "tfstate".
#   4. Grants the currently signed-in user the
#      "Storage Blob Data Contributor" role on the storage account so that
#      Terraform can use Azure AD authentication for state operations.
#
# Usage:
#   ./create-state-storage.sh [prefix] [environment]
#
#   prefix      – short label prepended to resource names (default: vth)
#   environment – deployment label (default: dev)
#
# Prerequisites:
#   - Azure CLI installed and signed in to Azure Government
#     (az login --allow-no-subscriptions can be used for initial auth).
#   - Sufficient permissions to create resource groups and storage accounts.
# ---------------------------------------------------------------------------

set -euo pipefail

# ── Configuration ─────────────────────────────────────────────────────────────

PREFIX="${1:-vth}"
ENVIRONMENT="${2:-dev}"
LOCATION="usgovarizona"
STATE_RG="rg-${PREFIX}-tfstate"
STATE_SA="${PREFIX}st${ENVIRONMENT}tfstate"
STATE_CONTAINER="tfstate"

# ── Helpers ───────────────────────────────────────────────────────────────────

info()  { echo "  [INFO]  $*"; }
error() { echo "  [ERROR] $*" >&2; exit 1; }

# ── 1. Switch to Azure Government ─────────────────────────────────────────────

info "Setting Azure CLI cloud to AzureUSGovernment …"
az cloud set --name AzureUSGovernment

# ── 2. Verify login ───────────────────────────────────────────────────────────

SUBSCRIPTION_ID=$(az account show --query id -o tsv 2>/dev/null) \
  || error "Not logged in.  Run: az login"
info "Using subscription: ${SUBSCRIPTION_ID}"

USER_OBJECT_ID=$(az ad signed-in-user show --query id -o tsv)
info "Current user object ID: ${USER_OBJECT_ID}"

# ── 3. Resource Group ─────────────────────────────────────────────────────────

info "Creating resource group '${STATE_RG}' in '${LOCATION}' …"
az group create \
  --name     "${STATE_RG}" \
  --location "${LOCATION}" \
  --output   none

# ── 4. Storage Account ────────────────────────────────────────────────────────

info "Creating storage account '${STATE_SA}' …"
az storage account create \
  --name                   "${STATE_SA}" \
  --resource-group         "${STATE_RG}" \
  --location               "${LOCATION}" \
  --sku                    Standard_LRS \
  --kind                   StorageV2 \
  --https-only             true \
  --min-tls-version        TLS1_2 \
  --allow-blob-public-access false \
  --output                 none

# ── 5. Blob Container ─────────────────────────────────────────────────────────

info "Creating blob container '${STATE_CONTAINER}' …"
az storage container create \
  --name         "${STATE_CONTAINER}" \
  --account-name "${STATE_SA}" \
  --auth-mode    login \
  --output       none

# ── 6. Role Assignment ────────────────────────────────────────────────────────

SA_ID=$(az storage account show \
  --name           "${STATE_SA}" \
  --resource-group "${STATE_RG}" \
  --query          id \
  -o               tsv)

info "Assigning 'Storage Blob Data Contributor' to current user …"
az role assignment create \
  --role       "Storage Blob Data Contributor" \
  --assignee   "${USER_OBJECT_ID}" \
  --scope      "${SA_ID}" \
  --output     none

# ── 7. Summary ────────────────────────────────────────────────────────────────

echo ""
echo "  ✔  Terraform state storage ready."
echo ""
echo "  Resource group : ${STATE_RG}"
echo "  Storage account: ${STATE_SA}"
echo "  Container      : ${STATE_CONTAINER}"
echo ""
echo "  Use these values with infra/scripts/init.sh:"
echo "    PREFIX=${PREFIX}  ENVIRONMENT=${ENVIRONMENT}"
echo ""
