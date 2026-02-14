# Services

This directory contains microservices for the Virtual Test Harness application.

## Structure

Each microservice should be in its own subdirectory with the following structure:

```
services/
├── <service-name>/
│   ├── src/
│   ├── tests/
│   ├── requirements.txt or package.json
│   ├── Dockerfile
│   └── README.md
```

## Example Microservices

To add a new microservice:

1. Create a new directory: `mkdir services/<service-name>`
2. Add your service code in `src/`
3. Add tests in `tests/`
4. Create a Dockerfile for containerization
5. Document your service in a README.md

## Communication

Microservices should communicate using the protocol buffers defined in the `protos/` directory at the root of this repository.
