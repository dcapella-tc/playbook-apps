"""Tests for write_output."""

from unittest.mock import MagicMock, patch

from app import App


def test_write_output_writes_report_variables():
    tcex = MagicMock()
    tcex.inputs.model_unresolved = MagicMock()
    tcex.inputs.model = MagicMock(owner_name='Owner')
    tcex.api.tc.v2.batch.return_value = MagicMock()

    with patch('playbook_app.AppInputs') as mock_app_inputs:
        mock_app_inputs.return_value.update_inputs.return_value = None
        app = App(tcex)

    app.report_xid = 'report-xid-123'
    app.indicators_count = 5
    app.groups_count = 2

    app.write_output()

    app.playbook.create.string.assert_any_call('report.xid', 'report-xid-123')
    app.playbook.create.string.assert_any_call('report.indicators.count', 5)
    app.playbook.create.string.assert_any_call('report.groups.count', 2)
    assert app.playbook.create.string.call_count == 3


def test_write_output_skips_xid_when_none():
    tcex = MagicMock()
    tcex.inputs.model_unresolved = MagicMock()
    tcex.inputs.model = MagicMock(owner_name='Owner')
    tcex.api.tc.v2.batch.return_value = MagicMock()

    with patch('playbook_app.AppInputs') as mock_app_inputs:
        mock_app_inputs.return_value.update_inputs.return_value = None
        app = App(tcex)

    app.report_xid = None
    app.indicators_count = 0
    app.groups_count = 0

    app.write_output()

    app.playbook.create.string.assert_any_call('report.indicators.count', 0)
    app.playbook.create.string.assert_any_call('report.groups.count', 0)
    assert app.playbook.create.string.call_count == 2
