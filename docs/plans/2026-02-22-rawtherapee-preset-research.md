# RawTherapee Kodak-style preset research

**Date:** 2026-02-22  
**Context:** Adventure Camp workflow uses `pg-develop --processor rawtherapee --preset <path>.pp3`. We wanted a permissively licensed Kodak-style PP3 to ship in `templates/` (Task 7); research done to decide.

**User-facing doc:** The full research is included in the documentation as [doc/preset-research.en.md](../doc/preset-research.en.md) and [doc/preset-research.de.md](../doc/preset-research.de.md).

## How RawTherapee “Kodak” looks work

| Mechanism | Format | Used by | Notes |
|-----------|--------|---------|--------|
| **Processing profile (PP3)** | `.pp3` text file | `rawtherapee-cli -p <path>` / pg-develop | Full tool settings; what our script expects. |
| **Film Simulation** | HaldCLUT (PNG/TIFF) | RawTherapee GUI only | RawPedia “Film Simulation” = HaldCLUT collection; not applied via CLI `-p`. |

So for **CLI** (and our script), we need a **PP3** file. The RawPedia Film Simulation page is about **HaldCLUT** (GUI workflow), not PP3.

## Sources checked

### 1. RawPedia Film Simulation (HaldCLUT)

- **URL:** [Film Simulation](https://rawpedia.rawtherapee.com/Film_Simulation)
- **Content:** [RawTherapee Film Simulation Collection](http://rawtherapee.com/shared/HaldCLUT.zip) (HaldCLUT images; ~402 MB). Film-style looks including names evoking Kodak etc.
- **Credits:** Pat David, Pavlov Dmitry, Michael Ezra.
- **License:** Not stated on the page (only credits + trademark disclaimer). Cannot assume permissive/CC0.
- **Use for us:** Not a PP3; not usable as `--preset` for pg-develop. Good for GUI users; we can link to it as an alternative.

### 2. pixlsus/RawTherapee-Presets (GitHub)

- **Reported:** CC0-1.0, PP3 presets (e.g. Acros, Classic Chrome). Often cited as *the* CC0 RawTherapee preset repo.
- **Status:** Repository URL returned 404 at research time (repo may be moved, renamed, or unavailable).
- **Content (from search):** Classic Chrome, Acros mentioned; **no Kodak Portra–named PP3** found in search results.
- **Use for us:** If the repo reappears, we could add e.g. Classic Chrome as a “film-like” alternative and document it; no Kodak-branded PP3 confirmed.

### 3. Other

- **Pat David (blog):** Film emulation presets (G’MIC/GIMP, HaldCLUT); Kodak Portra–style mentioned. License cited elsewhere as CC BY-SA; not PP3 for RawTherapee CLI.
- **TheSquirrelMafia/RawTherapee-PP3-Settings:** General PP3 starter files; no Kodak-specific preset confirmed; license not checked.

## Follow-up research: presets we could use and ship

**Goal:** Find any PP3 we can ship under a clear permissive license (CC0, Unlicense, MIT).

### pixlsus/RawTherapee-Presets

- **Status:** Still **404** (repo and raw content). Cannot use.
- **If it reappears:** CC0-1.0; presets like Classic Chrome, Acros (no Kodak Portra named). Could ship one as a “film-style” alternative with attribution.

### TheSquirrelMafia/RawTherapee-PP3-Settings

- **URL:** [GitHub](https://github.com/TheSquirrelMafia/RawTherapee-PP3-Settings)
- **Content:** Many PP3s, including **Kodak Portra** in `1 - PP3 Files to Install/TSM - Film Simulations/Color Films/`:
  - `Kodak Portra 160.pp3`, `Kodak Portra 160 VC.pp3`
  - `Kodak Portra 400 UC.pp3`, `Kodak Portra 400 VC.pp3`
  - `Kodak Portra 800.pp3`
  - Plus other film presets (Fuji, Kodak Ektar/Kodachrome, Agfa, etc.).
- **License:** **None stated.** No `LICENSE` file in repo root; README has no license or “use freely” wording. Default is “all rights reserved” — we **cannot** ship these without permission or a permissive license.
- **Possible next step:** Open an issue or contact the maintainer (PentaxForums / GitHub) asking whether they would add a permissive license (e.g. CC0 or MIT) so we could bundle one Portra preset with attribution. Until then, we only **link** to the repo in docs so users can download presets themselves.

### RawTherapee bundled profiles

- RawTherapee ships “Bundled profiles” (PP3) in the app; no standalone Kodak-style preset; license follows RawTherapee (GPL). Not a source for a permissively licensed preset to ship in our repo.

### Summary: can we ship anything today?

| Source              | Has Kodak-style PP3? | License we can ship? | Action |
|---------------------|----------------------|----------------------|--------|
| pixlsus             | No (Acros, Classic Chrome) | CC0 (repo 404)       | Cannot use (repo missing). |
| TheSquirrelMafia    | Yes (Portra 160/400/800)   | **No** (none stated)  | Do not ship. Link in docs for user download; optionally ask maintainer for CC0/MIT. |
| RawPedia HaldCLUT   | Film look (HaldCLUT)       | Not stated           | Not PP3; link for GUI users. |

**Conclusion:** We still have **no** preset we can ship without permission. Document TheSquirrelMafia as a source where users can get Kodak Portra PP3s (and add the link in workflow/examples). Optionally add a short “If you want to ship a preset” note: ask TheSquirrelMafia to add CC0/MIT so we can bundle one with attribution.

## Reasons we do not ship a preset

The project does **not** ship a Kodak-style PP3 in `templates/` for these reasons:

1. **License:** We only ship a preset if it has a clear permissive license (CC0, Unlicense, MIT, or equivalent). No Kodak Portra–style PP3 with such a license was found. RawPedia's Film Simulation collection (HaldCLUT) does not state a license; Pat David–style film presets are typically CC BY-SA, which we do not bundle without explicit approval.

2. **Format:** The CLI and `pg-develop` require a **PP3** file. RawPedia's main "film" offering is **HaldCLUT** (GUI only), not PP3, so it cannot be used as our default preset.

3. **Availability:** The only widely cited CC0 PP3 collection (pixlsus/RawTherapee-Presets) was unavailable (404) at research time and does not list a Kodak Portra PP3 in search results.

4. **User path:** Users can provide their own PP3 via `RAWTHERAPEE_PRESET`, `--preset`, or by placing a file at `templates/rawtherapee-kodak-portra.pp3`. We document RawPedia and "community PP3 or create in RawTherapee" as alternatives.

See this document for full research; workflow and examples docs reference why no preset is shipped.

## Conclusion

- **No permissively licensed (CC0/Unlicense/MIT) Kodak Portra–named PP3** was found that we can reliably ship.
- **RawPedia Film Simulation** = HaldCLUT (GUI), not PP3; useful to document as alternative for GUI users.
- **Recommendation:** Do **not** add a preset file to the repo. Keep docs and script as-is: optional `templates/rawtherapee-kodak-portra.pp3`, else `RAWTHERAPEE_PRESET` or `--preset`; point users to RawPedia for film-style looks and to “use a PP3 from community or create one in RawTherapee” for CLI.

