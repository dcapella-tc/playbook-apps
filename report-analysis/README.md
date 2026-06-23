# Report Analysis

## Release Notes

### 0.1.0

- Beta release: CAL analysis, Report enrichment, batch create/update, playbook outputs.

## Category

- Utility

## Description

Analyzes plain-text report content using ThreatConnect CAL Document Analysis,
then creates or updates a ThreatConnect Report and enriches it with extracted
metadata, tags, associated groups, and indicators.

**Beta limitations:** String content only (no Binary/PDF input); content truncated
at 100,000 characters; CAL rate limits apply; re-runs may duplicate indicators.

## Inputs

### Owner Name (String, required)

ThreatConnect owner for the Report and associated intel.

### Report Name (String, required)

Name of the Report group to create or update.

### content (String, required)

Plain-text report body sent to CAL for analysis.

**Note:** CAL credentials (`tc_cal_host`, `tc_cal_token`, `tc_cal_timestamp`) are
provided automatically via the CALSettings feature.

## CAL features (hardcoded)

Alias Extraction, IOC Extraction, AI Summary Generation, AI MITRE ATT&CK
Classification, AI NAICS Industry Classification.

## Pipeline

1. CAL Document Analysis on `content`
2. Create Report (deterministic XID)
3. Enrich Report: description, tags, associated groups, associated indicators
4. Batch submit to ThreatConnect

## Enrichment mapping

| Enrichment | Source |
|------------|--------|
| Description attribute | CAL AI summary |
| Tags | MITRE attack patterns, NAICS industries |
| Associated groups | Malware, Intrusion Set, Tool, Vulnerability (CVE), Tactic, Course of Action |
| Associated indicators | CAL IOC types (host, URL, file hashes, etc.) |

Attack Patterns are added as **tags**, not associated groups.

## Outputs

- `report.xid` (String) — Report external ID
- `report.indicators.count` (String) — count of indicators extracted from CAL
- `report.groups.count` (String) — count of associated groups extracted from CAL
