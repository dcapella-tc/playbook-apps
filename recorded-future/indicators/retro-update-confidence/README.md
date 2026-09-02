# RF Retro Update Confidence

## Release Notes

### 1.0.0

- Initial release: paginate TQL indicators and update confidence from Risk Score.

## Category

- Utility

## Description

Retrieves all indicators matching an input TQL query, paginates the ThreatConnect
v3 results, and sets each indicator's confidence to the integer value of its
`Risk Score` attribute.

Indicators without a valid `Risk Score` value (missing, not an integer, or outside
0-100) are skipped. Indicators whose confidence already matches are skipped.
Individual update failures are counted and do not stop the job.

## Inputs

### TQL (String, required)

ThreatConnect Query Language used to select indicators. Include `ownerName` in
the TQL when the job should be owner-scoped.

## Outputs

- `indicators.updated` (String) — indicators whose confidence was updated
- `indicators.skipped` (String) — missing/invalid Risk Score, or confidence already equal
- `indicators.failed` (String) — indicators whose confidence update failed
