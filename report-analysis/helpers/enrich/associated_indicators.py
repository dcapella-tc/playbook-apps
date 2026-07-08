"""Step 3.iv: Create or update associated indicators."""

from __future__ import annotations

from tcex.api.tc.v2.batch.batch_writer import BatchWriter

from models.doc_analysis_result import DocAnalysisResult
from models.report import Report


def create_associated_indicators(
    batch: BatchWriter,
    owner_name: str,
    report: Report,
    analysis: DocAnalysisResult,
) -> None:
    """Create or update associated indicators and link them to the Report."""
    for indicator in analysis.associated_indicators:
        indicator_batch = batch.indicator(indicator.type, indicator.summary)
        indicator_batch.association(report.xid)
        batch.save(indicator_batch)
