from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    HealthCheckView,
    KoboSubmissionViewSet,
    KoboWebhookView,
    ProjectMetadataView,
    home_view,
    submission_detail_view,
    submit_survey_view,
    view_submissions_view,
)

router = DefaultRouter()
router.register(r"submissions", KoboSubmissionViewSet, basename="kobo-submission")

urlpatterns = [
    # API endpoints
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("meta/", ProjectMetadataView.as_view(), name="project-metadata"),
    path("kobo/webhook/", KoboWebhookView.as_view(), name="kobo-webhook"),
    path("api/", include(router.urls)),
    # Web interface
    path("", home_view, name="home"),
    path("submit/", submit_survey_view, name="submit-survey"),
    path("submissions/", view_submissions_view, name="view-submissions"),
    path("submissions/<int:pk>/", submission_detail_view, name="submission-detail"),
]
