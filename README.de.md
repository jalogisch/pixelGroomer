# PixelGroomer

*[English Version](README.md)*

Modulares CLI-Toolset zur Automatisierung des Foto-Workflows.

> **Hinweis:** Dieses Projekt dient als Experiment für KI-gestützte Entwicklung mit [Cursor](https://cursor.com) als IDE. Der Code ist eine Mischung aus handgeschriebenem und KI-generiertem Code, der parallel entwickelt wird. Projektregeln sind in `.cursor/rules/*.mdc` definiert, um ein konsistentes KI-Verhalten sicherzustellen. Beitragende können diese Regeln nutzen oder neue hinzufügen.

**Features:**
- Import von SD-Karten mit automatischer Sortierung und Umbenennung
- EXIF/IPTC/XMP Metadaten-Management
- Album-Verwaltung mit Symlinks (spart Speicherplatz)
- RAW-Entwicklung zu JPG (darktable-cli oder ImageMagick)
- Integritätsprüfung mit Checksums

## Installation

```bash
# 1. Externe Abhängigkeiten (macOS)
brew install exiftool python3 darktable imagemagick

# 2. Setup ausführen (erstellt venv, installiert Python-Deps)
./setup.sh

# 3. Optional: Zum PATH hinzufügen
echo 'export PATH="$PATH:'$(pwd)'/bin"' >> ~/.zshrc
```

Das Setup-Script:
- Erstellt ein Python virtual environment (`.venv/`)
- Installiert Python-Abhängigkeiten
- Prüft externe Tools (exiftool, darktable, etc.)
- Erstellt `.env` aus Template

## Quickstart

### 1. Fotos importieren

```bash
pg-import /Volumes/EOS_DIGITAL --event "Hochzeit" --location "Berlin"
```

Fotos werden nach `~/Pictures/PhotoLibrary/2026-01-24/` sortiert und umbenannt.

### 2. Album erstellen

```bash
pg-album create "Hochzeit_Highlights"
pg-album add "Hochzeit_Highlights" ~/Pictures/PhotoLibrary/2026-01-24/*.jpg
```

### 3. RAW entwickeln

```bash
pg-develop ~/Pictures/PhotoLibrary/2026-01-24/*.cr3 --output ~/Desktop/jpgs/
```

### 4. Album exportieren

```bash
pg-album export "Hochzeit_Highlights" --to ~/Desktop/ForFamily/
```

## Scripts

| Script | Beschreibung |
|--------|--------------|
| `pg-import` | Import von SD-Karte mit Sortierung und EXIF-Tagging |
| `pg-rename` | Umbenennung nach konfigurierbarem Pattern |
| `pg-exif` | EXIF-Metadaten setzen/anzeigen |
| `pg-album` | Album-Management mit Symlinks |
| `pg-develop` | RAW zu JPG Entwicklung |
| `pg-verify` | Checksum-basierte Integritätsprüfung |
| `pg-web` | Web-Interface starten (öffnet Browser) |

## Konfiguration

```bash
# .env - Globale Einstellungen
PHOTO_LIBRARY="$HOME/Pictures/PhotoLibrary"
DEFAULT_AUTHOR="Max Mustermann"
FOLDER_STRUCTURE="{year}-{month}-{day}"
```

```yaml
# .import.yaml auf SD-Karte - Per-Import Einstellungen
event: "Hochzeit Meyer"
location: "Berlin"
```

**Priorität:** SD-Karte → .env → CLI-Argumente

## Dokumentation

- [Workflow](doc/workflow.de.md) - Vollständiger Arbeitsablauf
- [Konfiguration](doc/configuration.de.md) - Alle Einstellungen erklärt
- [Script-Referenz](doc/scripts.de.md) - Detaillierte Optionen aller Scripts
- [Beispiele](doc/examples.de.md) - Vollständige Workflow-Beispiele
- [Web Planner](doc/web-planner.de.md) - Web-Interface Architektur

Englische Dokumentation:
- [Workflow (EN)](doc/workflow.en.md)
- [Configuration (EN)](doc/configuration.en.md)
- [Script Reference (EN)](doc/scripts.en.md)
- [Examples (EN)](doc/examples.en.md)
- [Web Planner (EN)](doc/web-planner.en.md)

## Beitragen mit KI

Dieses Projekt verwendet Cursor-Regeln (`.cursor/rules/*.mdc`) zur Steuerung von KI-Assistenten:

| Regel | Zweck |
|-------|-------|
| `languages.mdc` | Nur Bash und Python; Python muss im venv laufen |
| `python-style.mdc` | Python Code-Stil für Web-Anwendung |
| `bash-compatibility.mdc` | Bash 3.2 Kompatibilität erzwingen (macOS Standard) |
| `bilingual-docs.mdc` | Dokumentation in Deutsch und Englisch pflegen |
| `shellcheck.mdc` | ShellCheck-Validierung für alle Scripts verlangen |

Bei Beiträgen mit einem KI-Assistenten sorgen diese Regeln für einheitlichen Code-Stil und Projektkonventionen.

## Lizenz

[Unlicense](https://unlicense.org) - Public Domain. Siehe [LICENSE](LICENSE).
