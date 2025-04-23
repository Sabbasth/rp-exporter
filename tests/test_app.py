# pylint: disable=missing-docstring
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# fmt: off
from app import (RedpandaConsoleTopicCollector)  # pylint: disable=import-error,wrong-import-position
# fmt: on


class TestRedpandaConsoleTopicCollector(unittest.TestCase):
    @patch("app.requests.get")
    def test_collect_metrics(self, mock_get):
        # Mock the responses
        topics_response = MagicMock()
        topics_response.status_code = 200
        topics_response.json.return_value = [{"topicName": "test-topic"}]

        topic_details_response = MagicMock()
        topic_details_response.status_code = 200
        topic_details_response.json.return_value = {
            "topicName": "test-topic",
            "partitions": [
                {"id": 0, "logDirSummary": {"totalSizeBytes": 1024}},
                {"id": 1, "logDirSummary": {"totalSizeBytes": 2048}},
            ],
        }

        # Configure the mock to return different responses
        mock_get.side_effect = [topics_response, topic_details_response]

        # Create collector and run metrics collection
        collector = RedpandaConsoleTopicCollector("http://localhost:8080")

        # Mock the Gauge
        collector.topic_disk_usage = MagicMock()

        collector.collect_metrics()

        # Check that the metrics were updated correctly
        calls = collector.topic_disk_usage.labels.call_args_list
        self.assertEqual(len(calls), 2)

        # Check first partition
        _, kwargs = calls[0]
        self.assertEqual(kwargs, {"topic": "test-topic", "partition": "0"})
        collector.topic_disk_usage.labels().set.assert_any_call(1024)

        # Check second partition
        _, kwargs = calls[1]
        self.assertEqual(kwargs, {"topic": "test-topic", "partition": "1"})
        collector.topic_disk_usage.labels().set.assert_any_call(2048)


if __name__ == "__main__":
    unittest.main()
