"""
Management command to list all KoboToolbox forms accessible with your API token.
Helps identify the correct form UID to use.
"""

from django.core.management.base import BaseCommand
from api.services.kobo_client import KoboToolboxClient, KoboAPIException


class Command(BaseCommand):
    help = "List all KoboToolbox forms accessible with your API token"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Fetching your KoboToolbox forms..."))
        self.stdout.write("")

        try:
            client = KoboToolboxClient()
            forms = client.get_forms()

            if not forms:
                self.stdout.write(
                    self.style.WARNING(
                        "No forms found. Check your KOBO_TOKEN and KOBO_BASE_URL."
                    )
                )
                return

            self.stdout.write(self.style.SUCCESS(f"Found {len(forms)} form(s):\n"))

            for idx, form in enumerate(forms, 1):
                uid = form.get("uid", "N/A")
                name = form.get("name", "Untitled")
                asset_type = form.get("asset_type", "N/A")
                deployment_active = form.get("has_deployment", False)
                url = form.get("url", "N/A")

                self.stdout.write(f"{idx}. {self.style.SUCCESS(name)}")
                self.stdout.write(f"   UID: {self.style.WARNING(uid)}")
                self.stdout.write(f"   Type: {asset_type}")
                self.stdout.write(
                    f"   Deployed: {'Yes' if deployment_active else 'No'}"
                )
                self.stdout.write(f"   URL: {url}")
                self.stdout.write("")

            self.stdout.write(
                self.style.NOTICE(
                    "\nUse the UID value in your .env file as KOBO_FORM_UID"
                )
            )

        except KoboAPIException as e:
            self.stdout.write(
                self.style.ERROR(f"Error connecting to KoboToolbox API: {e}")
            )
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("Troubleshooting tips:"))
            self.stdout.write("1. Check your KOBO_TOKEN is correct")
            self.stdout.write(
                "2. Verify KOBO_BASE_URL matches your KoboToolbox server:"
            )
            self.stdout.write(
                "   - For ee.kobotoolbox.org: https://kobo.humanitarianresponse.info"
            )
            self.stdout.write("   - For kf.kobotoolbox.org: https://kf.kobotoolbox.org")
            self.stdout.write("   - For kc.kobotoolbox.org: https://kc.kobotoolbox.org")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Unexpected error: {e}"))
