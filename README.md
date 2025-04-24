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

This repository includes deployment configurations for both Kubernetes and Docker Compose to run the exporter with Redpanda Console, Prometheus, and Grafana.

### Environment Variables

You need to configure the environment variables to connect to your existing Redpanda cluster:

```bash
export REDPANDA_BROKERS=your-redpanda-host:9092
export REDPANDA_ADMIN_API_URLS=http://your-redpanda-host:9644
```

### Running on Kubernetes (Default)

By default, the Makefile is configured to deploy to a local Kubernetes cluster (Minikube, Kind, or Docker Desktop).

#### Prerequisites

- A running Kubernetes cluster (Minikube, Kind, or Docker Desktop)
- kubectl configured to communicate with your cluster
- Docker installed

#### Starting on Kubernetes

```bash
# Build image and deploy to Kubernetes
make run

# Build the Docker image only
make build

# Apply Kubernetes manifests
make k8s-apply

# Forward ports to access services locally
make k8s-port-forward

# Restart a specific service
make restart-service SERVICE=rp-exporter
```

#### Stopping the Kubernetes Environment

```bash
make down
# or
make k8s-delete
```

### Running with Docker Compose

You can switch to Docker Compose mode by setting the `DOCKER=1` environment variable.

```bash
# Start with Docker Compose
make run DOCKER=1

# Stop Docker Compose environment
make down DOCKER=1

# Restart a specific service
make restart-service SERVICE=rp-exporter DOCKER=1
```

Or using Docker Compose directly:

```bash
docker-compose up -d
```

### Generating Test Data

The repository includes a script to generate test topics with random data. This is useful for testing the exporter and visualizing metrics in Grafana.

The script creates:

- Up to 4 topics with random names
- Between 2-10 partitions per topic
- Replication factor between 1-3
- Each topic is filled with 40-80 MB of random data
- Topics have a retention size of 50 MB

To run the script:

```bash
make generate-topics
```

Or directly:

```bash
python tests/generate_test_topics.py
```

### Available Services

When port forwarding is set up with `make k8s-port-forward` or when running Docker Compose, the following services are available:

- Redpanda Console: [http://localhost:8080](http://localhost:8080)
- Prometheus: [http://localhost:9090](http://localhost:9090)
- Grafana: [http://localhost:3000](http://localhost:3000) (admin/admin)
- Redpanda Exporter: [http://localhost:8000/metrics](http://localhost:8000/metrics)
- Kafka: localhost:9092

### Makefile Options

The Makefile supports the following options:

- `DOCKER=1` - Use Docker Compose instead of Kubernetes
- `SERVICE=name` - Specify service name for restart operations
- `NAMESPACE=name` - Kubernetes namespace (default: rp-exporter)

For a complete list of available commands:

```bash
make help
```
