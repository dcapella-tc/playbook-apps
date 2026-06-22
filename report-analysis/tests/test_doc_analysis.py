"""Tests for doc_analysis helper."""

from helpers.doc_analysis import doc_analysis


def test_doc_analysis_pass_through():
    data = {'title': 'Test Report', 'indicators': [{'type': 'Host', 'summary': '1.2.3.4'}]}
    result = doc_analysis(data)
    assert result is data
    assert result == data
