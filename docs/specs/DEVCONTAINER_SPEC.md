# DevContainer Specification

## Overview

This document specifies the development container requirements for the TTRPG Game Notes project. All development should occur within the defined devcontainer to ensure consistency across development environments.

## Purpose

The devcontainer ensures:
- Consistent development environment across all contributors
- All required tools and dependencies are pre-installed
- Proper configuration for IDE features and extensions
- Simplified onboarding for new developers
- Reproducible builds and tests

## Base Image Requirements

### Container Base
- **Base Image:** `mcr.microsoft.com/devcontainers/dotnet:1-10.0`
- **Rationale:** Official Microsoft .NET devcontainer with .NET 10.0 SDK (preview)
- **Platform:** Linux-based (compatible with Docker and GitHub Codespaces)

### Workspace Configuration
- **Workspace Folder:** `/workspaces/ttrpg-game-notes`
- **Remote User:** `root` (required for system-level tool installations)
- **Port Forwarding:** Ports 5000 (HTTP), 5001 (HTTPS), 5263 (Function App)

## Required System Tools

### Core Development Tools

1. **Git** (via devcontainers feature)
   - Version control for source code
   - Feature: `ghcr.io/devcontainers/features/git:1`

2. **Docker-in-Docker** (via devcontainers feature)
   - Container building and testing within devcontainer
   - Feature: `ghcr.io/devcontainers/features/docker-in-docker:2`

3. **Azure CLI** (via devcontainers feature)
   - Azure resource management and deployment
   - Feature: `ghcr.io/devcontainers/features/azure-cli:1`

4. **Terraform** (via devcontainers feature)
   - Infrastructure as Code deployment
   - Version: `latest`
   - Feature: `ghcr.io/devcontainers/features/terraform:1`

5. **Go** (via devcontainers feature)
   - Required for Terratest infrastructure tests
   - Version: `latest`
   - Feature: `ghcr.io/devcontainers/features/go:1`

### Additional Required Tools

1. **SQLite3**
   - Local database testing and development
   - Installation: `apt-get install sqlite3`

2. **dotnet-ef (Entity Framework Core CLI)**
   - Database migrations and scaffolding
   - Version: `10.0.*` (must match .NET SDK version)
   - Installation: `dotnet tool install --global dotnet-ef --version 10.0.*`

3. **Azure Functions Core Tools**
   - Local Azure Functions development and testing
   - Version: `4.x` (latest v4)
   - Installation: `npm install -g azure-functions-core-tools@4 --unsafe-perm true`

4. **Node.js and npm**
   - JavaScript tooling and Playwright UI tests
   - Included in base image

## Required VS Code Extensions

All developers must have the following extensions installed:

### C# Development
- **ms-dotnettools.csharp** - C# language support and IntelliSense
- **ms-dotnettools.vscode-dotnet-runtime** - .NET runtime management

### Database
- **ms-mssql.mssql** - SQL Server connection and query tools

### Code Quality
- **streetsidesoftware.code-spell-checker** - Spell checking for code and comments

### Azure
- **ms-azuretools.vscode-docker** - Docker integration
- **ms-azuretools.vscode-azureresourcegroups** - Azure resource management

### Infrastructure as Code
- **hashicorp.terraform** - Terraform language support and validation

### Version Control
- **eamodio.gitlens** - Enhanced Git capabilities

### Go Development
- **golang.go** - Go language support (for Terratest)

## Required VS Code Settings

### C# Formatting
```json
{
  "omnisharp.enableEditorConfigSupport": true,
  "omnisharp.enableRoslynAnalyzers": true,
  "[csharp]": {
    "editor.defaultFormatter": "ms-dotnettools.csharp",
    "editor.formatOnSave": true
  }
}
```

**Rationale:**
- Enforces consistent code formatting using EditorConfig
- Enables Roslyn analyzers for code quality
- Automatically formats C# files on save

## Post-Create Command

Upon container creation, the following command must execute:
```bash
cd web-app && dotnet restore && dotnet build
```

**Purpose:**
- Restore NuGet packages for the web application
- Perform initial build to verify environment setup
- Cache dependencies for faster subsequent builds

## Environment Variables

### PATH Additions
```bash
PATH="${PATH}:/root/.dotnet/tools"
```

**Purpose:** Make globally installed .NET tools accessible from any directory

## Maintenance Requirements

### Version Updates
- Review and update base image version quarterly
- Update .NET SDK version when new stable releases are available
- Keep Azure Functions Core Tools at latest v4.x release
- Update Terraform to latest stable version

### Extension Updates
- Review VS Code extension updates monthly
- Test compatibility before requiring new extensions
- Remove deprecated or unused extensions

### Security
- Scan base image for security vulnerabilities monthly
- Update system packages regularly via `apt-get update && apt-get upgrade`
- Review and rotate any development credentials

## Verification Checklist

Before committing devcontainer changes, verify:

- [ ] Container builds successfully
- [ ] All extensions install without errors
- [ ] Post-create command completes successfully
- [ ] dotnet CLI is accessible and correct version
- [ ] Azure CLI is accessible
- [ ] Terraform CLI is accessible
- [ ] Go toolchain is accessible
- [ ] dotnet-ef tool is accessible
- [ ] Azure Functions Core Tools (func) is accessible
- [ ] Port forwarding works for all specified ports
- [ ] C# IntelliSense and formatting work
- [ ] Database connection tools work
- [ ] Git operations work within container

## Troubleshooting

### Common Issues

**Issue:** dotnet-ef not found
**Solution:** Verify PATH includes `/root/.dotnet/tools` and tool was installed globally

**Issue:** Azure Functions Core Tools installation fails
**Solution:** Ensure npm installation uses `--unsafe-perm true` flag when running as root

**Issue:** Extensions not loading
**Solution:** Rebuild container to refresh extension installations

**Issue:** Port forwarding not working
**Solution:** Verify ports are not in use on host machine, check firewall settings

## References

- [DevContainer Specification](https://containers.dev/)
- [.NET DevContainers](https://github.com/devcontainers/images/tree/main/src/dotnet)
- [DevContainer Features](https://containers.dev/features)
- [VS Code DevContainers](https://code.visualstudio.com/docs/devcontainers/containers)

## Change History

- 2026-02-13: Initial specification created