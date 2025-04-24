#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import time
import requests
from prometheus_client import start_http_server, Gauge

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("redpanda-exporter")


class RedpandaConsoleTopicCollector:
    def __init__(self, redpanda_console_url):
        self.redpanda_console_url = redpanda_console_url
        self.topic_disk_usage = Gauge(
            "redpanda_topic_disk_usage_bytes", "Disk usage in bytes per topic", ["topic"]
        )

    def collect_metrics(self):
        try:
            # Fetch topic list with data
            topics_response = requests.get(f"{self.redpanda_console_url}/api/topics", timeout=10)
            if topics_response.status_code != 200:
                logger.error(f"Failed to fetch topics: {topics_response.status_code}")
                return

            # Parse the response
            response_data = topics_response.json()
            
            # Check if response is a dictionary with 'topics' key
            if isinstance(response_data, dict) and 'topics' in response_data:
                topics = response_data['topics']
            else:
                # Assume the response is a list of topics directly
                topics = response_data

            # For each topic, get partition sizes
            for topic in topics:
                # Skip if not a dictionary or doesn't have a topic name
                if not isinstance(topic, dict):
                    logger.warning(f"Unexpected topic format: {topic}")
                    continue
                
                topic_name = topic.get("topicName")
                if not topic_name:
                    logger.warning("Topic without a name found, skipping")
                    continue

                # Get total size - directly from the topic object if available
                size_bytes = 0
                if "logDirSummary" in topic and "totalSizeBytes" in topic["logDirSummary"]:
                    size_bytes = topic["logDirSummary"]["totalSizeBytes"]
                    
                # Update the metric for the whole topic
                self.topic_disk_usage.labels(topic=topic_name).set(size_bytes)
                logger.info(f"Set metric for topic {topic_name}: {size_bytes} bytes")

            logger.info("Metrics collected successfully")
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")


def parse_args():
    parser = argparse.ArgumentParser(description="Redpanda Console Prometheus Exporter")
    parser.add_argument(
        "--console-url", type=str, required=True, help="URL of the Redpanda Console (e.g., http://localhost:8080)"
    )
    parser.add_argument("--port", type=int, default=8000, help="Port on which the exporter HTTP server will listen")
    parser.add_argument("--interval", type=int, default=30, help="Interval in seconds between metrics collection")
    return parser.parse_args()


def main():
    args = parse_args()
    logger.info(f"Starting Redpanda exporter with Redpanda Console URL: {args.console_url}")

    # Start up the server to expose the metrics
    start_http_server(args.port)
    logger.info(f"Metrics server started on port {args.port}")

    # Create collector
    collector = RedpandaConsoleTopicCollector(args.console_url)

    # Collect metrics at regular intervals
    while True:
        collector.collect_metrics()
        time.sleep(args.interval)


if __name__ == "__main__":
    main()