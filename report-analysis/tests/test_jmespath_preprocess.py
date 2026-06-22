"""Tests for jmespath_preprocess helper."""

import pytest

from helpers.jmespath_preprocess import jmespath_preprocess


def test_jmespath_preprocess_parses_json():
    content = '{"title": "Test Report", "indicators": []}'
    result = jmespath_preprocess(content)
    assert result == {'title': 'Test Report', 'indicators': []}


def test_jmespath_preprocess_empty_content_raises():
    with pytest.raises(ValueError, match='empty'):
        jmespath_preprocess('')
