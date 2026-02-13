#!/bin/bash
# Setup local development environment

set -e

echo "Setting up development environment..."

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Install development tools
echo "Installing development tools..."
pip install pytest pytest-cov black flake8

# Check Terraform installation
if ! command -v terraform &> /dev/null; then
    echo "Warning: Terraform is not installed"
else
    echo "Terraform version: $(terraform version -json | jq -r '.terraform_version')"
fi

# Check Azure CLI installation
if ! command -v az &> /dev/null; then
    echo "Warning: Azure CLI is not installed"
else
    echo "Azure CLI version: $(az version -o json | jq -r '.\"azure-cli\"')"
fi

echo "Development environment setup complete!"
