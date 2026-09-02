"""ThreatConnect indicator helpers for retro confidence updates."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import requests

RISK_SCORE_ATTRIBUTE_TYPE = 'Risk Score'
RESULT_LIMIT = 1000
INDICATORS_PATH = '/v3/indicators'


def iter_indicators(
    session: requests.Session,
    tql: str,
    result_limit: int = RESULT_LIMIT,
) -> Iterator[dict[str, Any]]:
    """Yield all indicators matching TQL, following v3 pagination.

    Args:
        session: Authenticated ThreatConnect session.
        tql: ThreatConnect Query Language filter.
        result_limit: Page size for each GET (max 10000).

    Yields:
        Indicator dictionaries from the v3 API.

    Raises:
        requests.RequestException: If a page request fails.
    """
    response = session.get(
        INDICATORS_PATH,
        params={'tql': tql, 'fields': 'attributes', 'resultLimit': result_limit},
    )
    while True:
        response.raise_for_status()
        body = response.json()
        yield from body.get('data') or []
        next_url = body.get('next')
        if not next_url:
            break
        response = session.get(next_url)


def risk_score_confidence(indicator: dict[str, Any]) -> int | None:
    """Return the Risk Score attribute as a 0-100 integer.

    Args:
        indicator: Indicator dictionary from the v3 API.

    Returns:
        Parsed confidence, or None if the attribute is missing or invalid.
    """
    attributes = indicator.get('attributes')
    if isinstance(attributes, dict):
        attributes = attributes.get('data') or []
    elif not isinstance(attributes, list):
        attributes = []

    for attr in attributes:
        if attr.get('type') != RISK_SCORE_ATTRIBUTE_TYPE:
            continue
        return _parse_confidence(attr.get('value'))
    return None


def update_confidence(
    session: requests.Session,
    indicator_id: int | str,
    confidence: int,
) -> None:
    """PUT an indicator's confidence rating.

    Args:
        session: Authenticated ThreatConnect session.
        indicator_id: Indicator ID.
        confidence: Confidence value (0-100).

    Raises:
        requests.RequestException: If the update request fails.
    """
    response = session.put(
        f'{INDICATORS_PATH}/{indicator_id}',
        json={'confidence': confidence},
    )
    response.raise_for_status()


def _parse_confidence(value: Any) -> int | None:
    """Parse a Risk Score attribute value as a 0-100 integer."""
    if value is None:
        return None
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError):
        return None
    if 0 <= parsed <= 100:
        return parsed
    return None
