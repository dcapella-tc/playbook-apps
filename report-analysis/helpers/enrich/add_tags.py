"""Step 3.ii: Add tags to Report."""

from __future__ import annotations

from tcex.api.tc.v2.batch.batch_writer import BatchWriter

from models.doc_analysis_result import DocAnalysisResult
from models.report import Report


def add_tags(
    batch: BatchWriter,
    report: Report,
    analysis: DocAnalysisResult,
) -> None:
    """Add tags to the Report if present in analysis."""
    if not analysis.tags:
        return

    # TODO: batch.tag(...) per tag
    _ = (batch, report)
