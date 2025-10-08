"""
Django management command to fetch and sync KoboToolbox submissions.

Usage:
    python manage.py fetch_kobo_data <form_uid>
    python manage.py fetch_kobo_data <form_uid> --limit 100
    python manage.py fetch_kobo_data <form_uid> --force-update
"""

import os
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from api.models import KoboSubmission
from api.services import KoboToolboxClient


class Command(BaseCommand):
    help = "Fetch submissions from KoboToolbox and sync to database"

    def add_arguments(self, parser):
        parser.add_argument(
            "form_uid",
            nargs="?",
            type=str,
            help="KoboToolbox form/asset UID (optional if KOBO_FORM_UID env var is set)",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Maximum number of submissions to fetch (default: all)",
        )
        parser.add_argument(
            "--force-update",
            action="store_true",
            help="Update existing submissions even if already synced",
        )

    def handle(self, *args, **options):
        form_uid = options.get("form_uid") or os.getenv("KOBO_FORM_UID")

        if not form_uid:
            raise CommandError(
                "Form UID is required. Provide it as argument or set KOBO_FORM_UID env variable."
            )

        limit = options.get("limit")
        force_update = options.get("force_update", False)

        self.stdout.write(
            self.style.NOTICE(f"Fetching submissions from form: {form_uid}")
        )

        try:
            client = KoboToolboxClient()
        except ValueError as e:
            raise CommandError(str(e))

        # Fetch form details first
        try:
            form_details = client.get_form_details(form_uid)
            form_name = form_details.get("name", "Unknown")
            self.stdout.write(f"Form name: {form_name}")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not fetch form details: {e}"))

        # Fetch submissions
        try:
            if limit:
                submissions = client.get_submissions(form_uid, limit=limit)
                self.stdout.write(f"Fetched {len(submissions)} submissions")
            else:
                total_count = client.get_submission_count(form_uid)
                self.stdout.write(f"Total submissions available: {total_count}")
                submissions = client.get_all_submissions(form_uid)
                self.stdout.write(f"Fetched all {len(submissions)} submissions")
        except Exception as e:
            raise CommandError(f"Failed to fetch submissions: {e}")

        # Sync to database
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for submission in submissions:
            uuid = submission.get("_uuid")
            if not uuid:
                self.stdout.write(
                    self.style.WARNING("Skipping submission without UUID")
                )
                skipped_count += 1
                continue

            # Parse submission date
            submission_time_str = submission.get("_submission_time")
            if submission_time_str:
                try:
                    # Parse ISO 8601 format
                    date_submitted = datetime.fromisoformat(
                        submission_time_str.replace("Z", "+00:00")
                    )
                    if timezone.is_naive(date_submitted):
                        date_submitted = timezone.make_aware(date_submitted)
                except (ValueError, AttributeError):
                    date_submitted = timezone.now()
            else:
                date_submitted = timezone.now()

            # Create or update
            obj, created = KoboSubmission.objects.update_or_create(
                uuid=uuid,
                defaults={
                    "form_uid": form_uid,
                    "data": submission,
                    "date_submitted": date_submitted,
                },
            )

            if created:
                created_count += 1
            elif force_update:
                updated_count += 1
            else:
                skipped_count += 1

        # Summary
        self.stdout.write(self.style.SUCCESS("\n=== Sync Summary ==="))
        self.stdout.write(
            self.style.SUCCESS(f"Created: {created_count} new submissions")
        )
        if force_update:
            self.stdout.write(self.style.SUCCESS(f"Updated: {updated_count}"))
        self.stdout.write(f"Skipped: {skipped_count} (already exist)")
        self.stdout.write(
            self.style.SUCCESS(
                f"\nTotal in database: {KoboSubmission.objects.filter(form_uid=form_uid).count()}"
            )
        )
