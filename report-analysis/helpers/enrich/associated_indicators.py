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
    if not analysis.associated_indicators:
        return

    # TODO: mirror otx-pb _batch_create_indicators + association to report.xid
    _ = (batch, owner_name, report)
