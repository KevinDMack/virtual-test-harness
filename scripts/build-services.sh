#!/bin/bash
# Build all microservices

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICES_DIR="$SCRIPT_DIR/../services"

echo "Building microservices..."

# Iterate through each service directory
for service_dir in "$SERVICES_DIR"/*/ ; do
    if [ -d "$service_dir" ]; then
        service_name=$(basename "$service_dir")
        echo "Building service: $service_name"
        
        cd "$service_dir"
        
        # Build Docker image if Dockerfile exists
        if [ -f "Dockerfile" ]; then
            docker build -t "virtual-test-harness/$service_name:latest" .
        fi
    fi
done

echo "All services built successfully!"
