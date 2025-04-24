"""
Unit tests for the RedpandaConsoleTopicCollector class.
"""
import unittest
from unittest.mock import patch, MagicMock

# Import from the package
from src.app import RedpandaConsoleTopicCollector


class TestRedpandaConsoleTopicCollector(unittest.TestCase):
    """Test cases for the RedpandaConsoleTopicCollector class."""

    @patch("src.app.requests.get")
    def test_collect_metrics(self, mock_get):
        """Test that metrics are collected correctly from the API response."""
        # Mock the response for topic list
        topics_response = MagicMock()
        topics_response.status_code = 200
        topics_response.json.return_value = {"topics": [
            {
                "topicName": "test-topic",
                "logDirSummary": {"totalSizeBytes": 3072}
            }
        ]}

        # Configure the mock to return the response
        mock_get.return_value = topics_response

        # Create collector and run metrics collection
        collector = RedpandaConsoleTopicCollector("http://localhost:8080")

        # Mock the Gauge
        collector.topic_disk_usage = MagicMock()

        collector.collect_metrics()

        # Check that the metrics were updated correctly
        collector.topic_disk_usage.labels.assert_called_once_with(topic="test-topic")
        collector.topic_disk_usage.labels().set.assert_called_once_with(3072)


if __name__ == "__main__":
    unittest.main()
