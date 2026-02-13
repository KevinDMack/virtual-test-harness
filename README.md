# Virtual Test Harness

A microservice framework for leveraging AI to simulate sensor output and sensor fusion.

## Overview

The Virtual Test Harness is a cloud-native application designed to simulate sensor data and sensor fusion using AI capabilities. It is built on a microservices architecture and deployed on Azure Kubernetes Service (AKS) with AI Foundry integration.

## Project Structure

```
.
├── infra/              # Terraform infrastructure as code for AKS and AI Foundry
├── services/           # Microservices directory (each service in its own subdirectory)
├── scripts/            # Bash scripts for deployment and development tasks
├── protos/             # Protocol buffer definitions for inter-service communication
├── helm/               # Helm chart for Kubernetes deployment
├── .devcontainer/      # Development container configuration
└── README.md           # This file
```

## Quick Start

### Prerequisites

- Docker Desktop with Kubernetes enabled, or access to an AKS cluster
- Azure CLI
- Terraform >= 1.0
- Helm >= 3.0
- Python >= 3.11

### Development Setup

1. **Using Dev Container (Recommended)**
   
   Open this repository in VS Code with the Dev Containers extension:
   ```bash
   code .
   ```
   VS Code will prompt you to reopen in the container, which includes all necessary tools.

2. **Manual Setup**
   
   Run the setup script:
   ```bash
   ./scripts/setup-dev.sh
   ```

### Infrastructure Deployment

1. Configure Azure credentials:
   ```bash
   az login
   ```

2. Deploy infrastructure:
   ```bash
   ./scripts/deploy-infra.sh
   ```

3. Get AKS credentials:
   ```bash
   az aks get-credentials --resource-group rg-virtual-test-harness --name aks-virtual-test-harness
   ```

### Application Deployment

1. Build services:
   ```bash
   ./scripts/build-services.sh
   ```

2. Deploy with Helm:
   ```bash
   helm install virtual-test-harness ./helm
   ```

## Components

### Infrastructure (`infra/`)

Terraform configurations for:
- Azure Kubernetes Service (AKS) cluster
- AI Foundry (Azure Cognitive Services)
- Application Insights for monitoring
- Storage Account for AI data

See [infra/README.md](infra/README.md) for details.

### Services (`services/`)

Microservices implementing the core functionality. Each service should:
- Use the protocol buffers defined in `protos/`
- Include its own Dockerfile
- Have comprehensive tests

See [services/README.md](services/README.md) for details.

### Protocol Buffers (`protos/`)

Defines the API contracts between services:
- `sensor.proto`: Sensor data structures and service
- `fusion.proto`: Sensor fusion data structures and service

See [protos/README.md](protos/README.md) for details.

### Helm Chart (`helm/`)

Kubernetes deployment configuration including:
- Deployments
- Services
- ConfigMaps and Secrets
- Ingress rules

See [helm/README.md](helm/README.md) for details.

### Scripts (`scripts/`)

Utility scripts for common tasks:
- `deploy-infra.sh`: Deploy Azure infrastructure
- `setup-dev.sh`: Setup development environment
- `build-services.sh`: Build all microservices

See [scripts/README.md](scripts/README.md) for details.

## Development

### Adding a New Microservice

1. Create a new directory in `services/`:
   ```bash
   mkdir services/my-service
   ```

2. Add your service code, tests, and Dockerfile

3. Update the Helm chart to include your service

4. Update protocol buffers if needed

### Testing

Run tests for a specific service:
```bash
cd services/my-service
pytest
```

### Local Development

Use the dev container for a consistent development environment with all tools pre-installed.

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request

## License

See [LICENSE](LICENSE) for details.
