# Protocol Buffers

This directory contains Protocol Buffer (protobuf) definitions for the Virtual Test Harness microservices.

## Proto Files

- **sensor.proto**: Defines sensor data structures and SensorService
- **fusion.proto**: Defines sensor fusion data structures and FusionService

## Generating Code

### Python
```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. sensor.proto fusion.proto
```

### Go
```bash
protoc --go_out=. --go_opt=paths=source_relative \
    --go-grpc_out=. --go-grpc_opt=paths=source_relative \
    sensor.proto fusion.proto
```

### JavaScript/TypeScript
```bash
protoc --js_out=import_style=commonjs:. \
    --grpc-web_out=import_style=typescript,mode=grpcwebtext:. \
    sensor.proto fusion.proto
```

## Usage

Include these proto files in your microservices to ensure consistent communication between services.

## Updating Protos

When updating proto files:
1. Make changes to the `.proto` files
2. Regenerate code for all languages used in your services
3. Update the microservices to use the new definitions
4. Test thoroughly to ensure compatibility
