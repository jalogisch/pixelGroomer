# Raw Development CLI Alternatives — Design

**Goal:** Add RawTherapee as a third processor in pg-develop (preset-driven, film-style capable) and document command-line raw development alternatives (Darktable, ImageMagick, RawTherapee, plus brief mention of sips/ufraw for manual use). Do not apply ImageMagick resize to darktable or RawTherapee output so the developed look is preserved.

**Status:** Design approved. Next step: implementation plan (writing-plans skill).

---

## 1. Scope and Goals

### In scope

- Add **RawTherapee** as third processor in pg-develop: `--processor rawtherapee`, preset = path to PP3 file, config `RAW_PROCESSOR=rawtherapee` and optional `RAWTHERAPEE_PRESET`.
- **Resize rule:** Apply `--resize` only when processor is **ImageMagick**. For **darktable** and **rawtherapee**, do not run ImageMagick (or any external tool) to resize output; if user passes `--resize`, log that resize is not applied for this processor.
- **Documentation:** One “Command-line raw development alternatives” section: table or list of Darktable, ImageMagick, RawTherapee (all three supported by pg-develop), plus 1–2 sentences each on sips (macOS), ufraw/dcraw for manual use.
- Update help and config docs (PROCESSORS, RAW_PROCESSOR, RAWTHERAPEE_PRESET).

### Out of scope

- Bundling PP3 files or film presets; GUI setup; changing darktable or ImageMagick behaviour beyond the resize rule above.

### Success criteria

- Users can run `pg-develop *.cr3 --processor rawtherapee --preset /path/to/kodak.pp3` and get consistent output.
- Docs make it clear which CLI tools exist and which pg-develop supports.
- Darktable and RawTherapee outputs are never resized via ImageMagick.

---

## 2. pg-develop: RawTherapee Integration

### Binary and fallback

- Use **rawtherapee-cli**. Check with `command -v rawtherapee-cli`. If `RAW_PROCESSOR=rawtherapee` and binary is missing, fall back to imagemagick and log a warning (same pattern as darktable).

### Preset

- `--preset` / `-p` is the path to a `.pp3` file (absolute or relative). Optional config: **RAWTHERAPEE_PRESET** = default PP3 path when `--preset` is not set (like DARKTABLE_STYLE). No preset directory resolution in this design; user passes full path (or relative to cwd).

### Invocation

- For each RAW:  
  `rawtherapee-cli -o "<output.jpg>" -j<quality> -Y -c "<input>"`  
  If preset set: add `-p "<path_to.pp3>"` before `-c`. Quality 1–100 via `-j`. Output path = same as today (e.g. `out_dir/basename.jpg`).

### Resize

- **Do not** add any resize step for RawTherapee. If `--resize` is given, log that resize is not applied for this processor.

### Darktable resize (existing behaviour change)

- **Remove** the post-step that runs `convert ... -resize ...` on darktable output. If `--resize` is given when processor is darktable, log that resize is not applied for this processor.

### Sidecars

- RawTherapee uses `.raw.pp3` sidecars. Out of scope for this design: only use `-p` when user passes `--preset` or RAWTHERAPEE_PRESET. No `-s` (use sidecar) in initial implementation.

### Help and config

- **Help:** PROCESSORS section lists darktable, imagemagick, rawtherapee; one line for rawtherapee: “PP3 presets, film simulation; use --preset path/to.pp3”. Valid `--processor` names: darktable, imagemagick, rawtherapee.
- **config.sh:** Add `RAWTHERAPEE_PRESET` (default empty). `RAW_PROCESSOR` may be set to `rawtherapee`.

---

## 3. Documentation: Command-Line Raw Alternatives

### Placement

- New subsection in workflow doc (e.g. “Command-line raw development alternatives”) or a short standalone subsection under “RAW development” in configuration/workflow. Bilingual: EN + DE.

### Content

- **Supported by pg-develop:** Darktable, ImageMagick, RawTherapee — one line each (install, preset support). Note that pg-develop supports all three via `--processor`.
- **Other CLI options (manual use):** Brief mention of sips (macOS, minimal), ufraw/dcraw if relevant — “can be run manually; not integrated in pg-develop.”
- **Resize:** State that `--resize` is only applied when using the ImageMagick processor.

---

## 4. Testing and Error Handling

### Error handling

- Unknown processor: existing behaviour (log and exit). Add rawtherapee to `check_processor` and `detect_processor`.
- Missing rawtherapee-cli: same as darktable (fallback to imagemagick + warn).
- Invalid or missing PP3 path: rawtherapee-cli will fail; script reports failure per file (no special handling beyond existing “Failed: filename” style).

### Tests

- Existing pg-develop and pg-test-processors tests must still pass.
- If pg-test-processors compares processors: add rawtherapee when available (optional; can be follow-up). New integration test for pg-develop with `--processor rawtherapee` only if rawtherapee-cli is available (skip otherwise, same pattern as darktable/imagemagick).
- Document in test plan: manual check that `--resize` is ignored for darktable and rawtherapee (log message present).
