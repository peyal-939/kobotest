from django.contrib import admin

from .models import KoboSubmission


@admin.register(KoboSubmission)
class KoboSubmissionAdmin(admin.ModelAdmin):
    """Admin interface for KoboToolbox submissions."""

    list_display = [
        "short_uuid",
        "form_uid",
        "date_submitted",
        "date_synced",
    ]
    list_filter = ["form_uid", "date_submitted", "date_synced"]
    search_fields = ["uuid", "form_uid", "data"]
    readonly_fields = ["uuid", "date_synced", "date_updated"]
    ordering = ["-date_submitted"]
    date_hierarchy = "date_submitted"

    fieldsets = (
        (
            "Identification",
            {
                "fields": ("uuid", "form_uid"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("date_submitted", "date_synced", "date_updated"),
            },
        ),
        (
            "Submission Data",
            {
                "fields": ("data",),
                "classes": ("collapse",),
            },
        ),
    )

    def short_uuid(self, obj):
        """Display shortened UUID for readability."""
        return f"{obj.uuid[:12]}..."

    short_uuid.short_description = "UUID"

    def has_add_permission(self, request):
        """Disable manual creation in admin (synced from Kobo only)."""
        return False
