#!/usr/bin/env python3
"""
Script to generate test topics in Kafka with random names, random partitions,
random replication factors, and fill them with random data.
"""

import json
import random
import string
import time
from kafka import KafkaAdminClient, KafkaProducer
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError

# Configuration
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
MAX_TOPICS = 4
MIN_PARTITIONS = 2
MAX_PARTITIONS = 10
MIN_REPLICATION = 1
MAX_REPLICATION = 1
MIN_MSG_SIZE_MB = 40
MAX_MSG_SIZE_MB = 80
MAX_RETENTION_SIZE_MB = 50


def generate_random_string(length=10):
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


def generate_random_data(size_kb):
    """Generate random data of specified size in KB."""
    random_data = generate_random_string(size_kb * 1024)
    return random_data.encode("utf-8")


def create_random_topics():
    """Create random topics with random partitions and replication factors."""
    admin_client = KafkaAdminClient(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

    num_topics = random.randint(1, MAX_TOPICS)
    topics = []

    print(f"Creating {num_topics} topics...")

    for _ in range(num_topics):
        topic_name = f"test-topic-{generate_random_string(5)}"
        num_partitions = random.randint(MIN_PARTITIONS, MAX_PARTITIONS)
        replication_factor = random.randint(MIN_REPLICATION, MAX_REPLICATION)

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
    finally:
        admin_client.close()

    return [topic.name for topic in topics]


def send_messages_to_topics(topic_names):
    """Send random messages to topics until they reach the desired size."""
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, value_serializer=lambda x: json.dumps(x).encode("utf-8")
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
            message = {
                "timestamp": time.time(),
                "id": generate_random_string(8),
                "data": generate_random_string(msg_size_kb),
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
    print(f"  - Max topics: {MAX_TOPICS}")
    print(f"  - Partitions: {MIN_PARTITIONS}-{MAX_PARTITIONS}")
    print(f"  - Replication factor: {MIN_REPLICATION}-{MAX_REPLICATION}")
    print(f"  - Message size per topic: {MIN_MSG_SIZE_MB}-{MAX_MSG_SIZE_MB} MB")
    print(f"  - Retention size: {MAX_RETENTION_SIZE_MB} MB")
    print()

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


if __name__ == "__main__":
    main()
