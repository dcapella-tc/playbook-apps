"""Qualys API helper functions."""

from __future__ import annotations

import requests


def qualys_gateway_url(api_base_url: str) -> str:
    """Map Qualys API server URL to gateway URL for JWT /auth.

    Args:
        api_base_url: Qualys API server URL (qualysapi host).

    Returns:
        Corresponding gateway host URL for authentication requests.
    """
    return api_base_url.rstrip('/').replace('qualysapi', 'gateway', 1)


def get_qualys_cve_data(base_url: str, jwt_token: str, cve: str) -> str:
    """Fetch raw KnowledgeBase vulnerability data for a CVE.

    Args:
        base_url: Qualys API server URL (qualysapi host, e.g. https://qualysapi.qg3.apps.qualys.com).
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


def get_qualys_token(base_url: str, username: str, api_key: str) -> str:
    """Authenticate to Qualys and return a bearer token/JWT.

    Args:
        base_url: Qualys API server URL (qualysapi host). JWT auth is sent to the
            corresponding gateway host automatically.
        username: Qualys API username.
        api_key: Qualys API key (sent as the password form field).

    Returns:
        Bearer token/JWT string from the Qualys auth endpoint.

    Raises:
        requests.HTTPError: If the API returns a non-2xx status.
    """
    url = f'{qualys_gateway_url(base_url)}/auth'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Requested-With': 'Python requests',
    }
    data = {
        'username': username,
        'password': api_key,
        'token': 'true',
    }
    response = requests.post(url, headers=headers, data=data, timeout=30)
    response.raise_for_status()
    return response.text.strip()
