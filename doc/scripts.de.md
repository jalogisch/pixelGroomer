# Script-Referenz

*[English Version](scripts.en.md)*

Detaillierte Dokumentation aller PixelGroomer-Scripts.

## Voraussetzungen

Alle Scripts erfordern ein eingerichtetes Python virtual environment. Falls nicht vorhanden:

```bash
./setup.sh
```

Die Scripts prüfen automatisch das venv und zeigen einen Fehler mit Anleitung, falls es fehlt.

## pg-import

Importiert Fotos von SD-Karten oder Verzeichnissen mit automatischer Organisation.

### Syntax

```bash
pg-import <source> [optionen]
```

### Argumente

| Argument | Beschreibung |
|----------|--------------|
| `<source>` | Quellverzeichnis (z.B. `/Volumes/EOS_DIGITAL`) |

### Optionen

| Option | Kurz | Beschreibung |
|--------|------|--------------|
| `--event <name>` | `-e` | Event-Name für Metadaten und Dateinamen |
| `--location <loc>` | `-l` | Ort für EXIF-Metadaten |
| `--author <name>` | `-a` | Author überschreiben |
| `--output <dir>` | `-o` | Ziel-Archiv (überschreibt PHOTO_LIBRARY und .import.yaml) |
| `--dry-run` | `-n` | Vorschau ohne Änderungen |
| `--no-delete` | | Quelle nicht löschen (auch nicht fragen) |
| `--trip` | `-t` | Trip-Modus: keine Abfrage für Event/Ort; Dateinamen nur aus Datum+Sequenz, wenn kein Event gesetzt |
| `--verbose` | `-v` | Detaillierte Ausgabe |
| `--help` | `-h` | Hilfe anzeigen |

### Konfigurations-Priorität

Einstellungen werden in dieser Reihenfolge geladen (spätere überschreiben frühere):

1. `.import.yaml` auf SD-Karte (niedrigste Priorität)
2. `.env` Konfigurationsdatei
3. CLI-Argumente (höchste Priorität)
4. Interaktive Abfrage (nur wenn Wert fehlt)

### Beispiele

```bash
# Standard-Import mit Event
pg-import /Volumes/EOS_DIGITAL --event "Hochzeit"

# Mit Location und Author
pg-import /Volumes/SD -e "Urlaub" -l "Mallorca" -a "Max"

# In spezifisches Archiv (überschreibt .env und .import.yaml)
pg-import /Volumes/SD --output /Volumes/Archive/2026 --event "Test"

# Trip-Import (keine Abfragen; dateinamen nur aus Datum, wenn kein Event)
pg-import /Volumes/CARD --trip

# Vorschau
pg-import /Volumes/SD --dry-run --verbose
```

### Ablauf

1. venv prüfen (Fehler wenn nicht vorhanden)
2. Konfiguration laden (CLI → ENV → .env → .import.yaml)
3. Dateien scannen (RAW + JPG)
4. Nach EXIF-Datum gruppieren
5. Zielordner erstellen (Standard: `YYYY-MM-DD/`, konfigurierbar)
6. Dateien kopieren und umbenennen
7. EXIF-Tags setzen
8. Checksums generieren
9. Optional: Quelle löschen nach Bestätigung

---

## pg-rename

Benennt Fotos nach konfigurierbarem Pattern um.

### Syntax

```bash
pg-rename <path> [optionen]
```

### Optionen

| Option | Kurz | Beschreibung |
|--------|------|--------------|
| `--pattern <pat>` | `-p` | Naming-Pattern überschreiben |
| `--event <name>` | `-e` | Event-Name für `{event}` Platzhalter |
| `--recursive` | `-r` | Unterverzeichnisse einbeziehen |
| `--dry-run` | `-n` | Vorschau ohne Änderungen |
| `--verbose` | `-v` | Detaillierte Ausgabe |

### Pattern-Platzhalter

| Platzhalter | Beschreibung | Beispiel |
|-------------|--------------|----------|
| `{date}` | Datum aus EXIF | `20260124` |
| `{time}` | Zeit aus EXIF | `143022` |
| `{event}` | Event-Name | `Hochzeit` |
| `{seq}` | Sequenznummer | `1` |
| `{seq:03d}` | Mit Padding | `001` |
| `{camera}` | Kameramodell | `EOS5D` |

### Beispiele

```bash
# Mit Event
pg-rename ./photos --event "Urlaub"

# Custom Pattern
pg-rename ./photos --pattern "{date}_{time}_{seq:03d}" --dry-run

# Rekursiv
pg-rename ./archive --event "2026" --recursive
```

---

## pg-exif

Verwaltet EXIF/IPTC/XMP Metadaten.

### Syntax

```bash
pg-exif <files...> [optionen]
```

### Optionen

| Option | Kurz | Beschreibung |
|--------|------|--------------|
| `--author <name>` | `-a` | Artist/Creator setzen |
| `--copyright <text>` | `-c` | Copyright setzen |
| `--event <name>` | `-e` | Event-Name setzen |
| `--location <loc>` | `-l` | Location setzen |
| `--gps <lat,lon>` | | GPS-Koordinaten setzen |
| `--title <text>` | `-t` | Titel setzen |
| `--description <text>` | `-d` | Beschreibung setzen |
| `--keywords <k1,k2>` | `-k` | Keywords setzen |
| `--show` | `-s` | Metadaten anzeigen |
| `--remove` | | Metadaten entfernen |

### Gesetzte EXIF-Felder

| Option | EXIF/IPTC/XMP Felder |
|--------|---------------------|
| `--author` | Artist, XMP:Creator, IPTC:By-line |
| `--copyright` | Copyright, XMP:Rights, IPTC:CopyrightNotice |
| `--event` | XMP:Event, IPTC:Caption-Abstract |
| `--location` | XMP:Location, IPTC:City |
| `--gps` | GPSLatitude, GPSLongitude + Refs |

### Beispiele

```bash
# Metadaten anzeigen
pg-exif photo.jpg --show

# Author und Copyright setzen
pg-exif ./photos --author "Max" --copyright "© 2026 Max"

# GPS hinzufügen
pg-exif photo.jpg --gps "52.52,13.405"

# Alle Metadaten entfernen
pg-exif photo.jpg --remove
```

---

## pg-album

Verwaltet Foto-Alben mit Symlinks.

### Syntax

```bash
pg-album <command> [argumente]
```

### Commands

| Command | Beschreibung |
|---------|--------------|
| `create <name>` | Neues Album erstellen |
| `delete <name>` | Album löschen |
| `add <album> <files...>` | Fotos hinzufügen |
| `remove <album> <files...>` | Fotos entfernen |
| `list` | Alle Alben auflisten |
| `show <name>` | Album-Inhalt anzeigen |
| `info <name>` | Album-Metadaten anzeigen |
| `export <name> --to <dir>` | Album exportieren (echte Kopien) |

### Beispiele

```bash
# Album erstellen
pg-album create "Alps_Tour_Highlights"

# Fotos hinzufügen
pg-album add "Alps_Tour_Highlights" ~/Photos/2026-01-24/*.jpg

# Album anzeigen
pg-album show "Alps_Tour_Highlights"

# Album exportieren
pg-album export "Alps_Tour_Highlights" --to ~/Desktop/ForRiders/

# Album löschen
pg-album delete "Alps_Tour_Highlights"
```

### Hinweise

- Alben verwenden Symlinks (kein zusätzlicher Speicher)
- Originale bleiben im Archiv
- Ein Foto kann in mehreren Alben sein
- `export` erstellt echte Kopien

---

## pg-develop

Entwickelt RAW-Dateien zu JPG.

### Syntax

```bash
pg-develop <files...> [optionen]
```

### Optionen

| Option | Kurz | Beschreibung |
|--------|------|--------------|
| `--output <dir>` | `-o` | Ausgabeverzeichnis |
| `--preset <name>` | `-p` | Darktable-Preset |
| `--quality <1-100>` | `-q` | JPEG-Qualität |
| `--processor <name>` | | `darktable` oder `imagemagick` |
| `--resize <WxH>` | | Größe ändern (z.B. `1920x`, `x1080`) |
| `--overwrite` | | Existierende überschreiben |
| `--dry-run` | `-n` | Vorschau |

### Beispiele

```bash
# Standard-Entwicklung
pg-develop photo.cr3

# Mit Output und Qualität
pg-develop ./raws/*.cr3 --output ./jpgs --quality 95

# Mit Resize für Web
pg-develop ./raws/*.cr3 --output ./web --resize 1920x --quality 85

# Mit Darktable-Preset
pg-develop photo.cr3 --preset "vivid"

# ImageMagick erzwingen
pg-develop photo.cr3 --processor imagemagick
```

### XMP-Sidecars

Wenn eine `.xmp`-Datei neben dem RAW existiert, nutzt darktable-cli diese automatisch:

```
photo.cr3       # RAW
photo.cr3.xmp   # Darktable-Bearbeitungen → wird verwendet
```

---

## pg-verify

Prüft Datei-Integrität mit Checksums.

### Syntax

```bash
pg-verify <path> <mode> [optionen]
```

### Modes

| Mode | Kurz | Beschreibung |
|------|------|--------------|
| `--generate` | `-g` | Checksums für alle Dateien erstellen |
| `--check` | `-c` | Dateien gegen Checksums prüfen |
| `--update` | `-u` | Neue Dateien hinzufügen, bestehende behalten |

### Optionen

| Option | Beschreibung |
|--------|--------------|
| `--no-recursive` | Nur angegebenes Verzeichnis |
| `--verbose` | Detaillierte Ausgabe |

### Beispiele

```bash
# Checksums generieren
pg-verify ~/Pictures/PhotoLibrary --generate

# Integrität prüfen
pg-verify ~/Pictures/PhotoLibrary --check

# Neue Dateien hinzufügen
pg-verify ~/Pictures/PhotoLibrary --update

# Backup verifizieren
pg-verify /Volumes/Backup/Photos --check
```

### Checksum-Datei

Checksums werden in `.checksums` pro Verzeichnis gespeichert:

```
# .checksums
a1b2c3d4...  20260124_Hochzeit_001.cr3
e5f6g7h8...  20260124_Hochzeit_002.cr3
```

---

## pg-test-processors

Vergleicht RAW-Prozessoren (darktable vs ImageMagick).

### Syntax

```bash
pg-test-processors <raw-file>
```

### Beispiel

```bash
pg-test-processors photo.cr3
```

### Output

Erstellt zwei Dateien zum Vergleich:
- `photo_darktable.jpg`
- `photo_imagemagick.jpg`

Zeigt Verarbeitungszeit und Dateigröße für beide.

---

## setup.sh

Richtet die Entwicklungsumgebung ein.

### Syntax

```bash
./setup.sh
```

### Was es macht

1. Prüft Python 3 und venv-Modul
2. Erstellt `.venv/` virtual environment
3. Installiert Python-Abhängigkeiten aus `requirements.txt`
4. Prüft externe Tools (exiftool, darktable, imagemagick)
5. Erstellt `.env` aus `.env.example` (falls nicht vorhanden)
6. Macht Scripts ausführbar

### Wann ausführen

- Nach dem Klonen des Repositories
- Nach Änderungen an `requirements.txt`
- Wenn `.venv/` gelöscht wurde

---

## Tests ausführen

Das Projekt enthält eine umfassende Test-Suite mit pytest.

### Syntax

```bash
make test              # Alle Tests ausführen
make test-fast         # Langsame Tests überspringen
make test-coverage     # Coverage-Report erstellen

# Oder direkt mit pytest
source .venv/bin/activate
pytest tests/ -v                           # Alle Tests
pytest tests/unit/ -v                      # Nur Unit-Tests
pytest tests/integration/test_pg_import.py # Bestimmte Datei
```

### Test-Struktur

```
tests/
├── conftest.py          # Gemeinsame Fixtures
├── fixtures/            # Test-Helfer
├── unit/                # Tests für lib/ Module
├── integration/         # Tests für einzelne Scripts
├── e2e/                 # End-to-End Workflow-Tests
└── matrix/              # Kombinatorische Options-Tests
```

### Tests schreiben

Neue Features benötigen Tests. Siehe `tests/conftest.py` für verfügbare Fixtures:

- `test_env` - Isolierte Umgebung mit temp. Verzeichnissen
- `run_script` - `bin/pg-*` Scripts ausführen
- `sample_jpeg` - Test-Bilder erstellen
- `temp_sd_card` - Mock SD-Karten-Struktur

---

Zurück zum [Workflow](workflow.de.md) | [Konfiguration](configuration.de.md)
