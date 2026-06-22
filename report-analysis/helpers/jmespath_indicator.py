"""Step 6.i: JMESPath indicator normalization."""

from __future__ import annotations

from typing import Any

import jmespath

JMESPATH_EXPRESSION = '@'  # TODO: replace with indicator expression


def jmespath_indicator(indicator_raw: Any) -> dict[str, Any]:
    """Normalize a single indicator using JMESPath.

    Args:
        indicator_raw: Raw indicator object from the report payload.

    Returns:
        Normalized indicator dict with ``type`` and ``summary`` keys when available.
    """
    result = jmespath.search(JMESPATH_EXPRESSION, indicator_raw)
    if result is None:
        return {}
    if not isinstance(result, dict):
        return {'summary': str(result)}

    indicator = dict(result)
    if 'type' not in indicator and 'indicator_type' in indicator:
        indicator['type'] = indicator['indicator_type']
    if 'summary' not in indicator and 'value' in indicator:
        indicator['summary'] = indicator['value']
    return indicator
