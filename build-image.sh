#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# build-image.sh – Build and push the sensor-simulator container image to an
#                  Azure Container Registry (ACR).
#
# Usage:
#   ./build-image.sh <acr-login-server> [image-tag]
#
# Examples:
#   ./build-image.sh myregistry.azurecr.io
#   ./build-image.sh myregistry.azurecr.io v1.2.0
#
# Prerequisites:
#   - Docker (or compatible OCI builder) installed and running.
#   - Authenticated to ACR, e.g. via `az acr login --name <registry-name>`.
# ---------------------------------------------------------------------------

set -euo pipefail

ACR_LOGIN_SERVER="${1:?Usage: $0 <acr-login-server> [image-tag]}"
IMAGE_TAG="${2:-latest}"
IMAGE_NAME="sensor-simulator"
FULL_IMAGE="${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Building image: ${FULL_IMAGE}"
docker build \
  --platform linux/amd64 \
  --tag "${FULL_IMAGE}" \
  "${SCRIPT_DIR}"

echo "==> Pushing image: ${FULL_IMAGE}"
docker push "${FULL_IMAGE}"

echo "==> Done. Image available at: ${FULL_IMAGE}"
