.PHONY: run build test clean down generate-topics

# Default target
all: build run

# Run the local environment
run:
	docker-compose up -d

# Stop the local environment
down:
	docker-compose down

# Build the Docker image with the app
build:
	docker build -t rp-exporter .

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
	docker-compose down -v
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf tests/__pycache__
	rm -rf .pytest_cache
	rm -rf *.egg-info

# Help target
help:
	@echo "Available targets:"
	@echo "  run             - Start the local environment using docker-compose"
	@echo "  build           - Build the Docker image for the application"
	@echo "  test            - Run the test suite"
	@echo "  generate-topics - Generate test topics with random data and fills them"
	@echo "  install         - Install dependencies"
	@echo "  clean           - Remove containers, volumes and cache files"
	@echo "  down            - Stop the local environment"
	@echo "  all             - Build and run the application (default)"
	@echo "  help            - Show this help message"