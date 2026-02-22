# SD Card Identity Template — Design

**Goal:** Provide a minimal pre-created `.import.yaml` template (author, copyright, credit only) that users can copy onto every SD card so their name, the Unlicense, and artist name are set on import, with event/location left unset (e.g. for trip mode or per-shoot settings).

**Status:** Design approved. Next step: implementation plan (writing-plans skill).

---

## 1. Behaviour and Scope

### Template file

- Add **`templates/.import.yaml.identity`** with only three keys (no event, location, tags, etc.):
  - **`author`** — Your name (EXIF Artist / XMP:Creator / IPTC:By-line).
  - **`copyright`** — Copyright text, e.g. Unlicense: “© 2026 Your Name. Released under the Unlicense (https://unlicense.org)” or a short placeholder the user replaces.
  - **`credit`** — Artist name / credit line (e.g. “Jane Doe” or “pixelpiste”), written to **IPTC:Credit** (and optionally XMP if we add it for consistency).
- File includes a short comment at the top: copy to SD card as `DCIM/.import.yaml` or `/.import.yaml`; edit author, copyright, and credit; leave event/location unset for trip import.

### Config and import behaviour

- **Priority unchanged:** `.import.yaml` (lowest) → `.env` → CLI. Values from the identity template on the card are overridden by `.env` and CLI as today.
- **New keys from `.import.yaml`:** pg-import (and any shared loader) will read **`copyright`** and **`credit`** in addition to existing `event`, `location`, `author`, `archive`. If missing, copyright falls back to `DEFAULT_COPYRIGHT` from `.env`; credit is optional (no fallback).
- **EXIF on import:** During import, write **copyright** from YAML when set (else keep current behaviour: `DEFAULT_COPYRIGHT` from `.env`). Write **credit** from YAML when set (new behaviour). Author continues to come from YAML or `.env` as today.

### Out of scope

- No new scripts or CLI commands. No change to folder structure or naming. Event/location remain optional and unset in the identity template so trip mode and per-shoot settings still work as today.

---

## 2. Implementation

### 2.1 Template file

- **Add:** `templates/.import.yaml.identity`
- **Content:** YAML with only `author`, `copyright`, `credit`, plus a short comment. Example placeholder values, e.g. `author: "Your Name"`, `copyright: "© 2026 Your Name. Released under the Unlicense (https://unlicense.org)"`, `credit: "Your Name"` (or “pixelpiste” / artist name). No `event`, `location`, `tags`, or other keys.

### 2.2 EXIF mapping for credit

- **File:** `lib/exif_utils.py`
- **Change:** In `FIELD_MAP`, add a mapping for **credit**, e.g. to **IPTC:Credit** (and optionally **XMP:Credit** or similar if exiftool supports it). Ensure `write()` and any batch path accept a `credit` keyword and pass it to exiftool. No change to existing author/copyright behaviour.

### 2.3 Loading copyright and credit from .import.yaml

- **File:** `lib/config.sh` — `load_import_yaml` already returns all YAML keys as `key=value`; no change needed.
- **File:** `bin/pg-import`
- **Change:** In the config-loading block that parses YAML output (the `case` loop over keys), handle two new keys: **copyright** and **credit**. Store them in variables (e.g. `yaml_copyright`, `yaml_credit`). Apply same priority as author: YAML value used unless overridden by `.env` or CLI. For copyright: if YAML has a value, use it; else keep current behaviour (use `DEFAULT_COPYRIGHT` from `.env`). For credit: use YAML value when present; no `.env` default in this step.

### 2.4 CLI / .env

- **Copyright:** No `--copyright` on pg-import in this step; copyright comes from .import.yaml or `.env` only.
- **Credit:** No CLI flag; credit is set only via `.import.yaml`.

### 2.5 Writing copyright and credit during import

- **File:** `bin/pg-import`
- **Change:** Where EXIF is applied after copy (the block that builds `exif_args` and calls pg-exif or exiftool), use **copyright** from the resolved config (YAML or `.env` fallback for copyright only), and pass **credit** to the EXIF writer when the resolved config has a credit value.
- **File:** `lib/exif_utils.py` — Ensure the write path accepts and writes **credit** using the new FIELD_MAP entry.

### 2.6 Documentation

- **Workflow (EN/DE):** Add a short subsection, e.g. “Identity file for all cards” or “Minimal .import.yaml for author and copyright”: describe `templates/.import.yaml.identity`, that it sets author, copyright (e.g. Unlicense), and credit (artist name); copy to each card as `DCIM/.import.yaml`; leave event/location unset for trip import.
- **Configuration (EN/DE):** In the .import.yaml section, document the **copyright** and **credit** keys and point to the identity template. Optionally add the identity template to the “typical .import.yaml” or “minimal” example.

### Files to touch

- **New:** `templates/.import.yaml.identity`
- **Modify:** `lib/exif_utils.py` (credit in FIELD_MAP and write path), `bin/pg-import` (read copyright/credit from YAML, pass to EXIF write), `doc/workflow.en.md`, `doc/workflow.de.md`, `doc/configuration.en.md`, `doc/configuration.de.md`

---

## 3. Error Handling and Testing

### Error handling

- **Backward compatibility:** Existing `.import.yaml` files without `copyright` or `credit` keep working. Import uses `DEFAULT_COPYRIGHT` from `.env` when YAML has no copyright; credit is simply not written when missing.
- **Empty values:** If YAML has `copyright: ""` or `credit: ""`, treat as unset (don’t write empty EXIF; for copyright, fall back to `DEFAULT_COPYRIGHT` when applicable).
- **Unlicense text length:** Copyright can be a long string; rely on existing exiftool/EXIF write path; no truncation unless we hit a known tag length limit later.
- **No new failure modes:** Missing template or missing keys in YAML do not break import; behaviour is additive.

### Testing

- **Unit:** In `lib/exif_utils.py`, add or extend a test that writes with a `credit` argument and asserts IPTC:Credit (or the chosen tag) is set. Optionally assert that copyright from a dict/metadata is written when provided.
- **Integration:** In `tests/integration/test_pg_import.py`, add a test that runs pg-import with a source that has a `.import.yaml` containing only `author`, `copyright`, and `credit` (no event/location). Assert exit 0 and that the imported file has EXIF Artist, Copyright, and Credit set to those values (using existing exiftool-based helpers if present).
- **Backward compatibility:** Existing import tests that use `.import.yaml` without copyright/credit continue to pass.
- **Template:** Optionally validate `templates/.import.yaml.identity` is valid YAML and contains only the allowed keys; not required for MVP.

### Docs

- Identity template is referenced from workflow and configuration; no separate “testing” section for the template.

---

## 4. Summary

| Item | Decision |
|------|----------|
| Template path | `templates/.import.yaml.identity` |
| Template keys | `author`, `copyright`, `credit` only |
| Credit EXIF | IPTC:Credit (and optionally XMP if added) |
| Copyright source | .import.yaml or fallback to DEFAULT_COPYRIGHT from .env |
| New pg-import YAML keys | `copyright`, `credit` |
| New exif_utils field | `credit` in FIELD_MAP and write path |
| Docs | workflow.en/de.md, configuration.en/de.md |
