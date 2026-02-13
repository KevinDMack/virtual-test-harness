# Scripts

This directory contains bash scripts for common tasks in the Virtual Test Harness project.

## Available Scripts

- **deploy-infra.sh**: Deploy Azure infrastructure using Terraform
- **setup-dev.sh**: Setup local development environment
- **build-services.sh**: Build all microservices Docker images

## Usage

Make scripts executable:
```bash
chmod +x scripts/*.sh
```

Run a script:
```bash
./scripts/<script-name>.sh
```

## Adding New Scripts

When adding new scripts:
1. Use proper error handling with `set -e`
2. Add descriptive comments
3. Make scripts executable: `chmod +x <script-name>.sh`
4. Document the script in this README
