"""Step 1: Doc Analysis."""

from __future__ import annotations

from models.doc_analysis_result import DocAnalysisResult


def doc_analysis(content: str) -> DocAnalysisResult:
    """Analyze document content and extract enrichment data.

    Args:
        content: Raw report content from the playbook input.

    Returns:
        Enrichment data for the Report (description, tags, associations).

    Raises:
        ValueError: If content is empty.
    """
    if not content or not str(content).strip():
        raise ValueError('content input is empty.')

    # TODO: integrate Doc Analysis service or local parsing logic.
    return DocAnalysisResult()
