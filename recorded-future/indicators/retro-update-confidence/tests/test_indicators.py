"""Tests for indicator helpers."""

from unittest.mock import MagicMock

import pytest
import requests

from helpers.indicators import (
    RESULT_LIMIT,
    iter_indicators,
    risk_list_confidence,
    update_confidence,
)


def _response(data=None, next_url=None, ok=True, status_code=200):
    response = MagicMock()
    response.ok = ok
    response.status_code = status_code
    body = {'data': data or []}
    if next_url is not None:
        body['next'] = next_url
    response.json.return_value = body
    if not ok:
        response.raise_for_status.side_effect = requests.HTTPError('request failed')
    return response


def test_iter_indicators_paginates_next_url():
    session = MagicMock()
    first = _response([{'id': 1}], next_url='https://tc.example/api/v3/indicators?resultStart=1000')
    second = _response([{'id': 2}])
    session.get.side_effect = [first, second]

    indicators = list(iter_indicators(session, 'typeName = "Address"'))

    assert [item['id'] for item in indicators] == [1, 2]
    first_call = session.get.call_args_list[0]
    assert first_call.args[0] == '/v3/indicators'
    assert first_call.kwargs['params'] == {
        'tql': 'typeName = "Address"',
        'fields': 'attributes',
        'resultLimit': RESULT_LIMIT,
    }
    assert session.get.call_args_list[1].args[0] == (
        'https://tc.example/api/v3/indicators?resultStart=1000'
    )


def test_iter_indicators_get_failure_raises():
    session = MagicMock()
    session.get.return_value = _response(ok=False, status_code=400)

    with pytest.raises(requests.HTTPError):
        list(iter_indicators(session, 'typeName = "Address"'))


def test_risk_list_confidence_parses_nested_attribute():
    indicator = {
        'attributes': {
            'data': [
                {'type': 'Description', 'value': 'noise'},
                {'type': 'Risk List', 'value': '85'},
            ]
        }
    }
    assert risk_list_confidence(indicator) == 85


def test_risk_list_confidence_uses_first_risk_list():
    indicator = {
        'attributes': {
            'data': [
                {'type': 'Risk List', 'value': '10'},
                {'type': 'Risk List', 'value': '90'},
            ]
        }
    }
    assert risk_list_confidence(indicator) == 10


def test_risk_list_confidence_missing_returns_none():
    assert risk_list_confidence({'attributes': {'data': []}}) is None
    assert risk_list_confidence({}) is None


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        ('not-a-number', None),
        ('101', None),
        ('-1', None),
        ('0', 0),
        ('100', 100),
        (50, 50),
    ],
)
def test_risk_list_confidence_invalid_and_boundary_values(value, expected):
    indicator = {'attributes': {'data': [{'type': 'Risk List', 'value': value}]}}
    assert risk_list_confidence(indicator) == expected


def test_update_confidence_puts_confidence_body():
    session = MagicMock()
    session.put.return_value = _response()

    update_confidence(session, 42, 75)

    session.put.assert_called_once_with('/v3/indicators/42', json={'confidence': 75})


def test_update_confidence_put_failure_raises():
    session = MagicMock()
    session.put.return_value = _response(ok=False, status_code=500)

    with pytest.raises(requests.HTTPError):
        update_confidence(session, 42, 75)
