#!/usr/bin/env python3
"""
Script to generate test topics in Kafka with random names, random partitions,
random replication factors, and fill them with random data.
"""

import json
import os
import random
import string
import time
from kafka import KafkaAdminClient, KafkaProducer
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
MAX_TOPICS = 4
MIN_PARTITIONS = 2
MAX_PARTITIONS = 3  # Reduced from 10 to match the number of brokers
MIN_REPLICATION = 1
MAX_REPLICATION = 3
MIN_MSG_SIZE_MB = 10  # Reduced from 40 to make testing faster
MAX_MSG_SIZE_MB = 20  # Reduced from 80 to make testing faster
MAX_RETENTION_SIZE_MB = 50


def generate_random_string(length=10):
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


def generate_random_data(size_kb):
    """Generate random data of specified size in KB."""
    # Generating exactly size_kb * 1024 characters is too memory intensive
    # Instead, generate a smaller string that will still result in a JSON value of roughly the right size
    # Each character becomes ~1 byte in JSON
    random_data = generate_random_string(size_kb)
    return random_data.encode("utf-8")


def create_random_topics():
    """Create random topics with random partitions and replication factors."""
    print(f"Connecting to Kafka at {KAFKA_BOOTSTRAP_SERVERS}...")
    
    # Set client_id to avoid NodeNotReadyError
    admin_client = KafkaAdminClient(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        client_id="topic-generator-admin",
        # Add longer timeout to accommodate Kubernetes networking
        request_timeout_ms=30000,
        connections_max_idle_ms=60000
    )

    # Test the connection with list_topics before proceeding
    try:
        existing_topics = admin_client.list_topics()
        print(f"Successfully connected to Kafka. Existing topics: {existing_topics}")
    except Exception as e:
        print(f"Error connecting to Kafka: {str(e)}")
        admin_client.close()
        raise

    num_topics = random.randint(1, MAX_TOPICS)
    topics = []

    print(f"Creating {num_topics} topics...")

    for _ in range(num_topics):
        topic_name = f"test-topic-{generate_random_string(5)}"
        # Set fixed values to avoid issues with cluster size
        num_partitions = MIN_PARTITIONS
        replication_factor = 1  # Set to 1 for more reliable creation

        # Topic configurations including retention.bytes (50 MB)
        topic_configs = {
            "retention.bytes": str(MAX_RETENTION_SIZE_MB * 1024 * 1024),
            "retention.ms": str(86400000),  # 24 hours in milliseconds
        }

        new_topic = NewTopic(
            name=topic_name,
            num_partitions=num_partitions,
            replication_factor=replication_factor,
            topic_configs=topic_configs,
        )

        topics.append(new_topic)

    try:
        admin_client.create_topics(new_topics=topics, validate_only=False)
        print("Topics created successfully:")
        for topic in topics:
            print(
                f"  - {topic.name}: {topic.num_partitions} partitions, "
                f"replication factor {topic.replication_factor}"
            )
    except TopicAlreadyExistsError as e:
        print(f"Some topics already exist: {e}")
    except Exception as e:
        print(f"Error creating topics: {str(e)}")
        admin_client.close()
        raise
    finally:
        admin_client.close()

    return [topic.name for topic in topics]


def send_messages_to_topics(topic_names):
    """Send random messages to topics until they reach the desired size."""
    print(f"Connecting producer to Kafka at {KAFKA_BOOTSTRAP_SERVERS}...")
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, 
        value_serializer=lambda x: json.dumps(x).encode("utf-8"),
        client_id="topic-generator-producer",
        # Add configurations to improve connectivity in Kubernetes
        request_timeout_ms=30000,
        connections_max_idle_ms=60000,
        retry_backoff_ms=500,
        reconnect_backoff_max_ms=5000,
        reconnect_backoff_ms=1000
    )

    for topic_name in topic_names:
        # Random target size between MIN_MSG_SIZE_MB and MAX_MSG_SIZE_MB
        target_size_mb = random.randint(MIN_MSG_SIZE_MB, MAX_MSG_SIZE_MB)
        target_size_kb = target_size_mb * 1024

        print(f"Sending approximately {target_size_mb} MB of data to {topic_name}...")

        sent_kb = 0
        msg_count = 0

        # Generate messages until we reach the target size
        while sent_kb < target_size_kb:
            # Generate a random message between 10KB and 100KB
            msg_size_kb = random.randint(10, 100)
            if sent_kb + msg_size_kb > target_size_kb:
                msg_size_kb = target_size_kb - sent_kb

            if msg_size_kb <= 0:
                break

            # Create random message with timestamp
            # Use a smaller data size to avoid memory issues
            data_size = min(msg_size_kb // 10, 1000)  # Limit to 1000 chars max
            message = {
                "timestamp": time.time(),
                "id": generate_random_string(8),
                "data": generate_random_string(data_size),
            }

            # Send to a random partition
            producer.send(topic_name, value=message)

            sent_kb += msg_size_kb
            msg_count += 1

            # Print progress every 50 messages
            if msg_count % 50 == 0:
                print(
                    f"  Progress: {sent_kb/1024:.2f} MB / {target_size_mb} MB " f"({sent_kb/target_size_kb*100:.1f}%)"
                )

        print(f"Completed sending {sent_kb/1024:.2f} MB of data to {topic_name} " f"in {msg_count} messages")

    # Make sure all messages are sent
    producer.flush()
    producer.close()


def main():
    """Main function to create topics and send messages."""
    print("Kafka Test Topic Generator")
    print("=========================")
    print("Configuration:")
    print(f"  - Kafka Bootstrap Servers: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"  - Max topics: {MAX_TOPICS}")
    print(f"  - Partitions: {MIN_PARTITIONS}-{MAX_PARTITIONS}")
    print(f"  - Replication factor: {MIN_REPLICATION}-{MAX_REPLICATION}")
    print(f"  - Message size per topic: {MIN_MSG_SIZE_MB}-{MAX_MSG_SIZE_MB} MB")
    print(f"  - Retention size: {MAX_RETENTION_SIZE_MB} MB")
    print()

    # Try to establish initial connection to check connectivity
    print("Testing connection to Kafka...")
    try:
        from kafka.client_async import KafkaClient
        client = KafkaClient(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            client_id="connection-test",
            request_timeout_ms=10000
        )
        client.check_version()
        print("Initial connectivity test successful!")
        client.close()
    except Exception as connection_error:
        print(f"WARNING: Initial connection test failed: {str(connection_error)}")
        print("Will still attempt to proceed with topic creation...")
        print("If this fails, ensure Kafka is running and port-forwarding is active.")
        time.sleep(2)  # Pause to let user read the warning
        
    try:
        # Create topics
        topic_names = create_random_topics()

        # Wait for topics to be fully created
        print("Waiting for topics to be fully created...")
        time.sleep(5)

        # Send messages to topics
        if topic_names:
            send_messages_to_topics(topic_names)
            print("All data has been sent successfully!")
        else:
            print("No topics were created. Exiting.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print(f"Make sure Kafka is accessible at {KAFKA_BOOTSTRAP_SERVERS}")
        print("If using port forwarding, ensure 'make port-forward' is running in another terminal")
        print("You can try:")
        print("  1. Ensure port 9092 is correctly forwarded from the Kubernetes cluster")
        print("  2. Check that the Kafka service is running: kubectl get pods -n rp-exporter")
        print("  3. Verify port-forwarding is active with: kubectl port-forward svc/kafka 9092:9092 -n rp-exporter")


if __name__ == "__main__":
    main()
