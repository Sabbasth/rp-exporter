# Redpanda Console Exporter

A Prometheus exporter for Redpanda disk usage metrics per topic, using the Redpanda Console API.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python src/app.py --console-url http://redpanda-console:8080 --port 8000
```

## Metrics

- `redpanda_topic_disk_usage_bytes`: Disk usage in bytes per topic

## Test Environment

This repository includes deployment configurations for Kubernetes to run the exporter with Redpanda Console, Prometheus, and Grafana locally.

### Environment Variables

You need to configure the environment variables to connect to your existing Redpanda cluster:

```bash
export REDPANDA_BROKERS=your-redpanda-host:9092
export REDPANDA_ADMIN_API_URLS=http://your-redpanda-host:9644
```

### Running on Kubernetes

The application is designed to run on a local Kubernetes cluster (Minikube, Kind, or Docker Desktop).

#### Prerequisites

- A running Kubernetes cluster (Minikube, Kind, or Docker Desktop)
- kubectl configured to communicate with your cluster
- Docker installed

#### Starting the Environment

```bash
# Build image and deploy to Kubernetes
make run

# Build the Docker image only
make build

# Apply Kubernetes manifests
make apply

# Forward ports to access services locally
# Keep this command running in a terminal
make port-forward

# In another terminal, restart a specific service if needed
make restart-service SERVICE=rp-exporter
# Other services: grafana, kafka, prometheus, redpanda-console
```

#### Stopping the Environment

```bash
make down
# or
make delete
```

### Generating Test Data

The repository includes a script to generate test topics with random data. This is useful for testing the exporter and visualizing metrics in Grafana.

The script creates:

- Up to 4 topics with random names
- A configurable number of partitions per topic
- Configurable replication factor
- Each topic is filled with test data
- Topics have a retention size of 50 MB

To run the script, you have two options:

**Option 1: Run as a Kubernetes Job (Recommended)**

This runs the topic generator directly inside the Kubernetes cluster, without requiring port forwarding:

```bash
# Build and deploy the topic generator as a Kubernetes Job
make generate-topics

# Check the job logs
kubectl -n rp-exporter logs job/topic-generator -f
```

**Option 2: Run locally with port forwarding**

This requires you to have port forwarding active:

```bash
# In one terminal, start port forwarding
make port-forward

# In another terminal, run the local generator script
make generate-topics-local
```

### Available Services

The services are available in two ways:

**Option 1: Using Port Forwarding (Recommended)**

When port forwarding is set up with `make port-forward`, the following services are available:

- Redpanda Console: [http://localhost:8080](http://localhost:8080)
- Prometheus: [http://localhost:9090](http://localhost:9090)
- Grafana: [http://localhost:3000](http://localhost:3000) (admin/admin)
- Redpanda Exporter: [http://localhost:8000/metrics](http://localhost:8000/metrics)
- Kafka: localhost:9092

> **Note:** To access these services from your host machine, run `make port-forward` in a terminal and keep it running. This command establishes port forwarding from your Kubernetes services to your localhost. Press Ctrl+C to stop port forwarding when done.

**Option 2: Using NodePort Services**

Alternatively, the services are also exposed via NodePort:

- Redpanda Console: http://localhost:30808
- Prometheus: http://localhost:30909
- Grafana: http://localhost:30300 (admin/admin)
- Redpanda Exporter: http://localhost:30800/metrics

### Makefile Options

The Makefile supports the following options:

- `SERVICE=name` - Specify service name for restart operations
- `NAMESPACE=name` - Kubernetes namespace (default: rp-exporter)

For a complete list of available commands:

```bash
make help
```

Key commands include:

```bash
# Build all Docker images
make build-all

# Build only the main application
make build

# Build only the topic generator
make build-topic-generator

# Apply all Kubernetes manifests with both images
make apply

# Generate test topics inside the cluster
make generate-topics

# Generate test topics locally (requires port-forwarding)
make generate-topics-local
```
