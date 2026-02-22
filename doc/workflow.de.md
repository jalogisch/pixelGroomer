# PixelGroomer Workflow

*[English Version](workflow.en.md)*

Dieses Dokument beschreibt den typischen Foto-Workflow mit PixelGroomer - vom Import bis zum Teilen.

## Voraussetzungen

Vor der ersten Nutzung muss das Setup ausgeführt werden:

```bash
# Externe Tools installieren (macOS)
brew install exiftool python3 darktable imagemagick

# Setup ausführen (erstellt venv, .env, etc.)
./setup.sh
```

Das Setup:
- Erstellt ein Python virtual environment (`.venv/`)
- Installiert Python-Abhängigkeiten (PyYAML)
- Prüft externe Tools
- Erstellt `.env` aus Template

Alle Scripts prüfen automatisch, ob das venv existiert und zeigen einen Fehler mit Verweis auf `setup.sh`, falls nicht.

## Übersicht

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  SD-Karte   │────▶│   Import    │────▶│   Archiv    │────▶│   Teilen    │
│  (Kamera)   │     │  pg-import  │     │  sortiert   │     │  pg-develop │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                   │
                           ▼                   ▼
                    ┌─────────────┐     ┌─────────────┐
                    │   EXIF      │     │   Alben     │
                    │  pg-exif    │     │  pg-album   │
                    └─────────────┘     └─────────────┘
```

## Phase 1: Vorbereitung (optional)

Vor dem Shooting kannst du eine `.import.yaml` auf der SD-Karte vorbereiten:

```bash
# Auf SD-Karte erstellen: /DCIM/.import.yaml
cat > /Volumes/EOS_DIGITAL/DCIM/.import.yaml << 'EOF'
event: "Hochzeit Meyer"
location: "Stadtoldendorf"
tags:
  - wedding
  - outdoor
EOF
```

Diese Datei wird beim Import automatisch erkannt und als Basis-Konfiguration verwendet.

## Phase 2: Import

### Einfacher Import

```bash
# Mit Event als CLI-Argument (überschreibt .import.yaml)
pg-import /Volumes/EOS_DIGITAL --event "Endurotraining" --location "Stadtoldendorf"

# Nutzt .import.yaml oder fragt interaktiv
pg-import /Volumes/EOS_DIGITAL

# In ein spezifisches Archiv importieren
pg-import /Volumes/EOS_DIGITAL --output /Volumes/PhotoArchive/2026
```

### Trip- / Mehrtage-Import

Bei einer Tour oder einem Mehrtage-Shooting reicht ein Import mit `--trip`: keine Abfrage nach Event oder Ort. Dateien landen nach EXIF-Datum in einem Ordner pro Tag (z.B. `2026-01-24/`, `2026-01-25/`). Ohne gesetztes Event sind die Dateinamen nur aus Datum und Sequenz (z.B. `20260124_001.jpg`). Event und Ort können weiterhin in `.import.yaml` auf der Karte stehen; sie werden genutzt, wenn vorhanden.

```bash
pg-import /Volumes/CARD --trip
```

### Identitätsdatei für alle Karten

Kopiere `templates/.import.yaml.identity` auf jede SD-Karte als `DCIM/.import.yaml`. Sie setzt Author, Copyright (z.B. Unlicense) und Credit (Künstlername). Event und Ort für Trip-Import ungesetzt lassen.

### Urlaubs-Import (SD-Karte)

Nach dem Urlaub alle Fotos von der SD-Karte importieren — ohne Event und Ort, nur Autor, Copyright und Credit (Identität). `templates/.import.yaml.identity` als `DCIM/.import.yaml` auf die Karte kopieren oder .env nutzen. Import im Trip-Modus: ein Ordner pro Tag, Dateinamen nur mit Datum und Sequenz:

```bash
pg-import /Volumes/CARD --trip --no-delete
```

Oder das Wrapper-Skript: `./examples/holiday-import.sh /Volumes/CARD`

### Was passiert beim Import?

1. **Konfiguration laden** (Priorität: SD-Karte → .env → CLI)
2. **Dateien scannen** - Alle RAW und JPG Dateien finden
3. **Nach Datum sortieren** - EXIF-Datum auslesen
4. **Ordner erstellen** - z.B. `2026-01-24/`
5. **Kopieren & Umbenennen** - z.B. `20260124_Hochzeit_001.cr3`
6. **EXIF-Tags setzen** - Author, Copyright, Event, Location
7. **Checksums generieren** - Für Integritätsprüfung
8. **Optional: Quelle löschen** - Nach Bestätigung

### Ergebnis-Struktur

```
PhotoLibrary/
├── 2026-01-24/                         # Ordnerstruktur: {year}-{month}-{day}
│   ├── 20260124_Hochzeit_001.cr3
│   ├── 20260124_Hochzeit_002.cr3
│   ├── 20260124_Hochzeit_003.jpg
│   └── .checksums
├── 2026-01-25/
│   └── ...
```

Die Ordnerstruktur ist über `FOLDER_STRUCTURE` in `.env` konfigurierbar (siehe [Konfiguration](configuration.md)).

## Phase 3: Auswahl & Organisation

### Alben erstellen

Nach dem Import wählst du deine besten Fotos aus und organisierst sie in Alben:

```bash
# Album erstellen
pg-album create "Alps_Tour_Highlights"

# Beste Fotos hinzufügen (Symlinks, kein Speicherverbrauch)
pg-album add "Alps_Tour_Highlights" \
    ~/Pictures/PhotoLibrary/2026-01-24/20260124_Hochzeit_001.cr3 \
    ~/Pictures/PhotoLibrary/2026-01-24/20260124_Hochzeit_015.cr3 \
    ~/Pictures/PhotoLibrary/2026-01-24/20260124_Hochzeit_042.jpg

# Oder mit Wildcards
pg-album add "Alps_Tour_Highlights" ~/Pictures/PhotoLibrary/2026-01-24/*.jpg
```

### Album-Struktur

```
Albums/
├── Alps_Tour_Highlights/
│   ├── 20260124_Hochzeit_001.cr3 -> ../../PhotoLibrary/2026-01-24/...
│   ├── 20260124_Hochzeit_015.cr3 -> ...
│   └── 20260124_Hochzeit_042.jpg -> ...
└── .albums.json
```

**Vorteile von Symlink-Alben:**
- Kein zusätzlicher Speicherplatz
- Originale bleiben im Archiv
- Ein Foto kann in mehreren Alben sein
- Einfaches Hinzufügen/Entfernen

### Album-Verwaltung

```bash
# Alle Alben anzeigen
pg-album list

# Album-Inhalt anzeigen
pg-album show "Alps_Tour_Highlights"

# Album-Info (Größe, Anzahl, etc.)
pg-album info "Alps_Tour_Highlights"

# Foto aus Album entfernen (Original bleibt)
pg-album remove "Alps_Tour_Highlights" foto.jpg
```

## Phase 4: RAW-Entwicklung

### Für Social Media / Teilen

```bash
# Alle RAWs eines Ordners entwickeln
pg-develop ~/Pictures/PhotoLibrary/2026-01-24/*.cr3 \
    --output ~/Pictures/Export/Hochzeit/

# Mit Resize für Web
pg-develop ~/Pictures/PhotoLibrary/2026-01-24/*.cr3 \
    --output ~/Pictures/Export/Web/ \
    --resize 1920x \
    --quality 85

# Album entwickeln
pg-album export "Alps_Tour_Highlights" --to /tmp/highlights_raw/
pg-develop /tmp/highlights_raw/*.cr3 --output ~/Desktop/ForRiders/
```

### Darktable-Presets nutzen

Wenn du in Darktable Presets/Styles erstellt hast:

```bash
# Mit spezifischem Preset
pg-develop photo.cr3 --preset "vivid" --quality 95

# Preset in .env als Standard setzen
echo 'DARKTABLE_STYLE="mein_preset"' >> .env
```

### XMP-Sidecars

Wenn du RAWs in Darktable bearbeitet hast, werden die XMP-Sidecars automatisch verwendet:

```
photo.cr3           # RAW-Datei
photo.cr3.xmp       # Darktable-Bearbeitungen
```

```bash
# pg-develop nutzt automatisch die XMP-Einstellungen
pg-develop photo.cr3 --output ./export/
```

### RAW-Entwicklung per Kommandozeile – Alternativen

pg-develop unterstützt drei Prozessoren (per `--processor` oder `RAW_PROCESSOR` in .env):

- **Darktable** — Hochwertige RAW-Verarbeitung, Presets und XMP-Sidecars. Install: `brew install darktable`
- **ImageMagick** — Schneller, einfacher (nutzt dcraw). Install: `brew install imagemagick`
- **RawTherapee** — PP3-Presets und Filmsimulation (z. B. Kodak-Looks). Install: `brew install rawtherapee`

Resize (`--resize`) wird nur beim ImageMagick-Prozessor angewendet.

Andere CLI-Tools (z. B. **sips** unter macOS, **dcraw**/ufraw) können manuell genutzt werden, sind aber nicht in pg-develop integriert.

## Phase 5: Teilen & Export

### Album für Familie/Freunde exportieren

```bash
# Album als echte Kopien exportieren (nicht Symlinks)
pg-album export "Alps_Tour_Highlights" --to ~/Desktop/ForRiders/

# JPGs aus RAWs erstellen
pg-develop ~/Desktop/ForRiders/*.cr3 \
    --output ~/Desktop/ForRiders/ \
    --quality 90

# RAWs entfernen, nur JPGs behalten
rm ~/Desktop/ForRiders/*.cr3
```

### Für verschiedene Plattformen

```bash
# Instagram (1080px, hohe Qualität)
pg-develop ./photos/*.cr3 \
    --output ./instagram/ \
    --resize 1080x \
    --quality 95

# WhatsApp (kleiner, schneller Upload)
pg-develop ./photos/*.cr3 \
    --output ./whatsapp/ \
    --resize 1600x \
    --quality 80

# Druck (volle Auflösung)
pg-develop ./photos/*.cr3 \
    --output ./print/ \
    --quality 100
```

## Phase 6: Wartung & Backup

### Integrität prüfen

```bash
# Checksums für neues Archiv generieren
pg-verify ~/Pictures/PhotoLibrary --generate

# Regelmäßig prüfen
pg-verify ~/Pictures/PhotoLibrary --check

# Nach Backup prüfen
pg-verify /Volumes/Backup/PhotoLibrary --check
```

### Metadaten nachträglich ändern

```bash
# Author für alle Fotos eines Events setzen
pg-exif ~/Pictures/PhotoLibrary/2026-01-24/ \
    --author "Max Mustermann" \
    --copyright "© 2026 Max Mustermann"

# Location nachträglich hinzufügen
pg-exif ~/Pictures/PhotoLibrary/2026-01-24/ \
    --location "Stadtoldendorf, Germany" \
    --gps "52.52,13.405"

# Metadaten anzeigen
pg-exif photo.jpg --show
```

## Typischer Tagesablauf

```bash
# 1. Nach dem Shooting: SD-Karte einstecken
# 2. Import starten
pg-import /Volumes/EOS_DIGITAL --event "Stadtfest"

# 3. In Darktable/Lightroom sichten und bearbeiten
open -a Darktable ~/Pictures/PhotoLibrary/2026-01-24/

# 4. Beste Fotos markieren und Album erstellen
pg-album create "Stadtfest_Best"
pg-album add "Stadtfest_Best" ~/Pictures/PhotoLibrary/2026-01-24/20260124_Stadtfest_{001,015,023,042}.cr3

# 5. Für Social Media entwickeln
pg-develop ~/Pictures/PhotoLibrary/2026-01-24/*.cr3 \
    --output ~/Pictures/Export/Stadtfest/ \
    --resize 1920x

# 6. Fertig! Fotos sind:
#    - Im Archiv organisiert: ~/Pictures/PhotoLibrary/2026-01-24/
#    - Im Album verlinkt: ~/Pictures/Albums/Stadtfest_Best/
#    - Zum Teilen bereit: ~/Pictures/Export/Stadtfest/
```

## Tipps

### SD-Karten-Workflow optimieren

1. **Vor jedem Shooting:** `.import.yaml` auf SD-Karte erstellen
2. **Mehrere Events pro Karte?** Verschiedene `.import.yaml` pro DCIM-Unterordner
3. **Backup-Karte?** Gleiche `.import.yaml` auf beide Karten

### Speicherplatz sparen

- **Alben nutzen:** Symlinks statt Kopien
- **Originale behalten:** RAWs nur einmal im Archiv
- **Export löschen:** Nach dem Teilen können Exports gelöscht werden

### Datensicherheit

```bash
# Nach jedem Import: Checksums generieren
pg-verify ~/Pictures/PhotoLibrary --update

# Vor dem Backup: Integrität prüfen
pg-verify ~/Pictures/PhotoLibrary --check

# Nach dem Backup: Backup verifizieren
pg-verify /Volumes/Backup/PhotoLibrary --check
```

### Nach System-Updates

Falls Python aktualisiert wurde, kann das venv ungültig werden:

```bash
# venv neu erstellen
./setup.sh

# Oder manuell
rm -rf .venv && ./setup.sh
```

---

Weiter zur [Konfiguration](configuration.de.md) | [Script-Referenz](scripts.de.md)
