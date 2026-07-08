"""Tests for cal_client helper."""

from unittest.mock import MagicMock

import pytest

from helpers.cal_client import CALAuth, analyze_document, normalize_cal_host


def test_normalize_cal_host_adds_https_and_slash():
    assert normalize_cal_host('cal.threatconnect.com') == 'https://cal.threatconnect.com/'


def test_cal_auth_sets_headers():
    auth = CALAuth('my-token', 1700000000)
    request = MagicMock()
    request.headers = {}
    auth(request)
    assert request.headers['Authorization'] == 'my-token'
    assert request.headers['Timestamp'] == '1700000000'


def test_analyze_document_rate_limit_raises():
    session = MagicMock()
    response = MagicMock()
    response.status_code = 429
    session.post.return_value = response

    with pytest.raises(ValueError, match='Too many CAL requests'):
        analyze_document(session, 'content', 'cal.threatconnect.com', 'token', 123)
