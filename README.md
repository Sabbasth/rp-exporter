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

This repository includes a Docker Compose setup to run the exporter with Redpanda Console, Prometheus, and Grafana.

### Environment Variables

You need to configure the environment variables to connect to your existing Redpanda cluster:

```bash
export REDPANDA_BROKERS=your-redpanda-host:9092
export REDPANDA_ADMIN_API_URLS=http://your-redpanda-host:9644
```

### Starting the Test Environment

Using the included Makefile:

```bash
# Start the environment
make run

# Build the Docker image
make build

# Run unit tests
make test

# Generate test topics and data
make generate-topics
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

- Redpanda Console: [http://localhost:8080](http://localhost:8080)
- Prometheus: [http://localhost:9090](http://localhost:9090)
- Grafana: [http://localhost:3000](http://localhost:3000) (admin/admin)
- Redpanda Exporter: [http://localhost:8000/metrics](http://localhost:8000/metrics)
- Kafka: localhost:9092

### Stopping the Environment

```bash
make down
```

Or:

```bash
docker-compose down
```
