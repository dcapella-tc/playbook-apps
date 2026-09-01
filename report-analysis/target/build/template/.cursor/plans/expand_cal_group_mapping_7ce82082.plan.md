---
name: Expand CAL Group Mapping
overview: Extend map_cal_response.py to map CAL vulnerability (CVE), Tactic, and Course of Action rows into associated_groups, following the reference Doc Analysis object_mappings. Attack Patterns remain tags only.
todos:
  - id: map-groups
    content: Add _group_from_row helper; extend GROUP_TYPE_MAP; handle vulnerability via objectId
    status: completed
  - id: fixture-tests
    content: Update cal_app_data.json fixture and test_map_cal_response assertions
    status: completed
  - id: edge-tests
    content: Add unit tests for CVE dedup, missing objectId, attack pattern stays tag-only
    status: completed
isProject: false
---

# Expand CAL Mapping (CVEs and Group Types)

## Goal

Extend [`helpers/map_cal_response.py`](report-analysis/helpers/map_cal_response.py) so Doc Analysis enrichment creates more **associated groups** on the Report. No model or enrich-helper changes needed — [`AssociatedGroup`](report-analysis/models/report.py) and [`create_associated_groups`](report-analysis/helpers/enrich/associated_groups.py) already handle arbitrary group types.

## Current vs proposed mapping

| CAL `objectType` | CAL name field | Today | After |
|------------------|----------------|-------|-------|
| `malware` | `displayName` | Malware group | unchanged |
| `intrusion set` | `displayName` | Intrusion Set group | unchanged |
| `tools` | `displayName` | Tool group | unchanged |
| `vulnerability` | `objectId` (e.g. `CVE-2024-1234`) | **not mapped** | Vulnerability group |
| `tactic` | `displayName` | **not mapped** | Tactic group |
| `course of action` | `displayName` | **not mapped** | Course of Action group |
| `attack pattern` | `objectId` | MITRE tag only | **tags only** (per your choice) |

Reference: Doc Analysis [`object_mappings`](report-analysis/ignore/Clone%20of%20ThreatConnect%20Doc%20Analysis.abxz) in `app.py` lines 209–222.

## Implementation

### 1. Extend `GROUP_TYPE_MAP` and add CVE branch

In [`helpers/map_cal_response.py`](report-analysis/helpers/map_cal_response.py):

```python
GROUP_TYPE_MAP = {
    'malware': 'Malware',
    'intrusion set': 'Intrusion Set',
    'tools': 'Tool',
    'tactic': 'Tactic',
    'course of action': 'Course of Action',
}
```

Add a small helper to resolve group name from a CAL row:

```python
def _group_from_row(row: dict[str, Any]) -> AssociatedGroup | None:
    object_type = row.get('objectType') or ''
    if object_type == 'vulnerability':
        cve = row.get('objectId')
        if cve:
            return AssociatedGroup(type='Vulnerability', name=str(cve))
        return None
    tc_type = GROUP_TYPE_MAP.get(object_type)
    display_name = row.get('displayName')
    if tc_type and display_name:
        return AssociatedGroup(type=tc_type, name=str(display_name))
    return None
```

Replace the inline group block in `map_cal_response` (lines 86–92) with:

```python
group = _group_from_row(row)
if group:
    key = (group.type, group.name)
    if key not in seen_groups:
        seen_groups.add(key)
        associated_groups.append(group)
```

**Notes:**
- CVE rows use `objectId`, not `displayName` (reference `('vulnerability', 'objectId')`)
- Rows with only `description` and no name are skipped (no group name to create)
- Dedup by `(type, name)` unchanged

### 2. Update tests

**[`tests/fixtures/cal_app_data.json`](report-analysis/tests/fixtures/cal_app_data.json)** — add rows:

```json
{"objectType": "vulnerability", "objectId": "CVE-2024-1234"},
{"objectType": "tactic", "displayName": "Execution"},
{"objectType": "course of action", "displayName": "User Training"}
```

**[`tests/test_map_cal_response.py`](report-analysis/tests/test_map_cal_response.py)** — extend fixture assertion:

```python
AssociatedGroup(type='Vulnerability', name='CVE-2024-1234'),
AssociatedGroup(type='Tactic', name='Execution'),
AssociatedGroup(type='Course of Action', name='User Training'),
```

Add focused unit tests in `tests/test_map_cal_response.py` (or new `tests/test_map_cal_groups.py`):

- `vulnerability` without `objectId` → no group
- duplicate CVE row → deduped once
- `attack pattern` → still tag only, no group

### 3. Downstream impact (automatic)

- [`create_associated_groups`](report-analysis/helpers/enrich/associated_groups.py) — no code change; will batch-create new group types with deterministic XIDs
- [`report.groups.count`](report-analysis/app.py) output — will reflect higher counts when CAL returns these types
- No `app_spec.yml` / metadata changes required

## Data flow (unchanged)

```mermaid
flowchart LR
    cal["CAL appData"]
    map["map_cal_response"]
    groups["associated_groups"]
    enrich["create_associated_groups"]
    cal --> map --> groups --> enrich
```

## Out of scope

- Attack Pattern as associated groups (tags only)
- Storing `description` fields on groups (batch create uses name only today)
- CVE as tags in addition to Vulnerability groups
- `tags.count` playbook output
