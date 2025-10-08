"""
Custom template filters for the API app.
"""

from django import template
from datetime import timezone as dt_timezone
from zoneinfo import ZoneInfo
from django.utils import timezone

register = template.Library()


@register.filter(name="readable_field")
def readable_field(value):
    """
    Convert field names to human-readable format.
    Example: 'first_name' -> 'First Name'
    """
    if not value:
        return value
    # Replace underscores with spaces and title case
    return str(value).replace("_", " ").title()


@register.filter(name="is_list")
def is_list(value):
    """Check if value is a list or tuple."""
    return isinstance(value, (list, tuple))


@register.filter(name="dhaka_time")
def dhaka_time(value):
    """
    Convert datetime to Asia/Dhaka timezone.
    """
    if not value:
        return value

    dhaka_tz = ZoneInfo("Asia/Dhaka")

    # If the datetime is naive, assume it's UTC and attach UTC tzinfo
    if timezone.is_naive(value):
        value = value.replace(tzinfo=dt_timezone.utc)

    # Convert to Dhaka timezone
    return value.astimezone(dhaka_tz)
