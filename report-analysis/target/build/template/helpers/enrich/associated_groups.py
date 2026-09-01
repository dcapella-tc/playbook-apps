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
    for group in analysis.associated_groups:
        xid = batch.generate_xid([owner_name, group.type, group.name])
        group_batch = batch.group(group.type, group.name, xid=xid)
        group_batch.association(report.xid)
        batch.save(group_batch)
