# Infrastructure

This directory contains Terraform configurations for deploying the Virtual Test Harness infrastructure on Azure.

## Components

- **AKS (Azure Kubernetes Service)**: Container orchestration platform for running microservices
- **AI Foundry**: Azure Cognitive Services for AI capabilities
- **Application Insights**: Monitoring and telemetry
- **Storage Account**: Storage for AI Foundry data

## Usage

### Prerequisites

- Azure CLI installed and authenticated
- Terraform installed (>= 1.0)

### Deploy

1. Initialize Terraform:
   ```bash
   terraform init
   ```

2. Review the plan:
   ```bash
   terraform plan
   ```

3. Apply the configuration:
   ```bash
   terraform apply
   ```

### Variables

See `variables.tf` for available configuration options. You can override defaults by creating a `terraform.tfvars` file.

### Outputs

After deployment, Terraform will output:
- Resource group name
- AKS cluster name and configuration
- AI Foundry endpoint and keys
- Application Insights connection string
