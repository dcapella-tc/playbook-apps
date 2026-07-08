"""Tests for doc_analysis helper."""

from unittest.mock import MagicMock, patch

import pytest

from helpers.doc_analysis import doc_analysis
from models.doc_analysis_result import DocAnalysisResult
from models.report import AssociatedGroup, AssociatedIndicator


def test_doc_analysis_orchestrates_cal_and_mapping():
    session = MagicMock()
    app_data = [
        {'app': 'TextSummarizer', 'summary': 'Summary text.'},
        {'objectType': 'malware', 'displayName': 'Emotet'},
    ]

    with patch('helpers.doc_analysis.analyze_document', return_value=app_data) as mock_analyze:
        result = doc_analysis(
            'report body',
            session=session,
            cal_host='cal.threatconnect.com',
            cal_token='token',
            cal_timestamp=1234567890,
        )

    mock_analyze.assert_called_once_with(
        session,
        'report body',
        'cal.threatconnect.com',
        'token',
        1234567890,
    )
    assert isinstance(result, DocAnalysisResult)
    assert result.description == 'Summary text.'
    assert result.associated_groups == [AssociatedGroup(type='Malware', name='Emotet')]


def test_doc_analysis_empty_content_raises():
    with pytest.raises(ValueError, match='empty'):
        doc_analysis(
            '',
            session=MagicMock(),
            cal_host='cal.threatconnect.com',
            cal_token='token',
            cal_timestamp=1234567890,
        )
