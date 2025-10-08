"""
KoboToolbox API Client

Provides a Python interface to interact with KoboToolbox REST API v2.
Handles authentication, form metadata retrieval, and submission fetching.
"""

import os
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
from django.conf import settings


class KoboAPIException(Exception):
    """Raised when Kobo API returns an error response."""

    pass


class KoboToolboxClient:
    """
    Client for interacting with KoboToolbox API.

    Usage:
        client = KoboToolboxClient()
        forms = client.get_forms()
        submissions = client.get_submissions(form_uid='abc123')
    """

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize KoboToolbox API client.

        Args:
            token: API token from KoboToolbox. If None, reads from KOBO_TOKEN env var.
            base_url: Base URL for Kobo API. If None, reads from KOBO_BASE_URL env var.
            timeout: Request timeout in seconds (default 30).
        """
        self.token = token or os.getenv("KOBO_TOKEN", "")
        self.base_url = base_url or os.getenv(
            "KOBO_BASE_URL", "https://kf.kobotoolbox.org"
        )
        self.timeout = timeout

        if not self.token:
            raise ValueError(
                "KOBO_TOKEN must be provided or set as environment variable"
            )

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Token {self.token}",
                "Accept": "application/json",
            }
        )

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to Kobo API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path (e.g., '/api/v2/assets/')
            **kwargs: Additional arguments passed to requests

        Returns:
            JSON response as dictionary

        Raises:
            KoboAPIException: If request fails or returns error status
        """
        url = urljoin(self.base_url, endpoint)

        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise KoboAPIException(
                f"HTTP {response.status_code}: {response.text}"
            ) from e
        except requests.exceptions.RequestException as e:
            raise KoboAPIException(f"Request failed: {str(e)}") from e
        except ValueError as e:
            raise KoboAPIException(f"Invalid JSON response: {str(e)}") from e

    def get_forms(self) -> List[Dict[str, Any]]:
        """
        Retrieve all forms/assets accessible to the authenticated user.

        Returns:
            List of form metadata dictionaries.
        """
        response = self._make_request("GET", "/api/v2/assets/")
        return response.get("results", [])

    def get_form_details(self, form_uid: str) -> Dict[str, Any]:
        """
        Get detailed metadata for a specific form.

        Args:
            form_uid: The unique identifier for the form/asset

        Returns:
            Form metadata dictionary
        """
        return self._make_request("GET", f"/api/v2/assets/{form_uid}/")

    def get_submissions(
        self, form_uid: str, limit: Optional[int] = None, start: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Fetch submissions for a specific form.

        Args:
            form_uid: The unique identifier for the form/asset
            limit: Maximum number of submissions to retrieve (None = all)
            start: Starting offset for pagination

        Returns:
            List of submission dictionaries
        """
        params = {"start": start}
        if limit:
            params["limit"] = limit

        response = self._make_request(
            "GET", f"/api/v2/assets/{form_uid}/data/", params=params
        )
        return response.get("results", [])

    def get_all_submissions(self, form_uid: str) -> List[Dict[str, Any]]:
        """
        Fetch all submissions for a form (handles pagination automatically).

        Args:
            form_uid: The unique identifier for the form/asset

        Returns:
            Complete list of all submissions
        """
        all_submissions = []
        start = 0
        limit = 1000  # Fetch in batches of 1000

        while True:
            batch = self.get_submissions(form_uid, limit=limit, start=start)
            if not batch:
                break
            all_submissions.extend(batch)
            start += limit
            # If we got fewer than limit, we've reached the end
            if len(batch) < limit:
                break

        return all_submissions

    def get_submission_count(self, form_uid: str) -> int:
        """
        Get the total number of submissions for a form.

        Args:
            form_uid: The unique identifier for the form/asset

        Returns:
            Total count of submissions
        """
        response = self._make_request(
            "GET", f"/api/v2/assets/{form_uid}/data/", params={"limit": 1}
        )
        return response.get("count", 0)
