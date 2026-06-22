"""Step 2: Create ThreatConnect Report."""

from __future__ import annotations

from tcex.api.tc.v2.batch.batch_writer import BatchWriter

from models.report import Report


def create_report(
    batch: BatchWriter,
    owner_name: str,
    report_name: str,
) -> Report:
    """Create a ThreatConnect Report group.

    Args:
        batch: TcEx batch writer for the target owner.
        owner_name: ThreatConnect owner name.
        report_name: Report group name.

    Returns:
        Created report metadata.
    """
    xid = batch.generate_xid([owner_name, 'Report', report_name])
    # TODO: batch.group('Report', report_name, xid=xid) + batch.save(...)
    return Report(owner_name=owner_name, name=report_name, xid=xid)
