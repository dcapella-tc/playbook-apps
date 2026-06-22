"""Step 1: JMESPath preprocess."""

from __future__ import annotations

import json
from typing import Any

import jmespath

JMESPATH_EXPRESSION = '@'  # TODO: replace with preprocess expression


def jmespath_preprocess(content: str) -> dict[str, Any]:
    """Parse content and apply the preprocess JMESPath expression.

    Args:
        content: Raw report content, expected to be JSON.

    Returns:
        Parsed and transformed data as a dict.

    Raises:
        ValueError: If content is empty or not valid JSON.
    """
    if not content or not str(content).strip():
        raise ValueError('content input is empty.')

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f'content is not valid JSON ({exc}).') from exc

    result = jmespath.search(JMESPATH_EXPRESSION, data)
    if result is None:
        return {}
    if not isinstance(result, dict):
        return {'value': result}
    return result
