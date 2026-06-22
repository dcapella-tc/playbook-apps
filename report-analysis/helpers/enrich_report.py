"""Step 3: Enrich Report from Doc Analysis."""

from __future__ import annotations

from tcex.api.tc.v2.batch.batch_writer import BatchWriter

from helpers.enrich.add_description import add_description
from helpers.enrich.add_tags import add_tags
from helpers.enrich.associated_groups import create_associated_groups
from helpers.enrich.associated_indicators import create_associated_indicators
from models.doc_analysis_result import DocAnalysisResult
from models.report import Report


def enrich_report(
    batch: BatchWriter,
    owner_name: str,
    report: Report,
    analysis: DocAnalysisResult,
) -> Report:
    """Apply Doc Analysis enrichment to a Report."""
    add_description(batch, report, analysis)
    add_tags(batch, report, analysis)
    create_associated_groups(batch, owner_name, report, analysis)
    create_associated_indicators(batch, owner_name, report, analysis)
    return report
