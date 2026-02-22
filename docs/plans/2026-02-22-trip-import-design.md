# Trip Import Mode — Design

**Goal:** Add a "trip mode" to `pg-import` so users can import a full card (e.g. a week-long trip) in one go without being prompted for event or location. Files are placed in one folder per day by EXIF date (existing behaviour). When event is not set, filenames use date and sequence only.

**Status:** Design approved. Next step: implementation plan (writing-plans skill).

---

## 1. Behaviour and Scope

### Trip mode (`--trip`)

- **CLI:** New optional flag `--trip` (and short `-t` if desired) on `pg-import`. Example: `pg-import /Volumes/CARD --trip`.
- **Config:** Event and location still come from `.import.yaml` and `.env`/CLI in the existing priority order. `--trip` does not change that order; it only changes what happens when event/location are still missing after config.
- **Prompts:** When `--trip` is set, do not prompt for event or location. Other prompts (e.g. archive directory if configured) are unchanged.
- **Naming:**
  - If EVENT is non-empty (from YAML/env/CLI): use existing `NAMING_PATTERN` (e.g. `{date}_{event}_{seq:03d}`).
  - If EVENT is empty: use a fixed trip-only pattern `{date}_{seq:03d}` so filenames are like `20260124_001.cr3`, `20260125_002.jpg`.
- **EXIF:** Write event/location only when set (from config). Author/copyright etc. unchanged. No new EXIF fields.
- **Folders:** Unchanged — one folder per day by EXIF date (existing behaviour).

### Out of scope

- No new scripts; no change to `FOLDER_STRUCTURE` or archive layout; no new env vars for the trip pattern (trip pattern is fixed in code).

---

## 2. Implementation

### Where

- Only `bin/pg-import` (and its helpers). No new scripts, no lib API changes.

### Changes

1. **CLI and flag**
   - In the argument parsing block, add a flag (e.g. `-t, --trip`) that sets a variable e.g. `TRIP_MODE=true`.
   - Help text: state that `--trip` skips event/location prompts and uses date-only filenames when event is not set.

2. **Config / prompt logic**
   - In the block that runs after loading config and before building the plan (e.g. `load_import_config()` and the prompt section that follows):
     - If `TRIP_MODE` is true, do not run the "prompt for event" and "prompt for location" steps.
     - Still run: loading from `.import.yaml`, applying `.env`, applying CLI args, and any archive-dir prompt if configured.
     - Still run `EVENT=$(sanitize_filename "$EVENT")` when EVENT is non-empty. When EVENT is empty in trip mode, no need to sanitize.

3. **Naming**
   - In `generate_filename()` (or at its single call site): if `TRIP_MODE` is true and `EVENT` is empty, build the name from `{date}_{seq:03d}.{ext}` (reuse existing date/seq/extension logic; do not use `NAMING_PATTERN` or `{event}`). Otherwise keep current behaviour (use `NAMING_PATTERN` with `$EVENT`).

4. **No new config**
   - Trip pattern is fixed in code as `{date}_{seq:03d}`. No `.env` or `NAMING_PATTERN` override for trip mode.

### Data flow

Unchanged except for the two branches above: source → load config (YAML → .env → CLI) → if not trip, prompt for event/location → build plan (per-file date from EXIF, target dir from `get_target_dir`, name from `generate_filename`) → execute plan. Trip only affects "skip prompts" and "when EVENT empty, use date+seq name".

### Files to touch

- `bin/pg-import` only (parse flag, conditional prompts, conditional naming in `generate_filename` or at call site).

---

## 3. Error Handling and Testing

### Error handling

- No new failure modes; same as today (missing source, no files, EXIF read errors, copy failures). Trip mode only changes prompts and naming.
- Empty event in non-trip mode: unchanged — script still prompts for event when `--trip` is not set.
- Dry-run: `--trip` works with `--dry-run`; dry-run still only prints the plan and does not copy or delete.
- Interaction with existing flags: `--trip` is additive. It does not change behaviour of `--output`, `--no-delete`, `--verbose`, etc.

### Testing

- **Unit:** No new lib API. Optional: add a small test for a helper that computes "trip filename" (date + seq + ext) if that logic is extracted; not required if the logic stays inline in `pg-import`.
- **Integration** (in `tests/integration/test_pg_import.py`):
  - **Trip mode, no event:** Run `pg-import` with `--trip` and no `.import.yaml` (and no event in env). Assert: exit 0, no prompt (non-interactive), and imported filenames match `YYYYMMDD_NNN.ext` (e.g. `20260124_001.jpg`).
  - **Trip mode, event from YAML:** Run with `--trip` and a `.import.yaml` that sets `event: "AlpsTour"`. Assert: filenames use event (e.g. `20260124_AlpsTour_001.jpg`), same as current behaviour.
  - **Help:** Assert `pg-import --help` mentions `--trip` (and optionally "trip" or "date-only" in the description).
- **Existing tests:** Leave current tests as-is; ensure they do not pass `--trip` unless the test is trip-specific. No change to existing behaviour when `--trip` is not used.

### Documentation

- **Script reference:** In `doc/scripts.en.md` and `doc/scripts.de.md`, document `--trip` (and `-t` if added): "Skip event/location prompts; use date-only filenames when event is not set (e.g. trip import)."
- **Workflow:** In `doc/workflow.en.md` and `doc/workflow.de.md`, add a short "Trip / multi-day import" subsection: one command with `--trip`, files land in one folder per day; optional `.import.yaml` for event/location.

---

## 4. Summary

| Item | Decision |
|------|----------|
| Flag | `--trip` (short `-t` optional) |
| Prompts | Skip event and location when `--trip` |
| Event from .import.yaml | Still used when present |
| Naming when no event | `{date}_{seq:03d}.{ext}` (fixed in code) |
| Naming when event set | Existing `NAMING_PATTERN` |
| Folder layout | Unchanged (one per day by EXIF date) |
| Files to change | `bin/pg-import` only |
| Docs | scripts.en/de.md, workflow.en/de.md |
