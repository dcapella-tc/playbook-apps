"""Step 3.iii: Create or update associated groups."""

from __future__ import annotations

from tcex.api.tc.v2.batch.batch_writer import BatchWriter

from models.doc_analysis_result import DocAnalysisResult
from models.report import Report


def create_associated_groups(
    batch: BatchWriter,
    owner_name: str,
    report: Report,
    analysis: DocAnalysisResult,
) -> None:
    """Create or update associated groups and link them to the Report."""
    if not analysis.associated_groups:
        return

    # TODO: mirror otx-pb _batch_create_groups + association to report.xid
    _ = (batch, owner_name, report)
