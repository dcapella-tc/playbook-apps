"""Shared batch helpers for Report groups."""

from __future__ import annotations

from tcex.api.tc.v2.batch.batch_writer import BatchWriter

from models.report import Report


def report_group_batch(batch: BatchWriter, report: Report):
    """Return a batch group entry for an existing Report."""
    return batch.group('Report', report.name, xid=report.xid)
