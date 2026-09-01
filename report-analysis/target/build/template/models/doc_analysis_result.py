"""Doc Analysis result model."""

from __future__ import annotations

from dataclasses import dataclass, field

from models.report import AssociatedGroup, AssociatedIndicator


@dataclass
class DocAnalysisResult:
    """Enrichment data extracted from document analysis."""

    description: str | None = None
    tags: list[str] = field(default_factory=list)
    associated_groups: list[AssociatedGroup] = field(default_factory=list)
    associated_indicators: list[AssociatedIndicator] = field(default_factory=list)
