from django.db import models


class KoboSubmission(models.Model):
    """
    Stores survey submissions from KoboToolbox.
    Each submission is uniquely identified by its UUID from Kobo.
    """

    uuid = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Kobo submission UUID (_uuid)",
    )
    form_uid = models.CharField(
        max_length=100, db_index=True, help_text="Kobo form/asset UID"
    )
    data = models.JSONField(help_text="Complete submission data from Kobo")
    date_submitted = models.DateTimeField(
        db_index=True, help_text="Submission timestamp from Kobo"
    )
    date_synced = models.DateTimeField(
        auto_now_add=True, help_text="When this record was created in Django"
    )
    date_updated = models.DateTimeField(
        auto_now=True, help_text="Last update timestamp"
    )

    class Meta:
        ordering = ["-date_submitted"]
        verbose_name = "Kobo Submission"
        verbose_name_plural = "Kobo Submissions"
        indexes = [
            models.Index(fields=["-date_submitted"]),
            models.Index(fields=["form_uid", "-date_submitted"]),
        ]

    def __str__(self):
        return f"{self.form_uid} - {self.uuid[:8]} ({self.date_submitted})"
