# Konfiguration

*[English Version](configuration.en.md)*

PixelGroomer wird über mehrere Ebenen konfiguriert. Diese Anleitung erklärt alle Optionen.

## Setup

Vor der ersten Nutzung muss das Setup ausgeführt werden:

```bash
./setup.sh
```

Das Setup erstellt:
- **`.venv/`** - Python virtual environment mit allen Abhängigkeiten
- **`.env`** - Konfigurationsdatei (aus `.env.example`)

Alle Scripts prüfen automatisch das venv und zeigen einen Fehler, falls es fehlt:

```
[ERROR] Python virtual environment not found!

Please run the setup script first:

    /path/to/pixelGroomer/setup.sh
```

### Makefile-Befehle

```bash
make setup         # Setup ausführen
make check         # Abhängigkeiten prüfen
make deps          # Externe Tools installieren (macOS)
make clean         # venv entfernen
make test          # Alle Tests ausführen
make test-fast     # Langsame Tests überspringen
make test-coverage # Coverage-Report erstellen
make lint          # ShellCheck auf allen Scripts ausführen
```

## Konfigurations-Priorität

Einstellungen werden in dieser Reihenfolge geladen (spätere überschreiben frühere):

```
1. SD-Karte (.import.yaml)     ← niedrigste Priorität
2. Projekt (.env)              
3. CLI-Argumente               ← höchste Priorität
4. Interaktive Abfrage         ← nur wenn Wert fehlt
```

**Beispiel:**
```bash
# .import.yaml auf SD-Karte hat: event="Test"
# .env hat: DEFAULT_AUTHOR="Max"
# CLI: pg-import /sd --event "Hochzeit"

# Ergebnis:
# - Event: "Hochzeit" (CLI gewinnt)
# - Author: "Max" (.env, da kein CLI-Override)
```

## Globale Konfiguration (.env)

Erstelle die Datei im Projektverzeichnis:

```bash
cp .env.example .env
```

### Pfade

```bash
# Haupt-Archiv für alle Fotos
PHOTO_LIBRARY="$HOME/Pictures/PhotoLibrary"

# Verzeichnis für Symlink-Alben
ALBUM_DIR="$HOME/Pictures/Albums"

# Standard-Export-Verzeichnis
EXPORT_DIR="$HOME/Pictures/Export"
```

### Ordnerstruktur

```bash
# Pattern für die Ordnerorganisation
# Verfügbare Platzhalter: {year}, {month}, {day}
FOLDER_STRUCTURE="{year}-{month}-{day}"

# Beispiele:
# {year}-{month}-{day}        → 2026-01-24/
# {year}/{month}/{day}        → 2026/01/24/
# {year}-{month}/{day}        → 2026-01/24/
# {year}/{year}-{month}-{day} → 2026/2026-01-24/
```

### Metadaten-Defaults

```bash
# Standard-Author für alle Importe
DEFAULT_AUTHOR="Max Mustermann"

# Standard-Copyright
DEFAULT_COPYRIGHT="© 2026 Max Mustermann"
```

### Dateinamen-Pattern

```bash
# Verfügbare Platzhalter:
#   {date}   - YYYYMMDD aus EXIF
#   {time}   - HHMMSS aus EXIF
#   {event}  - Event-Name
#   {seq}    - Sequenznummer ({seq:03d} für Padding)
#   {camera} - Kameramodell aus EXIF
NAMING_PATTERN="{date}_{event}_{seq:03d}"

# Beispiele:
# {date}_{event}_{seq:03d}     → 20260124_Hochzeit_001.jpg
# {date}_{time}_{seq:03d}      → 20260124_143022_001.jpg
# {event}_{date}_{seq:03d}     → Hochzeit_20260124_001.jpg
```

### RAW-Entwicklung

```bash
# Bevorzugter Prozessor: darktable oder imagemagick
RAW_PROCESSOR="darktable"

# JPEG-Qualität (1-100)
JPEG_QUALITY=92

# Standard-Darktable-Preset (leer = keins)
DARKTABLE_STYLE=""
```

### Unterstützte Formate

```bash
# RAW-Formate (case-insensitive)
RAW_EXTENSIONS="cr2,cr3,nef,arw,raf,dng,orf,rw2"

# Bild-Formate
IMAGE_EXTENSIONS="jpg,jpeg,png,tiff,tif,heic,heif"
```

### Import-Verhalten

```bash
# Vor dem Löschen der Quelle fragen
CONFIRM_DELETE="true"

# Checksums beim Import generieren
GENERATE_CHECKSUMS="true"

# Checksum-Algorithmus (sha256 oder md5)
CHECKSUM_ALGORITHM="sha256"

# Archiv-Verzeichnis bei jedem Import interaktiv abfragen
# Wenn true, wird vor jedem Import nach dem Zielverzeichnis gefragt
# CLI --output überschreibt diese Abfrage
PROMPT_ARCHIVE_DIR="false"
```

### Python Virtual Environment

Das venv wird automatisch vom Setup erstellt. Falls du es manuell verwalten möchtest:

```bash
# venv erstellen
python3 -m venv .venv

# Aktivieren
source .venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

Die Scripts nutzen das venv automatisch ohne Aktivierung - sie rufen direkt `.venv/bin/python` auf.

## Per-Import Konfiguration (.import.yaml)

Lege diese Datei auf der SD-Karte ab:
- `/DCIM/.import.yaml` (empfohlen)
- `/.import.yaml` (Root der Karte)

### Basis-Optionen

```yaml
# Event-Name (wird für Dateinamen und EXIF verwendet)
event: "Hochzeit Meyer"

# Ort für EXIF-Metadaten
location: "Berlin, Germany"

# Author überschreiben (optional)
# Wird von .env DEFAULT_AUTHOR überschrieben!
author: "Max Mustermann"

# Ziel-Archiv für diesen Import (optional)
# Wird von .env PHOTO_LIBRARY überschrieben!
archive: "/Volumes/PhotoArchive/2026"
```

**Wichtig:** Werte in `.import.yaml` haben die niedrigste Priorität. Sie werden von `.env` und CLI-Argumenten überschrieben. Die Datei eignet sich gut für Event-spezifische Defaults, die bei Bedarf überschrieben werden können.

### Erweiterte Optionen

```yaml
# Keywords für EXIF
tags:
  - wedding
  - family
  - outdoor

# Notizen (nicht in Dateien geschrieben)
notes: "Tag 1 der Hochzeit, Zeremonie und Empfang"

# Naming-Pattern überschreiben
pattern: "{date}_{time}_{event}_{seq:03d}"

# GPS-Koordinaten für alle Fotos setzen
gps: "52.5200,13.4050"
```

### Mehrere Events pro SD-Karte

Wenn du mehrere Events auf einer Karte hast, kannst du verschiedene `.import.yaml` in DCIM-Unterordnern verwenden:

```
SD-Karte/
├── DCIM/
│   ├── 100CANON/
│   │   ├── .import.yaml  ← event: "Event 1"
│   │   └── IMG_001.CR3
│   └── 101CANON/
│       ├── .import.yaml  ← event: "Event 2"
│       └── IMG_100.CR3
```

## CLI-Argumente

CLI-Argumente haben immer die höchste Priorität:

```bash
pg-import /source [optionen]

Optionen:
  -e, --event <name>    Event-Name
  -l, --location <loc>  Ort
  -a, --author <name>   Author
  -o, --output <dir>    Ziel-Archiv
  -n, --dry-run         Vorschau ohne Änderungen
  --no-delete           Quelle nicht löschen
  -v, --verbose         Detaillierte Ausgabe
```

**Beispiele:**

```bash
# Event und Location überschreiben
pg-import /Volumes/SD --event "Geburtstag" --location "München"

# In spezifisches Archiv importieren
pg-import /Volumes/SD --output /Volumes/Backup/Photos

# Vorschau ohne Änderungen
pg-import /Volumes/SD --dry-run --verbose
```

## Umgebungsvariablen

Alle `.env`-Variablen können auch als Umgebungsvariablen gesetzt werden:

```bash
# Temporär für einen Befehl
PHOTO_LIBRARY=/tmp/test pg-import /source --event "Test"

# In der Shell-Session
export PHOTO_LIBRARY="/Volumes/Archive"
pg-import /source --event "Test"
```

## Beispiel-Konfigurationen

### Minimale .env

```bash
PHOTO_LIBRARY="$HOME/Pictures/Archiv"
DEFAULT_AUTHOR="Max Mustermann"
```

### Vollständige .env

```bash
# Pfade
PHOTO_LIBRARY="$HOME/Pictures/PhotoLibrary"
ALBUM_DIR="$HOME/Pictures/Albums"
EXPORT_DIR="$HOME/Pictures/Export"

# Struktur
FOLDER_STRUCTURE="{year}-{month}-{day}"
NAMING_PATTERN="{date}_{event}_{seq:03d}"

# Metadaten
DEFAULT_AUTHOR="Max Mustermann"
DEFAULT_COPYRIGHT="© 2026 Max Mustermann"

# RAW-Entwicklung
RAW_PROCESSOR="darktable"
JPEG_QUALITY=92
DARKTABLE_STYLE="vivid"

# RAW-Formate
RAW_EXTENSIONS="cr2,cr3,nef,arw,raf,dng,orf,rw2"
IMAGE_EXTENSIONS="jpg,jpeg,png,tiff,tif,heic,heif"

# Verhalten
CONFIRM_DELETE="true"
GENERATE_CHECKSUMS="true"
CHECKSUM_ALGORITHM="sha256"
PROMPT_ARCHIVE_DIR="false"
```

### Typische .import.yaml

```yaml
event: "Hochzeit Meyer"
location: "Berlin"
tags:
  - wedding
  - family
```

---

Zurück zum [Workflow](workflow.de.md) | Weiter zur [Script-Referenz](scripts.de.md)
