# Virtual Test Harness Helm Chart

This Helm chart deploys the Virtual Test Harness microservices to a Kubernetes cluster.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- Azure Kubernetes Service (AKS) cluster

## Installing the Chart

To install the chart with the release name `my-release`:

```bash
helm install my-release ./helm
```

## Uninstalling the Chart

To uninstall/delete the `my-release` deployment:

```bash
helm uninstall my-release
```

## Configuration

The following table lists the configurable parameters of the Virtual Test Harness chart and their default values.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Image repository | `virtual-test-harness` |
| `image.tag` | Image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.port` | Service port | `80` |
| `aiFoundry.enabled` | Enable AI Foundry integration | `true` |
| `aiFoundry.endpoint` | AI Foundry endpoint URL | `""` |
| `applicationInsights.enabled` | Enable Application Insights | `true` |

Specify each parameter using the `--set key=value[,key=value]` argument to `helm install`. For example:

```bash
helm install my-release ./helm --set replicaCount=3
```

Alternatively, a YAML file that specifies the values for the parameters can be provided:

```bash
helm install my-release ./helm -f values.yaml
```

## AI Foundry and Application Insights

To use AI Foundry and Application Insights, you need to create Kubernetes secrets with the necessary credentials:

```bash
# Create AI Foundry secret
kubectl create secret generic ai-foundry-key --from-literal=key=<your-key>

# Create Application Insights secret
kubectl create secret generic app-insights-connection --from-literal=connectionString=<your-connection-string>
```
