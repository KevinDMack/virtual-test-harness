# example-service

A minimal example microservice for the Virtual Test Harness.

## Structure

```
example-service/
├── src/
│   └── main.py
└── Dockerfile
```

## Running locally

```bash
docker build -t virtual-test-harness/example-service:latest .
docker run --rm virtual-test-harness/example-service:latest
```
