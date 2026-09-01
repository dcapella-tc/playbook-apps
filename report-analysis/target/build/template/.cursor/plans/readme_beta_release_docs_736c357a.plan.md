---
name: README Beta Release Docs
overview: Replace stale template README and incremental release notes with accurate beta documentation. Set programVersion to 0.1.0-beta and align app_spec.yml and install.json with current Report Analysis behavior.
todos:
  - id: readme
    content: Rewrite README.md with description, inputs, outputs, pipeline, beta limitations
    status: completed
  - id: app-spec
    content: Set programVersion 0.1.0-beta and consolidated releaseNotes in app_spec.yml
    status: completed
  - id: install-json
    content: Set programVersion 0.1.0-beta in install.json; optional displayName (Beta)
    status: completed
isProject: false
---

# README + Beta Release Notes (0.1.0-beta)

## Goal

Replace the leftover basic-template docs with accurate **beta** documentation. Version **`0.1.0-beta`** (pre-1.0; not GA). Consolidate misleading `1.0.0` / `1.1.0` skeleton notes into one beta changelog.

## Files to update

| File | Current state | Action |
|------|---------------|--------|
| [`README.md`](report-analysis/README.md) | "Example Basic Playbook App" template | Rewrite |
| [`app_spec.yml`](report-analysis/app_spec.yml) | `programVersion: 1.1.0`, skeleton + 1.1.0 notes | Beta version + consolidated notes |
| [`install.json`](report-analysis/install.json) | `programVersion: 1.1.0` | Match `0.1.0-beta` |

No code changes to [`app.py`](report-analysis/app.py) or helpers.

## 1. Version bump: `0.1.0-beta`

Set `programVersion: 0.1.0-beta` in both [`app_spec.yml`](report-analysis/app_spec.yml) and [`install.json`](report-analysis/install.json).

**Replace** `releaseNotes` in `app_spec.yml` with a single beta entry (drop separate 1.0.0 skeleton / 1.1.0 output entries):

```yaml
releaseNotes:
- notes:
  - Beta release. CAL Document Analysis, Report create/enrich via batch API, playbook outputs.
  version: 0.1.0-beta
```

Optional: append `(Beta)` to `displayName` in `app_spec.yml` / `install.json` — e.g. `Report Analysis (Beta)`. Skip unless you want it visible in App Builder.

## 2. Rewrite [`README.md`](report-analysis/README.md)

Follow sibling app structure ([`qualys/README.md`](../qualys/README.md), [`csv_hosted/README.md`](../csv_hosted/README.md)):

```markdown
# Report Analysis

## Release Notes

### 0.1.0-beta

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
```

Keep prose concise; adjust wording to match repo tone.

## 3. Align `app_spec.yml` note (optional polish)

Current `note` is accurate. Optionally expand one line to mention beta:

```yaml
note: Beta. Analyze plain-text report content via CAL Document Analysis, then
  create or update a ThreatConnect Report with extracted enrichment.
```

## 4. Out of scope

- `sdkVersion` bump (4.0.1 → 4.0.10) — separate from docs
- New `appId` — deployment concern, not docs
- `manifest.json` hash updates — TcEx tooling concern
- Tests — no behavior change

## Verification

- `programVersion` matches in `app_spec.yml` and `install.json`
- README inputs/outputs match [`app_spec.yml`](report-analysis/app_spec.yml) sections
- No references to "basic template" or skeleton remain
