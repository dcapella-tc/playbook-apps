"""Step 4: Create ThreatConnect Report."""

from __future__ import annotations

from typing import Any

from tcex import TcEx


def create_report(
    tcex: TcEx,
    owner_name: str,
    report_name: str,
    report_data: dict[str, Any],
) -> dict[str, Any]:
    """Create a ThreatConnect Report group.

    Args:
        tcex: TcEx application instance.
        owner_name: ThreatConnect owner name.
        report_name: Report group name.
        report_data: Shaped report payload from postprocess step.

    Returns:
        Created report metadata including ``xid`` and ``name``.
    """
    # TODO: build and save a Report group via tcex.api.tc.v2.batch.
    _ = (tcex, owner_name, report_data)
    return {'xid': 'stub-report-xid', 'name': report_name, 'type': 'Report'}
