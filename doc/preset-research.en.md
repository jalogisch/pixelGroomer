# RawTherapee Kodak-style preset research

*[Deutsche Version](preset-research.de.md)*

This document records why the project does not ship a Kodak-style PP3 preset and where you can get one. The Adventure Camp workflow uses `pg-develop --processor rawtherapee --preset <path>.pp3`.

## How RawTherapee "Kodak" looks work

| Mechanism | Format | Used by | Notes |
|-----------|--------|---------|--------|
| **Processing profile (PP3)** | `.pp3` text file | `rawtherapee-cli -p <path>` / pg-develop | Full tool settings; what our script expects. |
| **Film Simulation** | HaldCLUT (PNG/TIFF) | RawTherapee GUI only | RawPedia "Film Simulation" = HaldCLUT collection; not applied via CLI `-p`. |

For **CLI** (and our script), you need a **PP3** file. The RawPedia Film Simulation page is about **HaldCLUT** (GUI workflow), not PP3.

## Sources checked

### 1. RawPedia Film Simulation (HaldCLUT)

- **URL:** [Film Simulation](https://rawpedia.rawtherapee.com/Film_Simulation)
- **Content:** [RawTherapee Film Simulation Collection](http://rawtherapee.com/shared/HaldCLUT.zip) (HaldCLUT images; ~402 MB). Film-style looks including names evoking Kodak etc.
- **Credits:** Pat David, Pavlov Dmitry, Michael Ezra.
- **License:** Not stated on the page (only credits + trademark disclaimer). Cannot assume permissive/CC0.
- **Use for us:** Not a PP3; not usable as `--preset` for pg-develop. Good for GUI users; we link to it as an alternative.

### 2. pixlsus/RawTherapee-Presets (GitHub)

- **Reported:** CC0-1.0, PP3 presets (e.g. Acros, Classic Chrome). Often cited as the CC0 RawTherapee preset repo.
- **Status:** Repository URL returned 404 at research time (repo may be moved, renamed, or unavailable).
- **Content (from search):** Classic Chrome, Acros mentioned; **no Kodak Portra–named PP3** found in search results.
- **Use for us:** If the repo reappears, we could add e.g. Classic Chrome as a "film-like" alternative with attribution; no Kodak-branded PP3 confirmed.

### 3. Pat David (blog)

- Film emulation presets (G'MIC/GIMP, HaldCLUT); Kodak Portra–style mentioned. License cited elsewhere as CC BY-SA; not PP3 for RawTherapee CLI.

### 4. TheSquirrelMafia/RawTherapee-PP3-Settings (GitHub)

- **URL:** [GitHub](https://github.com/TheSquirrelMafia/RawTherapee-PP3-Settings)
- **Content:** Many PP3s, including **Kodak Portra** in `1 - PP3 Files to Install/TSM - Film Simulations/Color Films/`:
  - `Kodak Portra 160.pp3`, `Kodak Portra 160 VC.pp3`
  - `Kodak Portra 400 UC.pp3`, `Kodak Portra 400 VC.pp3`
  - `Kodak Portra 800.pp3`
  - Plus other film presets (Fuji, Kodak Ektar/Kodachrome, Agfa, etc.).
- **License:** **None stated.** No `LICENSE` file in repo root; README has no license or "use freely" wording. Default is "all rights reserved" — we **cannot** ship these without permission or a permissive license.
- **For users:** You can download presets from this repo and use them with `--preset` or `RAWTHERAPEE_PRESET`. We only link; we do not bundle.

### 5. RawTherapee bundled profiles

- RawTherapee ships "Bundled profiles" (PP3) in the app; no standalone Kodak-style preset; license follows RawTherapee (GPL). Not a source for a permissively licensed preset to ship in our repo.

## Summary: can we ship anything today?

| Source              | Has Kodak-style PP3? | License we can ship? | Action |
|---------------------|----------------------|----------------------|--------|
| pixlsus             | No (Acros, Classic Chrome) | CC0 (repo 404)       | Cannot use (repo missing). |
| TheSquirrelMafia    | Yes (Portra 160/400/800)   | **No** (none stated)  | Do not ship. Link in docs for user download; optionally ask maintainer for CC0/MIT. |
| RawPedia HaldCLUT   | Film look (HaldCLUT)       | Not stated           | Not PP3; link for GUI users. |

**Conclusion:** We have **no** preset we can ship without permission. We document TheSquirrelMafia as a source where you can get Kodak Portra PP3s.

## Reasons we do not ship a preset

The project does **not** ship a Kodak-style PP3 in `templates/` for these reasons:

1. **License:** We only ship a preset if it has a clear permissive license (CC0, Unlicense, MIT, or equivalent). No Kodak Portra–style PP3 with such a license was found. RawPedia's Film Simulation collection (HaldCLUT) does not state a license; Pat David–style film presets are typically CC BY-SA, which we do not bundle without explicit approval.

2. **Format:** The CLI and `pg-develop` require a **PP3** file. RawPedia's main "film" offering is **HaldCLUT** (GUI only), not PP3, so it cannot be used as our default preset.

3. **Availability:** The only widely cited CC0 PP3 collection (pixlsus/RawTherapee-Presets) was unavailable (404) at research time and does not list a Kodak Portra PP3 in search results.

4. **User path:** You can provide your own PP3 via `RAWTHERAPEE_PRESET`, `--preset`, or by placing a file at `templates/rawtherapee-kodak-portra.pp3`. We document RawPedia and TheSquirrelMafia so you can download or create a PP3.

## Recommendation

- Do **not** add a preset file to the repo. Use a PP3 from the community (e.g. [TheSquirrelMafia/RawTherapee-PP3-Settings](https://github.com/TheSquirrelMafia/RawTherapee-PP3-Settings), *TSM - Film Simulations / Color Films*) or create one in RawTherapee. For GUI-only film looks, use [RawPedia Film Simulation](https://rawpedia.rawtherapee.com/Film_Simulation) (HaldCLUT).
