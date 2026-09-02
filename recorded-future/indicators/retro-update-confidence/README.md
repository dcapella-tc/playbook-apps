# RF Retro Update Confidence

## Release Notes

### 1.0.0

- Initial release: paginate TQL indicators and update confidence from Risk Score.
  Limit how many matching indicators are processed per run.

## Category

- Utility

## Description

Retrieves indicators matching an input TQL query (up to the Max Indicators
limit), paginates the ThreatConnect v3 results, and sets each indicator's
confidence to the integer value of its `Risk Score` attribute.

Indicators without a valid `Risk Score` value (missing, not an integer, or outside
0-100) are skipped. Indicators whose confidence already matches are skipped.
Individual update failures are counted and do not stop the job.

## Inputs

### TQL (String, required)

ThreatConnect Query Language used to select indicators. Include `ownerName` in
the TQL when the job should be owner-scoped.

### Max Indicators (Integer, required)

Maximum number of TQL-matched indicators to process in this run, including
skips. Remaining matches are left for a later run. Must be an integer greater
than or equal to 1.

## Outputs

- `indicators.updated` (String) — indicators whose confidence was updated
- `indicators.skipped` (String) — missing/invalid Risk Score, or confidence already equal
- `indicators.failed` (String) — indicators whose confidence update failed
