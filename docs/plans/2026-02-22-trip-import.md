# Trip Import Mode Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a `--trip` flag to `pg-import` that skips event/location prompts and uses date-only filenames when event is not set, so users can import a full card (e.g. a week trip) in one go.

**Architecture:** Single script change in `bin/pg-import`: new flag, conditional skip of event/location prompts, and conditional naming in `generate_filename()`. Tests and bilingual docs follow.

**Tech Stack:** Bash (bin/pg-import), pytest (tests/integration), Markdown (doc/).

**Design reference:** `docs/plans/2026-02-22-trip-import-design.md`

---

## Task 1: Add --trip flag and TRIP_MODE variable

**Files:**
- Modify: `bin/pg-import` (Script Variables section, parse_args, show_help)

**Step 1: Add variable and flag**

In the "Script Variables" section (around line 24), add after `VERBOSE=false`:

```bash
TRIP_MODE=false
```

In `parse_args()`, add a case for the new flag (e.g. after `--no-delete`):

```bash
            -t|--trip)
                TRIP_MODE=true
                shift
                ;;
```

In `show_help()`, add to OPTIONS (e.g. after `--no-delete`):

```bash
    -t, --trip             Trip mode: skip event/location prompts, date-only names when no event
```

And add to EXAMPLES:

```bash
    pg-import /Volumes/CARD --trip    # Import without event/location prompts (date-only names)
```

**Step 2: Verify help**

Run: `bin/pg-import --help`  
Expected: `--trip` and the new example appear; script exits 0.

**Step 3: Commit**

```bash
git add bin/pg-import
git commit -m "created: add --trip flag to pg-import"
```

---

## Task 2: Skip event and location prompts when TRIP_MODE is true

**Files:**
- Modify: `bin/pg-import` (prompt block after config load, around lines 188–198)

**Step 1: Wrap event/location prompts in a condition**

Locate the block that prompts for event and location (e.g. "Prompt for event if still missing" and "Prompt for location (optional)"). Wrap that block so it runs only when `TRIP_MODE` is not true.

Example (adapt to exact line numbers and variable names):

```bash
    # Prompt for event if still missing (skip in trip mode)
    if [[ "$TRIP_MODE" != "true" && -z "$EVENT" ]]; then
        log_info "No event name specified"
        EVENT=$(prompt_input "Enter event name" "" "EVENT")
    fi
    
    # Prompt for location (optional) — skip in trip mode
    if [[ "$TRIP_MODE" != "true" && -z "$LOCATION" ]]; then
        LOCATION=$(prompt_input "Enter location (optional, press Enter to skip)" "" "LOCATION")
    fi
```

Keep the existing "Sanitize event name" step; when EVENT is empty in trip mode, sanitize is a no-op or harmless.

**Step 2: Verify non-interactive**

Run: `pg-import /tmp/empty_dir --trip 2>&1` (with an empty or non-existent dir; expect failure but no prompt for event).  
Expected: script does not hang on prompt; may fail with "No supported files" or similar.

**Step 3: Commit**

```bash
git add bin/pg-import
git commit -m "enhanced: skip event/location prompts in trip mode"
```

---

## Task 3: Use date-only filename pattern in trip mode when EVENT is empty

**Files:**
- Modify: `bin/pg-import` (function `generate_filename`, around lines 246–279)

**Step 1: Branch at start of generate_filename()**

At the start of `generate_filename()`, after assigning `file`, `sequence`, `date`, and `ext` (get_extension), add:

When `TRIP_MODE` is true and `EVENT` is empty, build the name as `{date}_{seq:03d}.{ext}` and return (echo) it, then return from the function. Use the existing `pad_number` for the sequence (e.g. 3 digits). Otherwise fall through to the existing pattern logic.

Example shape (adapt to exact style):

```bash
generate_filename() {
    local file="$1"
    local sequence="$2"
    local date="$3"
    
    local ext
    ext=$(get_extension "$file")
    
    # Trip mode with no event: date + sequence only
    if [[ "$TRIP_MODE" == "true" && -z "${EVENT:-}" ]]; then
        local padded_seq
        padded_seq=$(pad_number "$sequence" "3")
        echo "${date}_${padded_seq}.${ext}"
        return 0
    fi
    
    local pattern="$NAMING_PATTERN"
    # ... rest unchanged
```

Ensure `pad_number` is called with the same padding behaviour as for `{seq:03d}` (see existing usage in the function).

**Step 2: Run existing import tests**

Run: `make test-fast` or `pytest tests/integration/test_pg_import.py -v` (excluding slow if needed).  
Expected: existing tests still pass (they do not use `--trip`).

**Step 3: Commit**

```bash
git add bin/pg-import
git commit -m "enhanced: use date-only filenames in trip mode when event empty"
```

---

## Task 4: Integration tests for trip mode

**Files:**
- Modify: `tests/integration/test_pg_import.py`

**Step 1: Add test that --help mentions --trip**

Add a test (e.g. in an existing class or a new `TestPgImportTrip` class):

```python
def test_import_help_mentions_trip(self, run_script):
    """pg-import --help mentions --trip."""
    result = run_script('pg-import', '--help')
    assert result.returncode == 0
    output = result.stdout + result.stderr
    assert '--trip' in output
    assert 'trip' in output.lower()
```

**Step 2: Add test that trip mode with no event produces date-only filenames**

Use the existing fixtures (e.g. `temp_sd_card`, `create_jpeg_with_date`, `test_env`, `run_script`). Create a small SD layout with at least one JPEG that has EXIF date. Run `pg-import` with `--trip`, no `.import.yaml`, and no event in env. Assert exit 0 and that the copied file in the archive has a name like `YYYYMMDD_NNN.jpg` (date + 3-digit seq + extension). Mark with `@requires_exiftool` and `@requires_pillow` if other import tests do.

**Step 3: Add test that trip mode with event from .import.yaml uses event in filename**

Create a temp source with `.import.yaml` containing `event: "AlpsTour"` (and optionally location). Add a JPEG with EXIF date. Run `pg-import` with `--trip`. Assert that the imported file name contains the event (e.g. `*AlpsTour*` or pattern matching `{date}_AlpsTour_{seq}.jpg`).

**Step 4: Run tests**

Run: `pytest tests/integration/test_pg_import.py -v -k trip` (or run the new tests by name).  
Expected: new tests pass.

**Step 5: Commit**

```bash
git add tests/integration/test_pg_import.py
git commit -m "created: add integration tests for pg-import trip mode"
```

---

## Task 5: Document --trip in script reference and workflow

**Files:**
- Modify: `doc/scripts.en.md` (pg-import options and/or examples)
- Modify: `doc/scripts.de.md` (same)
- Modify: `doc/workflow.en.md` (add short "Trip / multi-day import" subsection)
- Modify: `doc/workflow.de.md` (same)

**Step 1: Script reference EN**

In `doc/scripts.en.md`, in the pg-import section, add `-t, --trip` to the options list and a one-line description: skip event/location prompts; use date-only filenames when event is not set (e.g. trip import). Add one example: `pg-import /Volumes/CARD --trip`.

**Step 2: Script reference DE**

In `doc/scripts.de.md`, add the same option and example in German (e.g. "Trip-Modus: keine Abfrage für Event/Ort; dateinamen nur aus Datum+Sequenz, wenn kein Event gesetzt").

**Step 3: Workflow EN**

In `doc/workflow.en.md`, add a short subsection (e.g. under Phase 2: Import) titled "Trip / multi-day import". State: run once with `--trip`; files are placed in one folder per day by EXIF date; event/location optional via `.import.yaml`.

**Step 4: Workflow DE**

In `doc/workflow.de.md`, add the same subsection in German.

**Step 5: Commit**

```bash
git add doc/scripts.en.md doc/scripts.de.md doc/workflow.en.md doc/workflow.de.md
git commit -m "enhanced: document pg-import --trip in scripts and workflow docs"
```

---

## Final verification

- `make lint` — exit 0  
- `make test-fast` — all relevant tests pass  
- `pg-import --help` — shows `--trip`  
- Manual (optional): run `pg-import <path> --trip --dry-run` with a folder of test images; confirm plan shows date-only names when no event is set

---

## Execution handoff

Plan saved to `docs/plans/2026-02-22-trip-import.md`.

Two execution options:

1. **Subagent-driven (this session)** — I run a subagent per task, you review between tasks.
2. **Parallel session** — Open a new session with executing-plans, run the plan with checkpoints.

Which approach?
