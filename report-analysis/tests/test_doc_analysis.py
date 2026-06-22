"""Tests for doc_analysis helper."""

import pytest

from helpers.doc_analysis import doc_analysis
from models.doc_analysis_result import DocAnalysisResult


def test_doc_analysis_returns_empty_result():
    result = doc_analysis('some report content')
    assert isinstance(result, DocAnalysisResult)
    assert result.description is None
    assert result.tags == []
    assert result.associated_groups == []
    assert result.associated_indicators == []


def test_doc_analysis_empty_content_raises():
    with pytest.raises(ValueError, match='empty'):
        doc_analysis('')
