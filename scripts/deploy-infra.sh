#!/bin/bash
# Deploy infrastructure using Terraform

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$SCRIPT_DIR/../infra"

echo "Deploying infrastructure..."

cd "$INFRA_DIR"

# Initialize Terraform
terraform init

# Plan the deployment
terraform plan -out=tfplan

# Apply the plan
terraform apply tfplan

# Save outputs
terraform output -json > outputs.json

echo "Infrastructure deployment complete!"
