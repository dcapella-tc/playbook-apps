"""Map CAL appData rows into DocAnalysisResult."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from models.doc_analysis_result import DocAnalysisResult
from models.report import AssociatedGroup, AssociatedIndicator

INDICATOR_TYPE_MAP = {
    'address': 'Address',
    'emailaddress': 'Email Address',
    'host': 'Host',
    'url': 'URL',
    'asn': 'ASN',
    'cidr': 'CIDR',
    'emailSubject': 'Email Subject',
    'hashtag': 'Hashtag',
    'mutex': 'Mutex',
    'registryKey': 'Registry Key',
    'userAgent': 'User Agent',
}

GROUP_TYPE_MAP = {
    'malware': 'Malware',
    'intrusion set': 'Intrusion Set',
    'tools': 'Tool',
}

_MD5_PATTERN = re.compile(r'^[a-fA-F0-9]{32}$')
_SHA1_PATTERN = re.compile(r'^[a-fA-F0-9]{40}$')
_SHA256_PATTERN = re.compile(r'^[a-fA-F0-9]{64}$')


def _file_indicator_type(hash_value: str) -> str | None:
    if _MD5_PATTERN.match(hash_value):
        return 'File'
    if _SHA1_PATTERN.match(hash_value):
        return 'File'
    if _SHA256_PATTERN.match(hash_value):
        return 'File'
    return None


def _collect_industries(row: dict[str, Any]) -> list[str]:
    industry = row.get('industry', [])
    if isinstance(industry, str):
        return [industry] if industry.strip() else []
    return [str(item) for item in industry if str(item).strip()]


def map_cal_response(
    app_data: list[dict[str, Any]],
    *,
    resolve_mitre_tag: Callable[[str], str | None] | None = None,
) -> DocAnalysisResult:
    """Convert CAL appData into report enrichment fields."""
    description: str | None = None
    tags: list[str] = []
    seen_tags: set[str] = set()
    associated_groups: list[AssociatedGroup] = []
    seen_groups: set[tuple[str, str]] = set()
    associated_indicators: list[AssociatedIndicator] = []
    seen_indicators: set[tuple[str, str]] = set()

    for row in app_data:
        app = row.get('app')
        if app == 'TextSummarizer' and row.get('summary'):
            description = row['summary']

        if app == 'TextIndustrializer':
            for industry in _collect_industries(row):
                if industry not in seen_tags:
                    seen_tags.add(industry)
                    tags.append(industry)

        object_type = row.get('objectType')
        if object_type == 'attack pattern' and row.get('objectId') and resolve_mitre_tag:
            tag = resolve_mitre_tag(row['objectId'])
            if tag and tag not in seen_tags:
                seen_tags.add(tag)
                tags.append(tag)

        group_type = GROUP_TYPE_MAP.get(object_type or '')
        display_name = row.get('displayName')
        if group_type and display_name:
            key = (group_type, display_name)
            if key not in seen_groups:
                seen_groups.add(key)
                associated_groups.append(AssociatedGroup(type=group_type, name=display_name))

        indicator_type_key = row.get('indicatorType')
        unique_id = row.get('uniqueId')
        if indicator_type_key and unique_id:
            if indicator_type_key == 'file':
                tc_type = _file_indicator_type(unique_id)
                if tc_type:
                    key = (tc_type, unique_id)
                    if key not in seen_indicators:
                        seen_indicators.add(key)
                        associated_indicators.append(
                            AssociatedIndicator(type=tc_type, summary=unique_id)
                        )
            else:
                tc_type = INDICATOR_TYPE_MAP.get(indicator_type_key)
                if tc_type:
                    key = (tc_type, unique_id)
                    if key not in seen_indicators:
                        seen_indicators.add(key)
                        associated_indicators.append(
                            AssociatedIndicator(type=tc_type, summary=unique_id)
                        )

    return DocAnalysisResult(
        description=description,
        tags=tags,
        associated_groups=associated_groups,
        associated_indicators=associated_indicators,
    )
