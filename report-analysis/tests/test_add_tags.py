"""Tests for add_tags helper."""

from unittest.mock import MagicMock, patch

from helpers.enrich.add_tags import add_tags
from models.doc_analysis_result import DocAnalysisResult
from models.report import Report


def test_add_tags_tags_report_and_saves():
    batch = MagicMock()
    group_batch = MagicMock()
    report = Report(owner_name='Owner', name='Report', xid='report-xid')
    analysis = DocAnalysisResult(tags=['malware', 'T1059'])

    with patch('helpers.enrich.add_tags.report_group_batch', return_value=group_batch):
        add_tags(batch, report, analysis)

    group_batch.tag.assert_any_call('malware')
    group_batch.tag.assert_any_call('T1059')
    assert group_batch.tag.call_count == 2
    batch.save.assert_called_once_with(group_batch)


def test_add_tags_skips_when_empty():
    batch = MagicMock()
    report = Report(owner_name='Owner', name='Report', xid='report-xid')

    add_tags(batch, report, DocAnalysisResult())

    batch.save.assert_not_called()
