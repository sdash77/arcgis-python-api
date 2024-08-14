import unittest
from unittest.mock import MagicMock

from arcgis.datapipelines import _pipelines


class TestPipelineRunParsing(unittest.TestCase):
    """Tests for the arcgis.datapipelines._dataclasses module."""

    def setUp(self) -> None:
        self.run = _pipelines.PipelineRun("https://arcgis.com", MagicMock())
        return super().setUp()

    def test_parses_message(self):
        """It parses a message."""
        message = self.run._parse_message(RunCompletedWithErrors["messages"][0])
        self.assertEqual(
            message,
            {
                "type": "info",
                "messageCode": "ADP_102093",
                "message": "Creating new services.",
                "nodeId": "18706e1a0243",
            },
        )

    def test_parses_pipeline_validation_errors(self):
        """It parses failures resulting from invalid pipeline properties."""
        failure = self.run._parse_failure(RunFailurePipelineValidation["failure"])
        self.assertSubsetEqual(
            failure, {"message": "The data is invalid.", "messageCode": "ADP_102015"}
        )
        self.assertEqual(len(failure["detailProperties"]), 2)
        self.assertEqual(
            failure["detailProperties"][0],
            {
                "message": "A required parameter is missing.",
                "messageCode": "ADP_102016",
                "path": "inputs[0].type",
            },
        )
        self.assertEqual(
            failure["detailProperties"][1],
            {
                "message": "A required parameter is missing.",
                "messageCode": "ADP_102016",
                "path": "outputs",
            },
        )

    def test_parses_node_validation_errors(self):
        """It parses failures resulting from invalid node properties."""
        failure = self.run._parse_failure(RunFailureNodeValidation["failure"])
        self.assertSubsetEqual(
            failure,
            {"message": "An unknown error occurred.", "messageCode": "ADP_999999"},
        )
        self.assertEqual(len(failure["detailProperties"]), 2)
        self.assertEqual(
            failure["detailProperties"][0],
            {
                "message": "A required parameter is missing.",
                "messageCode": "ADP_102016",
                "nodeId": "1801aa9ef7a2",
                "parameter": "spatialReference",
            },
        )
        self.assertEqual(
            failure["detailProperties"][1],
            {
                "message": "A required parameter is missing.",
                "messageCode": "ADP_102016",
                "nodeId": "1801aa9ef7a2",
            },
        )

    def test_parses_run_failure_result(self):
        """It parses a run failure."""
        result = self.run._parse_result(RunFailurePipelineValidation)
        self.assertSubsetEqual(
            result,
            {
                "id": "1",
                "status": "failed",
            },
        )
        self.assertEqual(result["failure"]["message"], "The data is invalid.")
        self.assertEqual(len(result["failure"]["details"]), 2)
        self.assertEqual(len(result["failure"]["detailProperties"]), 2)
        self.assertEqual(len(result["messages"]), 0)

    def test_parses_run_completed_result(self):
        """It parses a run success."""
        result = self.run._parse_result(RunCompletedWithErrors)
        self.assertSubsetEqual(
            result,
            {
                "id": "0d440895cd904b84a61d7446c14df858",
                "status": "completedWithErrors",
            },
        )
        self.assertEqual(len(result["messages"]), 5)
        self.assertEqual(
            result["outputs"], [{"itemId": "f5a5df09d9db410cb420bbc9aef21bcc"}]
        )

    def test_parses_run_properties(self):
        """It parses run properties."""
        props = self.run._parse_properties(RunProperties)
        self.assertEqual(
            props,
            {
                "id": "string",
                "itemId": "string",
                "status": "submitted",
                "createdAt": "2024-02-27T01:23:53.621Z",
                "runningAt": "2024-01-27T01:23:53.621Z",
                "terminatedAt": "2024-03-27T01:23:53.621Z",
            },
        )

    def assertSubsetEqual(self, a, b):
        """Assert that b is a subset of a."""
        for k, v in b.items():
            self.assertEqual(a[k], v)


RunFailureNodeValidation = {
    "id": "1",
    "version": "1.1",
    "status": "failed",
    "failure": {
        "code": 422,
        "messageCode": "ADP_999999",
        "message": "An unknown error occurred.",
        "details": [
            "A required parameter is missing",
            "A required parameter is missing",
        ],
        "detailProperties": [
            {
                "messageCode": "ADP_102016",
                "message": "A required parameter is missing.",
                "path": "1801aa9ef7a2.spatialReference",
            },
            {
                "messageCode": "ADP_102016",
                "message": "A required parameter is missing.",
                "path": "1801aa9ef7a2",
            },
        ],
    },
    "messages": [
        {
            "type": "info",
            "messageCode": "ADP_102093",
            "message": "Creating new services.",
            "path": "18706e1a0243",
        }
    ],
}

RunFailurePipelineValidation = {
    "id": "1",
    "version": "1.1",
    "status": "failed",
    "failure": {
        "messageCode": "ADP_102015",
        "message": "The data is invalid.",
        "details": [
            "A required parameter is missing.",
            "A required parameter is missing.",
        ],
        "detailProperties": [
            {
                "messageCode": "ADP_102016",
                "message": "A required parameter is missing.",
                "path": "inputs[0].type",
            },
            {
                "messageCode": "ADP_102016",
                "message": "A required parameter is missing.",
                "path": "outputs",
            },
        ],
    },
    "messages": [],
}

RunCompletedWithErrors = {
    "id": "0d440895cd904b84a61d7446c14df858",
    "status": "completedWithErrors",
    "messages": [
        {
            "type": "info",
            "messageCode": "ADP_102093",
            "message": "Creating new services.",
            "path": "18706e1a0243",
        },
        {
            "type": "info",
            "messageCode": "ADP_102094",
            "message": "Writing records.",
            "path": "18706e1a0243",
        },
        {
            "type": "info",
            "messageCode": "ADP_102100",
            "message": "Completed.",
            "path": "18706e1a0243",
        },
        {
            "type": "info",
            "messageCode": "ADP_102093",
            "message": "Creating new services.",
            "path": "18706e1a02432",
        },
        {
            "type": "error",
            "messageCode": "ADP_102008",
            "message": "Service name is unavailable.",
            "path": "18706e1a02432",
        },
    ],
    "results": {
        "outputs": [
            {
                "itemId": "f5a5df09d9db410cb420bbc9aef21bcc",
                "url": "https://servicesdev.arcgis.com/LkFyxb9zDq7vAOAm/arcgis/rest/services/test_errors4/FeatureServer",
            }
        ],
        "startTimestamp": 1679449097917,
        "endTimestamp": 1679449118001,
    },
}

RunProperties = {
    "id": "string",
    "userId": "string",
    "computeResourceId": "string",
    "status": "submitted",
    "itemId": "string",
    "taskId": "string",
    "taskRunId": "string",
    "timeoutInMinutes": 0,
    "createdAt": "2024-02-27T01:23:53.621Z",
    "submittedAt": "2024-02-27T01:23:53.621Z",
    "waitingAt": "2024-02-27T01:23:53.621Z",
    "runningAt": "2024-01-27T01:23:53.621Z",
    "cancellingAt": "2024-02-27T01:23:53.621Z",
    "cancelledAt": "2024-02-27T01:23:53.621Z",
    "succeededAt": "2024-02-27T01:23:53.621Z",
    "failedAt": "2024-02-27T01:23:53.621Z",
    "completedAt": "2024-02-27T01:23:53.621Z",
    "terminatedAt": "2024-03-27T01:23:53.621Z",
    "failureReason": "internalError",
    "failureMessage": "string",
}


if __name__ == "__main__":
    unittest.main()
