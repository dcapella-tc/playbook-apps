"""Tests for App run and write_output."""

from unittest.mock import MagicMock, patch

import pytest
import requests
from tcex.exit import ExitCode

from app import App


def _build_app(tql: str = 'typeName = "Address"') -> App:
    tcex = MagicMock()
    tcex.inputs.model_unresolved = MagicMock()
    tcex.inputs.model = MagicMock(tql=tql)
    with patch('playbook_app.AppInputs') as mock_app_inputs:
        mock_app_inputs.return_value.update_inputs.return_value = None
        return App(tcex)


def _indicator(indicator_id, confidence, risk_list=None, summary=None):
    attributes = []
    if risk_list is not None:
        attributes.append({'type': 'Risk List', 'value': risk_list})
    return {
        'id': indicator_id,
        'summary': summary or f'ioc-{indicator_id}',
        'confidence': confidence,
        'attributes': {'data': attributes},
    }


def test_write_output_writes_count_variables():
    app = _build_app()
    app.updated_count = 3
    app.skipped_count = 2
    app.failed_count = 1

    app.write_output()

    app.playbook.create.string.assert_any_call('indicators.updated', 3)
    app.playbook.create.string.assert_any_call('indicators.skipped', 2)
    app.playbook.create.string.assert_any_call('indicators.failed', 1)
    assert app.playbook.create.string.call_count == 3


def test_run_exits_when_tql_is_empty():
    app = _build_app(tql='   ')
    app.tcex.exit.exit.side_effect = SystemExit

    with pytest.raises(SystemExit):
        app.run()

    app.tcex.exit.exit.assert_called_once_with(ExitCode.FAILURE, 'TQL input is required.')


def test_run_updates_skips_and_counts_put_failures():
    app = _build_app()
    session = MagicMock()
    app.tcex.session.tc.__enter__.return_value = session
    put_ok = MagicMock()
    put_fail = MagicMock()
    put_fail.raise_for_status.side_effect = requests.HTTPError('put failed')
    session.put.side_effect = [put_ok, put_fail]

    indicators = [
        _indicator(1, 10, risk_list='80'),
        _indicator(2, 25, risk_list='25'),
        _indicator(3, 10),
        _indicator(4, 10, risk_list='90'),
    ]

    with patch('app.iter_indicators', return_value=indicators):
        app.run()

    assert app.updated_count == 1
    assert app.skipped_count == 2
    assert app.failed_count == 1
    session.put.assert_any_call('/v3/indicators/1', json={'confidence': 80})
    session.put.assert_any_call('/v3/indicators/4', json={'confidence': 90})
    assert 'Updated 1 indicators (2 skipped, 1 failed).' == app.exit_message


def test_run_get_failure_exits():
    app = _build_app()
    session = MagicMock()
    app.tcex.session.tc.__enter__.return_value = session

    app.tcex.exit.exit.side_effect = SystemExit

    with patch('app.iter_indicators', side_effect=requests.HTTPError('get failed')):
        with pytest.raises(SystemExit):
            app.run()

    app.tcex.exit.exit.assert_called_once()
    assert 'Failed to retrieve indicators' in app.tcex.exit.exit.call_args.args[1]
