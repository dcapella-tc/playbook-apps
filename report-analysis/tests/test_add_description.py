"""Tests for add_description helper."""

from unittest.mock import MagicMock, patch

from helpers.enrich.add_description import add_description
from models.doc_analysis_result import DocAnalysisResult
from models.report import Report


def test_add_description_sets_attribute_and_saves():
    batch = MagicMock()
    group_batch = MagicMock()
    report = Report(owner_name='Owner', name='Report', xid='report-xid')
    analysis = DocAnalysisResult(description='Threat summary')

    with patch('helpers.enrich.add_description.report_group_batch', return_value=group_batch):
        add_description(batch, report, analysis)

    group_batch.attribute.assert_called_once_with(
        'Description',
        'Threat summary',
        displayed=True,
        unique='Type',
    )
    batch.save.assert_called_once_with(group_batch)


def test_add_description_skips_when_missing():
    batch = MagicMock()
    report = Report(owner_name='Owner', name='Report', xid='report-xid')

    add_description(batch, report, DocAnalysisResult())

    batch.save.assert_not_called()
