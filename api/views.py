import os
from datetime import datetime, timezone as _dt_timezone
from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import KoboSubmission
from .serializers import (
    HealthCheckSerializer,
    KoboSubmissionSerializer,
    ProjectMetadataSerializer,
)
from .services import KoboToolboxClient


class HealthCheckView(APIView):
    """Lightweight endpoint to confirm the API is running."""

    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        serializer = HealthCheckSerializer(
            {"status": "ok", "timestamp": timezone.now()}
        )
        return Response(serializer.data)


class ProjectMetadataView(APIView):
    """Expose basic project metadata for client bootstrapping."""

    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        serializer = ProjectMetadataSerializer(
            {
                "name": "KoboToolbox API",
                "version": "0.1.0",
                "debug": settings.DEBUG,
            }
        )
        return Response(serializer.data)


class KoboWebhookView(APIView):
    """
    Receive real-time submission webhooks from KoboToolbox REST Services.

    Configure in Kobo project settings:
    - REST Services → Add new endpoint
    - URL: https://yourdomain.com/api/kobo/webhook/
    - Method: POST
    """

    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request):
        """Process incoming webhook payload from Kobo."""
        payload = request.data

        # Extract required fields
        uuid = payload.get("_uuid")
        if not uuid:
            return Response(
                {"error": "Missing _uuid in payload"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get form UID (may come from different fields depending on Kobo setup)
        form_uid = payload.get("_xform_id_string") or payload.get("formid") or "unknown"

        # Parse submission timestamp
        submission_time_str = payload.get("_submission_time")
        if submission_time_str:
            try:
                # Parse ISO timestamp (Kobo returns Z for UTC)
                dt = datetime.fromisoformat(submission_time_str.replace("Z", "+00:00"))
                # Ensure it's timezone-aware (assume UTC if naive)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=_dt_timezone.utc)
                # Convert to Asia/Dhaka explicitly
                dhaka_tz = ZoneInfo("Asia/Dhaka")
                date_submitted = dt.astimezone(dhaka_tz)
            except (ValueError, AttributeError):
                date_submitted = timezone.now()
        else:
            date_submitted = timezone.now()

        # Create or update submission
        obj, created = KoboSubmission.objects.update_or_create(
            uuid=uuid,
            defaults={
                "form_uid": form_uid,
                "data": payload,
                "date_submitted": date_submitted,
            },
        )

        return Response(
            {
                "status": "ok",
                "action": "created" if created else "updated",
                "uuid": uuid,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class KoboSubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to browse synced KoboToolbox submissions.

    Provides list and detail views (read-only).
    Filter by form_uid using ?form_uid=xxx
    """

    queryset = KoboSubmission.objects.all()
    serializer_class = KoboSubmissionSerializer
    filterset_fields = ["form_uid"]
    ordering_fields = ["date_submitted", "date_synced"]
    ordering = ["-date_submitted"]


# Template-based views for web interface


def home_view(request):
    """Home page with app overview."""
    return render(request, "api/home.html")


def submit_survey_view(request):
    """Page with embedded Kobo form for submission."""
    form_url = os.getenv("KOBO_FORM_URL", "")
    return render(request, "api/submit_survey.html", {"form_url": form_url})


def view_submissions_view(request):
    """List all submissions with search and auto-sync."""
    # Auto-sync if requested
    sync_message = None
    sync_status = None
    if request.GET.get("sync") == "true":
        form_uid = os.getenv("KOBO_FORM_UID")
        if not form_uid:
            sync_message = "KOBO_FORM_UID not configured in .env file"
            sync_status = "error"
        else:
            try:
                client = KoboToolboxClient()
                submissions = client.get_submissions(form_uid)

                created_count = 0
                updated_count = 0
                total_fetched = len(submissions) if submissions else 0

                for sub in submissions:
                    uuid = sub.get("_uuid")
                    if not uuid:
                        continue

                    submission_time_str = sub.get("_submission_time")
                    if submission_time_str:
                        try:
                            dt = datetime.fromisoformat(
                                submission_time_str.replace("Z", "+00:00")
                            )
                            if dt.tzinfo is None:
                                dt = dt.replace(tzinfo=_dt_timezone.utc)
                            dhaka_tz = ZoneInfo("Asia/Dhaka")
                            date_submitted = dt.astimezone(dhaka_tz)
                        except (ValueError, AttributeError):
                            date_submitted = timezone.now()
                    else:
                        date_submitted = timezone.now()

                    _, created = KoboSubmission.objects.update_or_create(
                        uuid=uuid,
                        defaults={
                            "form_uid": form_uid,
                            "data": sub,
                            "date_submitted": date_submitted,
                        },
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

                sync_message = f"✓ Synced {total_fetched} submissions from KoboToolbox. Created: {created_count}, Updated: {updated_count}"
                sync_status = "success"
            except Exception as e:
                import traceback

                error_detail = traceback.format_exc()
                print(f"Sync error: {error_detail}")  # Log to console
                sync_message = f"Sync failed: {str(e)}"
                sync_status = "error"

    # Get submissions with search
    search_query = request.GET.get("search", "")
    submissions = KoboSubmission.objects.all().order_by("-date_submitted")

    if search_query:
        submissions = submissions.filter(
            data__icontains=search_query
        ) | submissions.filter(uuid__icontains=search_query)

    return render(
        request,
        "api/view_submissions.html",
        {
            "submissions": submissions,
            "sync_message": sync_message,
            "sync_status": sync_status,
            "search_query": search_query,
        },
    )


def submission_detail_view(request, pk):
    """Detail view for a single submission."""
    submission = get_object_or_404(KoboSubmission, pk=pk)
    return render(request, "api/submission_detail.html", {"submission": submission})
