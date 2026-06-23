"""Tests for map_cal_response helper."""

import json
from pathlib import Path

from helpers.map_cal_response import map_cal_response
from models.report import AssociatedGroup, AssociatedIndicator

FIXTURE_PATH = Path(__file__).parent / 'fixtures' / 'cal_app_data.json'


def test_map_cal_response_from_fixture():
    app_data = json.loads(FIXTURE_PATH.read_text())
    result = map_cal_response(
        app_data,
        resolve_mitre_tag=lambda object_id: f'TAG:{object_id}',
    )

    assert result.description == 'Threat report summary.'
    assert result.tags == ['541512', 'TAG:T1059']
    assert result.associated_groups == [
        AssociatedGroup(type='Malware', name='Emotet'),
    ]
    assert AssociatedIndicator(type='Host', summary='evil.example.com') in result.associated_indicators
    assert AssociatedIndicator(type='File', summary='d41d8cd98f00b204e9800998ecf8427e') in (
        result.associated_indicators
    )


def test_map_cal_response_empty_app_data():
    result = map_cal_response([])
    assert result.description is None
    assert result.tags == []
    assert result.associated_groups == []
    assert result.associated_indicators == []
