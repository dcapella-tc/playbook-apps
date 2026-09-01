"""CAL Document Analysis API client."""

from __future__ import annotations

from typing import Any

import requests
import requests.auth

CAL_APPS = 'alias,ioc,textsummarize,attack,textindustry'
MAX_CONTENT_LENGTH = 100_000


class CALAuth(requests.auth.AuthBase):
    """Token-based auth for CAL."""

    def __init__(self, token: str, timestamp: int):
        self.token = token
        self.timestamp = timestamp

    def __call__(self, r: requests.PreparedRequest):
        r.headers['Authorization'] = self.token
        r.headers['Timestamp'] = str(self.timestamp)
        return r


def normalize_cal_host(cal_host: str) -> str:
    """Ensure CAL host is a base URL with trailing slash."""
    host = cal_host.rstrip('/')
    if not host.startswith('http'):
        host = f'https://{host}'
    return f'{host}/'


def analyze_document(
    session: requests.Session,
    content: str,
    cal_host: str,
    cal_token: str,
    cal_timestamp: int,
) -> list[dict[str, Any]]:
    """Call CAL Document Analysis and return appData rows.

    Raises:
        ValueError: On rate limit (HTTP 429).
        requests.HTTPError: On other non-success responses.
    """
    session.base_url = normalize_cal_host(cal_host)
    session.auth = CALAuth(cal_token, cal_timestamp)

    text = content[:MAX_CONTENT_LENGTH]
    documents = [
        {
            'name': 'Playbook Document',
            'text': text,
            'sourceId': 'http://threatconnect.com/playbooks',
            'shareable': 1,
        }
    ]
    params = {
        'source': 'playbooks',
        'apps': CAL_APPS,
        'output': 'clean',
    }

    response = session.post('/helix/document/v1/analyze', params=params, json=documents)
    if response.status_code == 429:
        raise ValueError('Too many CAL requests in the last 24 hours. Please try again later.')

    response.raise_for_status()
    payload = response.json()
    if not payload:
        return []
    return payload[0].get('appData', []) or []
