SERVICE ?= none
NAMESPACE ?= rp-exporter
.PHONY: run build test clean down generate-topics restart-service setup apply delete port-forward

# Default target
all: build run

# Create the namespace if it doesn't exist
setup:
	kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -

# Apply Kubernetes manifests
apply: setup build load-image
	kubectl apply -k k8s -n $(NAMESPACE)

# Delete all resources in the namespace
delete:
	kubectl delete -k k8s -n $(NAMESPACE)

# Load the locally built Docker image into kind/minikube
load-image:
	@if command -v minikube >/dev/null 2>&1; then \
		echo "Loading image into Minikube..."; \
		minikube image load rp-exporter:latest; \
	elif command -v kind >/dev/null 2>&1; then \
		echo "Loading image into Kind..."; \
		kind load docker-image rp-exporter:latest; \
	elif command -v docker >/dev/null 2>&1 && docker info 2>/dev/null | grep -q "Kubernetes"; then \
		echo "Docker Desktop with Kubernetes detected. Image will be available automatically."; \
	elif command -v kubectl >/dev/null 2>&1 && kubectl config current-context | grep -q "rancher-desktop"; then \
		echo "Rancher Desktop detected. Image will be available automatically."; \
	else \
		echo "No recognized Kubernetes environment detected. Skipping image load."; \
	fi

# Port forward Kubernetes services to localhost
port-forward:
	@echo "Starting port forwarding for services..."
	@echo "Press Ctrl+C to stop."
	@kubectl -n $(NAMESPACE) port-forward svc/redpanda-console 8080:8080 & \
	kubectl -n $(NAMESPACE) port-forward svc/prometheus 9090:9090 & \
	kubectl -n $(NAMESPACE) port-forward svc/grafana 3000:3000 & \
	kubectl -n $(NAMESPACE) port-forward svc/rp-exporter 8000:8000 & \
	kubectl -n $(NAMESPACE) port-forward svc/kafka 9092:9092 & \
	wait

# Restart a service in Kubernetes
restart-service:
	@if [ -z "$(SERVICE)" ] || [ "$(SERVICE)" = "none" ]; then \
		echo "Usage: make restart-service SERVICE=<service-name>"; \
		echo "Available services: rp-exporter, kafka, redpanda-console, prometheus, grafana"; \
		exit 1; \
	fi
	@if [ "$(SERVICE)" = "kafka" ]; then \
		kubectl -n $(NAMESPACE) rollout restart statefulset/kafka; \
	else \
		kubectl -n $(NAMESPACE) rollout restart deployment/$(SERVICE); \
	fi

# Run the local environment
run: apply

# Stop the local environment
down: delete

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
clean: delete
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf tests/__pycache__
	rm -rf .pytest_cache
	rm -rf *.egg-info

# Help target
help:
	@echo "Available targets:"
	@echo ""
	@echo "Kubernetes operations:"
	@echo "  run             - Deploy to Kubernetes cluster (calls apply)"
	@echo "  down            - Remove Kubernetes deployments (calls delete)"
	@echo "  setup           - Create namespace for the application"
	@echo "  apply           - Apply all Kubernetes manifests"
	@echo "  delete          - Delete all resources from Kubernetes"
	@echo "  port-forward    - Forward Kubernetes service ports to localhost"
	@echo "  restart-service - Restart a specific Kubernetes deployment (use SERVICE=name)"
	@echo "  load-image      - Load the local Docker image into minikube/kind"
	@echo ""
	@echo "Common:"
	@echo "  build           - Build the Docker image for the application"
	@echo "  test            - Run the test suite"
	@echo "  generate-topics - Generate test topics with random data and fills them"
	@echo "  install         - Install dependencies"
	@echo "  clean           - Remove resources and clean cache files"
	@echo "  all             - Build and run the application (default)"
	@echo "  help            - Show this help message"
	@echo ""
	@echo "Options:"
	@echo "  SERVICE=name    - Specify service name for restart operations"
	@echo "  NAMESPACE=name  - Kubernetes namespace (default: rp-exporter)"