"""Tests for enrich_report helper."""

from unittest.mock import MagicMock, patch

from helpers.enrich_report import enrich_report
from models.doc_analysis_result import DocAnalysisResult
from models.report import AssociatedGroup, AssociatedIndicator, Report


def test_enrich_report_empty_analysis_is_noop():
    batch = MagicMock()
    report = Report(owner_name='Owner', name='Report', xid='xid')

    with (
        patch('helpers.enrich_report.add_description') as mock_description,
        patch('helpers.enrich_report.add_tags') as mock_tags,
        patch('helpers.enrich_report.create_associated_groups') as mock_groups,
        patch('helpers.enrich_report.create_associated_indicators') as mock_indicators,
    ):
        result = enrich_report(batch, 'Owner', report, DocAnalysisResult())

    mock_description.assert_called_once_with(batch, report, DocAnalysisResult())
    mock_tags.assert_called_once_with(batch, report, DocAnalysisResult())
    mock_groups.assert_called_once_with(batch, 'Owner', report, DocAnalysisResult())
    mock_indicators.assert_called_once_with(batch, 'Owner', report, DocAnalysisResult())
    assert result is report


def test_enrich_report_with_enrichment_data():
    batch = MagicMock()
    report = Report(owner_name='Owner', name='Report', xid='xid')
    analysis = DocAnalysisResult(
        description='A threat report',
        tags=['malware'],
        associated_groups=[AssociatedGroup(type='Adversary', name='APT1')],
        associated_indicators=[AssociatedIndicator(type='Host', summary='1.2.3.4')],
    )

    result = enrich_report(batch, 'Owner', report, analysis)

    assert result is report
