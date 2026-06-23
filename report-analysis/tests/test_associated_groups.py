"""Tests for associated_groups helper."""

from unittest.mock import MagicMock

from helpers.enrich.associated_groups import create_associated_groups
from models.doc_analysis_result import DocAnalysisResult
from models.report import AssociatedGroup, Report


def test_create_associated_groups_creates_and_associates():
    batch = MagicMock()
    batch.generate_xid.return_value = 'group-xid'
    group_batch = MagicMock()
    batch.group.return_value = group_batch
    report = Report(owner_name='Owner', name='Report', xid='report-xid')
    analysis = DocAnalysisResult(
        associated_groups=[AssociatedGroup(type='Malware', name='Emotet')],
    )

    create_associated_groups(batch, 'Owner', report, analysis)

    batch.generate_xid.assert_called_once_with(['Owner', 'Malware', 'Emotet'])
    batch.group.assert_called_once_with('Malware', 'Emotet', xid='group-xid')
    group_batch.association.assert_called_once_with('report-xid')
    batch.save.assert_called_once_with(group_batch)
