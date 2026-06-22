"""Report domain models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AssociatedGroup:
    """Associated group to link to a Report."""

    type: str
    name: str


@dataclass
class AssociatedIndicator:
    """Associated indicator to link to a Report."""

    type: str
    summary: str


@dataclass
class Report:
    """ThreatConnect Report group."""

    owner_name: str
    name: str
    xid: str
    type: str = 'Report'
