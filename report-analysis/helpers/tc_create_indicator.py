"""Step 6.ii: Create ThreatConnect indicator."""

from __future__ import annotations

from typing import Any

from tcex import TcEx


def create_indicator(
    tcex: TcEx,
    owner_name: str,
    indicator_data: dict[str, Any],
    report_xid: str,
) -> dict[str, Any]:
    """Create a ThreatConnect indicator and associate it to a report.

    Args:
        tcex: TcEx application instance.
        owner_name: ThreatConnect owner name.
        indicator_data: Normalized indicator from jmespath_indicator.
        report_xid: XID of the parent report group.

    Returns:
        Created indicator metadata.
    """
    # TODO: build and save indicator via tcex.api.tc.v2.batch with report association.
    _ = (tcex, owner_name, report_xid)
    indicator_type = indicator_data.get('type', 'Unknown')
    summary = indicator_data.get('summary', '')
    return {
        'type': indicator_type,
        'summary': summary,
        'associatedGroupXid': report_xid,
    }
