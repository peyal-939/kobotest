from datetime import datetime
from unittest.mock import MagicMock, patch

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import KoboSubmission


class HealthCheckViewTests(APITestCase):
    def test_health_endpoint_returns_ok(self):
        url = reverse("health-check")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ok")


class ProjectMetadataViewTests(APITestCase):
    def test_metadata_endpoint_returns_expected_payload(self):
        url = reverse("project-metadata")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("name", response.data)
        self.assertIn("version", response.data)
        self.assertIn("debug", response.data)


class KoboWebhookViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("kobo-webhook")
        self.sample_payload = {
            "_uuid": "test-uuid-12345",
            "_xform_id_string": "test-form-uid",
            "_submission_time": "2025-10-07T12:00:00.000Z",
            "respondent_name": "Test User",
            "survey_response": "Sample answer",
        }

    def test_webhook_creates_new_submission(self):
        response = self.client.post(self.url, self.sample_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "ok")
        self.assertEqual(response.data["action"], "created")
        self.assertEqual(response.data["uuid"], "test-uuid-12345")

        # Verify database record
        submission = KoboSubmission.objects.get(uuid="test-uuid-12345")
        self.assertEqual(submission.form_uid, "test-form-uid")
        self.assertEqual(submission.data, self.sample_payload)

    def test_webhook_updates_existing_submission(self):
        # Create initial submission
        self.client.post(self.url, self.sample_payload, format="json")

        # Update with new data
        updated_payload = self.sample_payload.copy()
        updated_payload["survey_response"] = "Updated answer"

        response = self.client.post(self.url, updated_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["action"], "updated")

        # Verify only one record exists
        self.assertEqual(
            KoboSubmission.objects.filter(uuid="test-uuid-12345").count(), 1
        )

        # Verify data was updated
        submission = KoboSubmission.objects.get(uuid="test-uuid-12345")
        self.assertEqual(submission.data["survey_response"], "Updated answer")

    def test_webhook_rejects_missing_uuid(self):
        invalid_payload = {"formid": "test-form"}
        response = self.client.post(self.url, invalid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)


class KoboSubmissionModelTests(APITestCase):
    def test_submission_str_representation(self):
        submission = KoboSubmission.objects.create(
            uuid="abc123-def456",
            form_uid="form-001",
            data={"test": "data"},
            date_submitted=timezone.now(),
        )
        self.assertIn("form-001", str(submission))
        self.assertIn("abc123", str(submission))


class KoboSubmissionAPITests(APITestCase):
    def setUp(self):
        self.submission = KoboSubmission.objects.create(
            uuid="api-test-uuid",
            form_uid="api-form-001",
            data={"question1": "answer1"},
            date_submitted=timezone.now(),
        )

    def test_list_submissions(self):
        url = reverse("kobo-submission-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle both paginated and non-paginated responses
        data = (
            response.data
            if isinstance(response.data, list)
            else response.data.get("results", [])
        )
        self.assertEqual(len(data), 1)

    def test_retrieve_submission_detail(self):
        url = reverse("kobo-submission-detail", args=[self.submission.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], "api-test-uuid")
        self.assertEqual(response.data["form_uid"], "api-form-001")

    def test_filter_submissions_by_form_uid(self):
        # Create another submission with different form_uid
        KoboSubmission.objects.create(
            uuid="another-uuid",
            form_uid="api-form-002",
            data={"test": "data"},
            date_submitted=timezone.now(),
        )

        url = reverse("kobo-submission-list")
        response = self.client.get(url, {"form_uid": "api-form-001"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = (
            response.data
            if isinstance(response.data, list)
            else response.data.get("results", [])
        )
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["form_uid"], "api-form-001")
