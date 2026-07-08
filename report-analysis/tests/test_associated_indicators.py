"""Tests for associated_indicators helper."""

from unittest.mock import MagicMock

from helpers.enrich.associated_indicators import create_associated_indicators
from models.doc_analysis_result import DocAnalysisResult
from models.report import AssociatedIndicator, Report


def test_create_associated_indicators_creates_and_associates():
    batch = MagicMock()
    indicator_batch = MagicMock()
    batch.indicator.return_value = indicator_batch
    report = Report(owner_name='Owner', name='Report', xid='report-xid')
    analysis = DocAnalysisResult(
        associated_indicators=[AssociatedIndicator(type='Host', summary='evil.example.com')],
    )

    create_associated_indicators(batch, 'Owner', report, analysis)

    batch.indicator.assert_called_once_with('Host', 'evil.example.com')
    indicator_batch.association.assert_called_once_with('report-xid')
    batch.save.assert_called_once_with(indicator_batch)
