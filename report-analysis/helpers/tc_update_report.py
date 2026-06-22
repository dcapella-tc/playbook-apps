"""Step 5: Update ThreatConnect Report."""

from __future__ import annotations

from typing import Any

from tcex import TcEx


def update_report(
    tcex: TcEx,
    owner_name: str,
    report: dict[str, Any],
    report_data: dict[str, Any],
) -> dict[str, Any]:
    """Update an existing ThreatConnect Report group.

    Args:
        tcex: TcEx application instance.
        owner_name: ThreatConnect owner name.
        report: Report metadata returned from create_report.
        report_data: Shaped report payload from postprocess step.

    Returns:
        Updated report metadata.
    """
    # TODO: apply attributes, tags, and associations via batch or v3 API.
    _ = (tcex, owner_name)
    return {**report, **report_data}
