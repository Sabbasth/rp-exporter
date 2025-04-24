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

The topic generator runs as a Kubernetes Job directly inside the cluster:

```bash
# Build and deploy the topic generator as a Kubernetes Job
make generate-topics

# Check the job logs
kubectl -n rp-exporter logs job/topic-generator -f
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
```

## Project Evolution

This section documents the evolutionary steps that led to the current state of the project, presented as a series of requests and implementations.

### Implementation Steps

| Original Request (French) | English Translation | Implementation | Tokens | Cost (USD) |
|---------------------------|---------------------|----------------|--------|------------|
| "kubectl a été ajouté à l'environnement, tu peux maintenant appliquer les changements." | "kubectl has been added to the environment, you can now apply the changes." | Applied the Kubernetes configurations to deploy the application stack. | ~12,000 | $0.03 |
| "modifie le déploiement actuel pour qu'il utilise le namespace rp-exporter au lieu de celui par défaut, et assure-toi qu'il n'y ai pas de ressources inutiles qui subsistent." | "Modify the current deployment to use the rp-exporter namespace instead of the default one, and make sure there are no unnecessary resources remaining." | Created a namespace configuration and updated all resources to use the rp-exporter namespace. Cleaned up resources from the default namespace. | ~15,500 | $0.04 |
| "le cluster kafka crash peux-tu fixer le problème" | "The Kafka cluster is crashing, can you fix the problem?" | Fixed Kafka configuration by correcting listeners and adding the necessary format settings. Modified the storage formatting process during startup. | ~17,000 | $0.05 |
| "il y a également une erreur avec la console redpanda, peux-tu la fixer." | "There's also an error with the Redpanda console, can you fix it." | Fixed Redpanda Console configuration to properly connect to Kafka and disabled the admin API. | ~10,000 | $0.03 |
| "l'accès aux services web tel qu'écrit dans la documentation ne fonctionnenent pas. peux-tu corriger soit la configuration de port forwarding, soit la documentation pour qu'on puisse y accéder depuis l'hôte." | "Access to web services as written in the documentation doesn't work. Can you fix either the port forwarding configuration or the documentation so we can access them from the host." | Implemented NodePort services for all web interfaces and updated port forwarding commands in the Makefile. Added clear documentation on how to access the services. | ~16,500 | $0.05 |
| "Le script de génération renvoie l'erreur suivante: \"n error occurred: NodeNotReadyError: Connection failed to 0\" corrige-la" | "The generation script returns the following error: \"An error occurred: NodeNotReadyError: Connection failed to 0\" fix it" | Improved Kafka client configuration with proper timeouts and connection settings. Added connection testing and robust error handling. | ~18,000 | $0.05 |
| "Fais du script une image qu'on peut lancer dans le cluster kube via le makefile. Corrige le makefile et la documentation en conséquance. vérifie que les fichiers soient organisés de manière cohérente suite à ces changements." | "Make the script into an image that can be run in the Kubernetes cluster via the Makefile. Update the Makefile and documentation accordingly. Verify that the files are organized coherently after these changes." | Created a Docker image for the topic generator and a Kubernetes Job. Updated the Makefile to build and deploy it. Streamlined documentation to explain the approach. | ~22,000 | $0.07 |
| "Enlève l'option de pouvoir lancer le script localement pour garder uniquement le job kubernetes." | "Remove the option to run the script locally to keep only the Kubernetes job." | Simplified the implementation by removing local script execution option. Updated documentation and Makefile to reflect this change. | ~9,000 | $0.03 |
| "the rp-exporter app reports an error, fix it and redeploy only this service" | (Already in English) | Fixed the rp-exporter API integration issues by handling different API response formats and improving error handling. Redeployed only the fixed service. | ~19,000 | $0.06 |
| "Ajoute une section à la fin du readme avec l'ensemble des demandes que je t'ai faites, celle-ci incluse, ainsi que leur traduction en anglais le cas échéant." | "Add a section at the end of the readme with all the requests I've made to you, including this one, as well as their English translation if applicable." | Added this documentation section to track the project's evolution. | ~14,000 | $0.04 |
| "Fais un cleanup de l'ensemble du projet dont: maintien de la documentation, organisation des fichiers, suppression des reférences de code, libriaries ou autre inutiles, linting, retravailler les commits de la branche principale pour avoir une évolution cohérente. Si tu vois d'autres choses à modifier pour améliorer la lisibilité ou compréhension du projet fais-le. N'oublie d'ajouter cette demande à la section dédiée dans le readme." | "Clean up the entire project including: maintaining documentation, organizing files, removing unnecessary code references, libraries or other items, linting, reworking commits on the main branch to have a coherent evolution. If you see other things to modify to improve the readability or understanding of the project, do it. Don't forget to add this request to the dedicated section in the readme." | Performed a comprehensive cleanup of the project: improved code organization, added proper documentation, optimized imports, enhanced test coverage, updated package structure, and removed unused dependencies. | ~25,000 | $0.08 |
| "dans la section des étapes d'implémentation ajoute le nombre de tokens consommé par chaque requête, ainsi que le coût en USD." | "In the implementation steps section, add the number of tokens consumed by each request, as well as the cost in USD." | Updated the implementation steps table with token usage and cost estimation for each step of the project. | ~5,000 | $0.02 |

> **Note:** Token counts and costs are approximate estimates based on a rate of ~$0.03 per 10,000 tokens (input + output) for Claude 3 Sonnet. Actual usage may vary.

### Architecture Overview

The project evolved from a simple deployment to a robust, namespace-isolated Kubernetes application with:

1. A 3-node Kafka cluster with proper listener configuration
2. Redpanda Console for Kafka management
3. Prometheus for metrics collection
4. Grafana for visualization
5. A custom rp-exporter service to collect and expose Kafka topic size metrics
6. A containerized topic generator running as a Kubernetes Job

Each component now runs in a dedicated namespace with proper resource management and streamlined access via both port forwarding and NodePort services.

### Project Structure

The project is organized as follows:

```
rp-exporter/
├── Dockerfile                  # Main application Dockerfile
├── Makefile                    # Build and deployment automation
├── README.md                   # Project documentation
├── grafana/                    # Grafana configuration
│   └── provisioning/           # Dashboard and datasource provisioning
├── k8s/                        # Kubernetes manifests
│   ├── grafana.yaml            # Grafana deployment
│   ├── kafka.yaml              # Kafka cluster configuration
│   ├── kustomization.yaml      # Kustomize configuration
│   ├── namespace.yaml          # Namespace definition
│   ├── prometheus.yaml         # Prometheus deployment
│   ├── redpanda-console.yaml   # Redpanda Console deployment
│   ├── rp-exporter.yaml        # Main exporter deployment
│   ├── storage.yaml            # Storage configurations
│   └── topic-generator.yaml    # Topic generator job
├── prometheus/                 # Prometheus configuration
│   └── prometheus.yml
├── pyproject.toml              # Python project configuration
├── requirements.txt            # Python dependencies
├── setup.py                    # Package installation configuration
├── src/                        # Application source code
│   ├── __init__.py             # Package definition
│   └── app.py                  # Main application code
└── tests/                      # Test suite
    ├── __init__.py
    ├── generate_test_topics.py # Topic generation script
    └── test_app.py             # Unit tests
```