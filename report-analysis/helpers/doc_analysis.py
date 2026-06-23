"""Step 1: Doc Analysis."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from helpers.cal_client import analyze_document
from helpers.map_cal_response import map_cal_response
from models.doc_analysis_result import DocAnalysisResult


def doc_analysis(
    content: str,
    *,
    session: Any,
    cal_host: str,
    cal_token: str,
    cal_timestamp: int,
    resolve_mitre_tag: Callable[[str], str | None] | None = None,
) -> DocAnalysisResult:
    """Analyze document content via CAL and extract enrichment data.

    Args:
        content: Plain-text report content from the playbook input.
        session: Requests session for CAL HTTP calls.
        cal_host: CAL hostname or base URL from CALSettings.
        cal_token: CAL authorization token from CALSettings.
        cal_timestamp: CAL token expiration timestamp from CALSettings.
        resolve_mitre_tag: Optional callback to resolve MITRE object IDs to tags.

    Returns:
        Enrichment data for the Report (description, tags, associations).

    Raises:
        ValueError: If content is empty or CAL rate-limits the request.
        requests.HTTPError: If the CAL request fails.
    """
    if not content or not str(content).strip():
        raise ValueError('content input is empty.')

    app_data = analyze_document(session, content, cal_host, cal_token, cal_timestamp)
    return map_cal_response(app_data, resolve_mitre_tag=resolve_mitre_tag)
