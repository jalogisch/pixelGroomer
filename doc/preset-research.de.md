# RawTherapee Kodak-Preset-Recherche

*[English Version](preset-research.en.md)*

Dieses Dokument erläutert, warum das Projekt kein Kodak-PP3-Preset mitliefert und wo du eines bekommen kannst. Der Adventure-Camp-Workflow nutzt `pg-develop --processor rawtherapee --preset <path>.pp3`.

## Wie „Kodak“-Looks in RawTherapee funktionieren

| Mechanismus      | Format            | Verwendung                    | Anmerkung |
|------------------|------------------|-------------------------------|-----------|
| **Verarbeitungsprofil (PP3)** | `.pp3`-Textdatei | `rawtherapee-cli -p <path>` / pg-develop | Volle Werkzeugeinstellungen; das erwartet unser Script. |
| **Film Simulation** | HaldCLUT (PNG/TIFF) | Nur RawTherapee-GUI | RawPedia „Film Simulation“ = HaldCLUT-Sammlung; nicht per CLI `-p` anwendbar. |

Für die **CLI** (und unser Script) brauchst du eine **PP3**-Datei. Die RawPedia-Seite Film Simulation bezieht sich auf **HaldCLUT** (GUI-Workflow), nicht auf PP3.

## Geprüfte Quellen

### 1. RawPedia Film Simulation (HaldCLUT)

- **URL:** [Film Simulation](https://rawpedia.rawtherapee.com/Film_Simulation)
- **Inhalt:** [RawTherapee Film Simulation Collection](http://rawtherapee.com/shared/HaldCLUT.zip) (HaldCLUT-Bilder; ~402 MB). Film-Looks inkl. Namen wie Kodak usw.
- **Credits:** Pat David, Pavlov Dmitry, Michael Ezra.
- **Lizenz:** Auf der Seite nicht angegeben (nur Credits + Marken-Hinweis). Keine Annahme permissiv/CC0.
- **Für uns:** Kein PP3; nicht als `--preset` für pg-develop nutzbar. Gut für GUI-Nutzer; wir verlinken es als Alternative.

### 2. pixlsus/RawTherapee-Presets (GitHub)

- **Berichtet:** CC0-1.0, PP3-Presets (z. B. Acros, Classic Chrome). Oft als CC0-RawTherapee-Preset-Repo genannt.
- **Status:** Repository-URL zum Recherchezeitpunkt 404 (Repo evtl. umgezogen/umbenannt/nicht verfügbar).
- **Inhalt (aus Suche):** Classic Chrome, Acros erwähnt; **kein Kodak Portra–PP3** in Suchergebnissen.
- **Für uns:** Falls das Repo wieder erscheint, könnten wir z. B. Classic Chrome als „film-ähnlich“ mit Quellenangabe einbinden; kein Kodak-PP3 bestätigt.

### 3. Pat David (Blog)

- Film-Emulations-Presets (G'MIC/GIMP, HaldCLUT); Kodak Portra–Stil erwähnt. Lizenz anderswo als CC BY-SA; nicht PP3 für RawTherapee-CLI.

### 4. TheSquirrelMafia/RawTherapee-PP3-Settings (GitHub)

- **URL:** [GitHub](https://github.com/TheSquirrelMafia/RawTherapee-PP3-Settings)
- **Inhalt:** Viele PP3s, u. a. **Kodak Portra** unter `1 - PP3 Files to Install/TSM - Film Simulations/Color Films/`:
  - `Kodak Portra 160.pp3`, `Kodak Portra 160 VC.pp3`
  - `Kodak Portra 400 UC.pp3`, `Kodak Portra 400 VC.pp3`
  - `Kodak Portra 800.pp3`
  - sowie weitere Film-Presets (Fuji, Kodak Ektar/Kodachrome, Agfa usw.).
- **Lizenz:** **Nicht angegeben.** Keine `LICENSE`-Datei im Repo; README ohne Lizenz oder „frei nutzbar“. Default: „alle Rechte vorbehalten“ — wir **dürfen** diese nicht ohne Erlaubnis oder permissive Lizenz mitliefern.
- **Für Nutzer:** Du kannst Presets aus diesem Repo herunterladen und mit `--preset` oder `RAWTHERAPEE_PRESET` nutzen. Wir verlinken nur; wir bündeln nicht.

### 5. RawTherapee gebündelte Profile

- RawTherapee liefert „Bundled profiles“ (PP3) mit der App; kein eigenständiges Kodak-Preset; Lizenz wie RawTherapee (GPL). Keine Quelle für ein permissiv lizenziertes Preset zum Mitliefern in unserem Repo.

## Zusammenfassung: Können wir etwas mitliefern?

| Quelle            | Hat Kodak-PP3?        | Lizenz zum Mitliefern? | Aktion |
|-------------------|----------------------|------------------------|--------|
| pixlsus           | Nein (Acros, Classic Chrome) | CC0 (Repo 404)         | Nicht nutzbar (Repo fehlt). |
| TheSquirrelMafia   | Ja (Portra 160/400/800)      | **Nein** (keine angegeben) | Nicht mitliefern. In Doku verlinken zum Selbst-Download; optional Maintainer um CC0/MIT bitten. |
| RawPedia HaldCLUT | Film-Look (HaldCLUT)  | Nicht angegeben        | Kein PP3; für GUI-Nutzer verlinken. |

**Fazit:** Wir haben **kein** Preset, das wir ohne Erlaubnis mitliefern können. Wir dokumentieren TheSquirrelMafia als Quelle, von der du Kodak-Portra-PP3s bekommen kannst.

## Gründe, warum wir kein Preset mitliefern

Das Projekt liefert **kein** Kodak-PP3 in `templates/` aus folgenden Gründen:

1. **Lizenz:** Wir liefern nur ein Preset mit, wenn es eine klare permissive Lizenz hat (CC0, Unlicense, MIT o. ä.). Es wurde kein Kodak-Portra–PP3 mit einer solchen Lizenz gefunden. Die RawPedia-Film-Simulation-Sammlung (HaldCLUT) nennt keine Lizenz; Pat-David–Presets sind typischerweise CC BY-SA, die wir ohne ausdrückliche Zustimmung nicht bündeln.

2. **Format:** CLI und `pg-develop` benötigen eine **PP3**-Datei. Das Hauptangebot von RawPedia für „Film“ ist **HaldCLUT** (nur GUI), kein PP3, und kann daher nicht als Standard-Preset genutzt werden.

3. **Verfügbarkeit:** Die einzige oft genannte CC0-PP3-Sammlung (pixlsus/RawTherapee-Presets) war zum Recherchezeitpunkt nicht verfügbar (404) und listet kein Kodak-Portra-PP3 in Suchergebnissen.

4. **Nutzerweg:** Du kannst ein eigenes PP3 über `RAWTHERAPEE_PRESET`, `--preset` oder eine Datei unter `templates/rawtherapee-kodak-portra.pp3` bereitstellen. Wir dokumentieren RawPedia und TheSquirrelMafia, damit du ein PP3 herunterladen oder erstellen kannst.

## Empfehlung

- **Kein** Preset ins Repo aufnehmen. Nutze ein PP3 aus der Community (z. B. [TheSquirrelMafia/RawTherapee-PP3-Settings](https://github.com/TheSquirrelMafia/RawTherapee-PP3-Settings), *TSM - Film Simulations / Color Films*) oder erstelle eines in RawTherapee. Für reine GUI-Film-Looks: [RawPedia Film Simulation](https://rawpedia.rawtherapee.com/Film_Simulation) (HaldCLUT).
