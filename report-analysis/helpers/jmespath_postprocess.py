"""Step 3: JMESPath postprocess."""

from __future__ import annotations

from typing import Any

import jmespath

JMESPATH_EXPRESSION = '@'  # TODO: replace with postprocess expression


def jmespath_postprocess(data: dict[str, Any]) -> dict[str, Any]:
    """Apply the postprocess JMESPath expression to analyzed data.

    Args:
        data: Analyzed report data from step 2.

    Returns:
        Report payload shaped for ThreatConnect create/update, including an
        ``indicators`` list when present in the source data.
    """
    result = jmespath.search(JMESPATH_EXPRESSION, data)
    if result is None:
        return {'indicators': []}
    if not isinstance(result, dict):
        return {'value': result, 'indicators': []}

    payload = dict(result)
    indicators = payload.get('indicators', [])
    if indicators is None:
        indicators = []
    payload['indicators'] = indicators
    return payload
