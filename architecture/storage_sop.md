# Storage SOP
## Goal
Persist test plan history and user settings to local JSON files.

## Files
| File | Purpose |
|------|---------|
| `data/history.json` | Array of all test plan records (Schema 4) |
| `data/settings.json` | Single settings object (Schema 1) |
| `data/exports/` | Generated DOCX/PDF files |

## ID Generation
Format: `TP-YYYYMMDD-NNN`
- `YYYYMMDD` = today's date in UTC
- `NNN` = 3-digit sequence, reset per day (001, 002, ...)
- Example: `TP-20260404-001`

## API Key Masking Rules
- Never expose raw keys in API responses
- Mask rule: show only last 4 chars, prefix with `••••••••••••`
- Example: `sk-abc...XY12` → `••••••••••••XY12`
- On PUT /api/settings: if incoming value starts with `••`, preserve the stored raw value

## History Write Strategy
- Load → check for existing ID → update if found, append if new → write
- Ensures idempotent saves (re-generating same plan updates, not duplicates)

## Settings Merge Strategy
- `load_settings()` always deep-merges stored values onto default structure
- Ensures new fields added in future versions are always present with defaults

## Starred Plans
- `starred: boolean` field on each history record
- Toggled via `PATCH /api/history/{id}/star`
