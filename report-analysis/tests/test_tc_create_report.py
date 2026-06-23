"""Tests for tc_create_report helper."""

from unittest.mock import MagicMock

from helpers.tc_create_report import create_report
from models.report import Report


def test_create_report_uses_batch_generate_xid():
    batch = MagicMock()
    batch.generate_xid.return_value = 'generated-report-xid'
    group_batch = MagicMock()
    batch.group.return_value = group_batch

    result = create_report(batch, 'MyOwner', 'My Report')

    batch.generate_xid.assert_called_once_with(['MyOwner', 'Report', 'My Report'])
    batch.group.assert_called_once_with('Report', 'My Report', xid='generated-report-xid')
    batch.save.assert_called_once_with(group_batch)
    assert result == Report(
        owner_name='MyOwner',
        name='My Report',
        xid='generated-report-xid',
        type='Report',
    )
