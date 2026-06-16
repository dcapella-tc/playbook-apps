"""Qualys API helper functions."""

from __future__ import annotations

import requests


def get_qualys_cve_data(base_url: str, jwt_token: str, cve: str) -> str:
    """Fetch raw KnowledgeBase vulnerability data for a CVE.

    Args:
        base_url: Qualys platform base URL (e.g. https://qualysapi.qualys.com).
        jwt_token: Bearer JWT for Qualys API authentication.
        cve: CVE identifier (e.g. CVE-2024-1234).

    Returns:
        Raw response body text from the Qualys API.

    Raises:
        requests.HTTPError: If the API returns a non-2xx status.
    """
    url = f'{base_url.rstrip("/")}/api/4.0/fo/knowledge_base/vuln/'
    headers = {
        'X-Requested-With': 'curl',
        'Authorization': f'Bearer {jwt_token}',
    }
    params = {'action': 'list', 'cve': cve}
    response = requests.post(url, headers=headers, params=params, timeout=60)
    response.raise_for_status()
    return response.text
