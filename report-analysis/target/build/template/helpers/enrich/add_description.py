"""Step 3.i: Add description attribute to Report."""

from __future__ import annotations

from tcex.api.tc.v2.batch.batch_writer import BatchWriter

from helpers.batch_report import report_group_batch
from models.doc_analysis_result import DocAnalysisResult
from models.report import Report


def add_description(
    batch: BatchWriter,
    report: Report,
    analysis: DocAnalysisResult,
) -> None:
    """Add a description attribute to the Report if present in analysis."""
    if not analysis.description:
        return

    group_batch = report_group_batch(batch, report)
    group_batch.attribute('Description', analysis.description, displayed=True, unique='Type')
    batch.save(group_batch)
