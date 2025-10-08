from rest_framework import serializers

from .models import KoboSubmission


class HealthCheckSerializer(serializers.Serializer):
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()


class ProjectMetadataSerializer(serializers.Serializer):
    name = serializers.CharField()
    version = serializers.CharField()
    debug = serializers.BooleanField()


class KoboSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for KoboToolbox submissions."""

    class Meta:
        model = KoboSubmission
        fields = [
            "id",
            "uuid",
            "form_uid",
            "data",
            "date_submitted",
            "date_synced",
            "date_updated",
        ]
        read_only_fields = ["id", "date_synced", "date_updated"]
