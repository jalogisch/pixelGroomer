# RAW+JPG Split by Type with Paired Names — Design

**Goal:** When importing from an SD card (or directory), allow importing both RAW and JPG, splitting them into subfolders by type (`raw/` and `jpg/` under the date folder), and pairing them so the same shot has a matching base name (e.g. `raw/20260124_Event_001.cr3` and `jpg/20260124_Event_001.jpg`).

**Approach:** Opt-in flag `--split-by-type` on `pg-import`. When set: group files by (EXIF date, base name); assign one sequence per shot; place RAW in `raw/`, non-RAW images in `jpg/`; same base name for each file in a pair. When unset: current behavior (flat date folder, one sequence per file).

**Status:** Design approved. Next: implementation plan (writing-plans).

---

## 1. Behavior and Layout

- **Pairing:** Group files by EXIF date + base name (filename without extension). Each group = one "shot"; one sequence number per shot. Example: `IMG_1000.CR3` and `IMG_1000.JPG` → one shot.
- **Placement:** Under the existing date folder (from `FOLDER_STRUCTURE`), add two subfolders: `raw/` (extensions in `RAW_EXTENSIONS`) and `jpg/` (extensions in `IMAGE_EXTENSIONS`).
- **Naming:** Same pattern as today (e.g. `{date}_{event}_{seq:03d}.{ext}`), so a pair is e.g. `raw/20260124_Event_001.cr3` and `jpg/20260124_Event_001.jpg`.
- **Unpaired files:** A shot with only RAW or only JPG still gets a sequence and goes into the appropriate subfolder.
- **Default (no flag):** Unchanged: flat date folder, one sequence per file, no subfolders.

## 2. Ordering and Sequence

- Shots are ordered by EXIF date-time (then source path if needed) so sequence numbers are stable. Within each shot, all files (RAW + JPG) receive the same sequence number.

## 3. Config and Compatibility

- No new env vars in v1; subfolder names are fixed `raw` and `jpg`.
- Existing options (`--trip`, `NAMING_PATTERN`, `FOLDER_STRUCTURE`) continue to apply; `get_target_dir` still returns the date folder; we append `raw/` or `jpg/` when `--split-by-type` is set.

## 4. Errors and Edge Cases

- **No EXIF date:** Fall back to file mtime (as today); use for grouping and ordering.
- **Same base name, multiple extensions:** All get the same sequence; RAW extensions → `raw/`, image extensions → `jpg/`.
- **Sidecars (e.g. XMP):** No change to current sidecar handling; no pairing logic for sidecars.

## 5. Deliverables

- `bin/pg-import`: add `--split-by-type`; when set, build plan with (date, base name) grouping, one sequence per shot, target paths under `raw/` or `jpg/`.
- Tests: unit/integration for pairing and subfolder layout; update or add e2e for RAW+JPG with `--split-by-type`.
- Docs: `doc/workflow.en.md` / `doc/workflow.de.md` and `doc/scripts.en.md` / `doc/scripts.de.md` (pg-import options) — short subsection describing the flag and resulting layout.
