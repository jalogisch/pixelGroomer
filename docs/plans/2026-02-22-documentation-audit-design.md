# Documentation audit design

**Date:** 2026-02-22  
**Goal:** Keep README/workflow/examples up to date, order examples easy→complex, document darktable on macOS (Homebrew deprecation) and link preset research in README.

## Decisions

- **Example order:** Both the examples table and section order go easy → complex. Order: Holiday Import → Daily Offload → Album Development → Album Export → Adventure Camp → Enduro → Creating Your Own.
- **Preset research:** Linked from README Documentation section (EN + DE).
- **Darktable on Mac:** Add a short note that the darktable formula may be deprecated/removed from Homebrew; suggest cask, official download, or ImageMagick/RawTherapee.

## Changes

### README (EN + DE)

- **Features:** "RAW development to JPG (darktable-cli, ImageMagick, or RawTherapee)".
- **Install:** Add `rawtherapee` to brew line. Add note: On macOS, the darktable formula may be deprecated or removed from Homebrew; use `brew install --cask darktable`, install from darktable.org, or use ImageMagick/RawTherapee with pg-develop.
- **Documentation:** Add link to "RawTherapee preset research" → doc/preset-research.en.md (and .de.md in README.de.md).

### Workflow (EN + DE)

- **Prerequisites:** Add `rawtherapee` to the brew line (or optional line). Same darktable-on-Mac note as README.

### Examples (EN + DE)

- **Table:** Reorder rows to: holiday-import, daily-offload, develop-album, album-export, adventure-camp-workflow, enduro-workflow.
- **Sections:** Reorder to: Holiday Import → Daily Offload → Album Development → Album Export → Adventure Camp → Enduro → Creating Your Own.

## Reference

- Darktable: Homebrew deprecation (Gatekeeper), disable date 2026-09-01; cask still available.
- RawTherapee: already documented in workflow processor list; add to README and prerequisites for consistency.
