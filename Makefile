SERVICE ?= none
NAMESPACE ?= rp-exporter
.PHONY: run build test clean down generate-topics restart-service k8s-setup k8s-apply k8s-delete k8s-port-forward k8s-restart

# Default target
all: build run

# Docker Compose Operations
# -------------------------

# Run the local environment with Docker Compose
run-docker:
	docker-compose up -d

# Stop the Docker Compose environment
down-docker:
	docker-compose down

# Restart a specific service in Docker Compose
restart-service-docker:
	@if [ -z "$(SERVICE)" ] || [ "$(SERVICE)" = "none" ]; then \
		echo "Usage: make restart-service-docker SERVICE=<service-name>"; \
		echo "Available services: rp-exporter, broker, redpanda-console, prometheus, grafana"; \
		exit 1; \
	fi
	docker-compose restart $(SERVICE)

# Kubernetes Operations
# --------------------

# Create the namespace if it doesn't exist
k8s-setup:
	kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -

# Apply Kubernetes manifests
k8s-apply: k8s-setup build k8s-load-image
	kubectl apply -k k8s -n $(NAMESPACE)

# Delete all resources in the namespace
k8s-delete:
	kubectl delete -k k8s -n $(NAMESPACE)

# Load the locally built Docker image into kind/minikube (if using local k8s)
k8s-load-image:
	@if command -v minikube >/dev/null 2>&1; then \
		echo "Loading image into Minikube..."; \
		minikube image load rp-exporter:latest; \
	elif command -v kind >/dev/null 2>&1; then \
		echo "Loading image into Kind..."; \
		kind load docker-image rp-exporter:latest; \
	else \
		echo "Neither Minikube nor Kind detected. Skipping image load."; \
	fi

# Port forward Kubernetes services to localhost
k8s-port-forward:
	@echo "Starting port forwarding for services..."
	@echo "Press Ctrl+C to stop."
	@kubectl -n $(NAMESPACE) port-forward svc/redpanda-console 8080:8080 & \
	kubectl -n $(NAMESPACE) port-forward svc/prometheus 9090:9090 & \
	kubectl -n $(NAMESPACE) port-forward svc/grafana 3000:3000 & \
	kubectl -n $(NAMESPACE) port-forward svc/rp-exporter 8000:8000 & \
	kubectl -n $(NAMESPACE) port-forward svc/broker 9092:9092 & \
	wait

# Restart a service in Kubernetes
k8s-restart:
	@if [ -z "$(SERVICE)" ] || [ "$(SERVICE)" = "none" ]; then \
		echo "Usage: make k8s-restart SERVICE=<service-name>"; \
		echo "Available services: rp-exporter, broker, redpanda-console, prometheus, grafana"; \
		exit 1; \
	fi
	kubectl -n $(NAMESPACE) rollout restart deployment/$(SERVICE)

# Common Operations
# ----------------

# Run the local environment (defaults to Kubernetes, override with DOCKER=1)
run:
	@if [ "$(DOCKER)" = "1" ]; then \
		$(MAKE) run-docker; \
	else \
		$(MAKE) k8s-apply; \
	fi

# Stop the local environment
down:
	@if [ "$(DOCKER)" = "1" ]; then \
		$(MAKE) down-docker; \
	else \
		$(MAKE) k8s-delete; \
	fi

# Restart a specific service
restart-service:
	@if [ -z "$(SERVICE)" ] || [ "$(SERVICE)" = "none" ]; then \
		echo "Usage: make restart-service SERVICE=<service-name>"; \
		echo "Available services: rp-exporter, broker, redpanda-console, prometheus, grafana"; \
		exit 1; \
	fi
	@if [ "$(DOCKER)" = "1" ]; then \
		$(MAKE) restart-service-docker SERVICE=$(SERVICE); \
	else \
		$(MAKE) k8s-restart SERVICE=$(SERVICE); \
	fi

# Build the Docker image with the app
build:
	docker build -t rp-exporter:latest .

# Run tests
test:
	python -m pytest -v tests/

# Generate test topics with random data
generate-topics:
	python tests/generate_test_topics.py

# Install dependencies
install:
	pip install -r requirements.txt
	pip install -e .

# Clean up
clean:
	@if [ "$(DOCKER)" = "1" ]; then \
		docker-compose down -v; \
	else \
		$(MAKE) k8s-delete; \
	fi
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf tests/__pycache__
	rm -rf .pytest_cache
	rm -rf *.egg-info

# Help target
help:
	@echo "Available targets:"
	@echo ""
	@echo "Kubernetes Mode (default):"
	@echo "  run             - Deploy to Kubernetes cluster (calls k8s-apply)"
	@echo "  down            - Remove Kubernetes deployments (calls k8s-delete)"
	@echo "  k8s-setup       - Create namespace for the application"
	@echo "  k8s-apply       - Apply all Kubernetes manifests"
	@echo "  k8s-delete      - Delete all resources from Kubernetes"
	@echo "  k8s-port-forward - Forward Kubernetes service ports to localhost"
	@echo "  k8s-restart     - Restart a specific Kubernetes deployment (use SERVICE=name)"
	@echo "  k8s-load-image  - Load the local Docker image into minikube/kind"
	@echo ""
	@echo "Docker Compose Mode (use DOCKER=1):"
	@echo "  run-docker      - Start with Docker Compose"
	@echo "  down-docker     - Stop Docker Compose environment"
	@echo "  restart-service-docker - Restart a specific Docker service (use SERVICE=name)"
	@echo ""
	@echo "Common:"
	@echo "  build           - Build the Docker image for the application"
	@echo "  test            - Run the test suite"
	@echo "  generate-topics - Generate test topics with random data and fills them"
	@echo "  install         - Install dependencies"
	@echo "  restart-service - Restart a service (works with both Docker and K8s)"
	@echo "  clean           - Remove containers, volumes and cache files"
	@echo "  all             - Build and run the application (default)"
	@echo "  help            - Show this help message"
	@echo ""
	@echo "Options:"
	@echo "  DOCKER=1        - Use Docker Compose instead of Kubernetes"
	@echo "  SERVICE=name    - Specify service name for restart operations"
	@echo "  NAMESPACE=name  - Kubernetes namespace (default: rp-exporter)"