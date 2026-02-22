<p align="center">
  <img src="doc/images/logo.png" alt="PixelGroomer" width="200">
</p>

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
pg-import /Volumes/EOS_DIGITAL --event "Endurotraining" --location "Stadtoldendorf"
```

Fotos werden nach `~/Pictures/PhotoLibrary/2026-01-24/` sortiert und umbenannt.

### 2. Album erstellen

```bash
pg-album create "Alps_Tour_Highlights"
pg-album add "Alps_Tour_Highlights" ~/Pictures/PhotoLibrary/2026-01-24/*.jpg
```

### 3. RAW entwickeln

```bash
pg-develop ~/Pictures/PhotoLibrary/2026-01-24/*.cr3 --output ~/Desktop/jpgs/
```

### 4. Album exportieren

```bash
pg-album export "Alps_Tour_Highlights" --to ~/Desktop/ForRiders/
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

## Konfiguration

```bash
# .env - Globale Einstellungen
PHOTO_LIBRARY="$HOME/Pictures/PhotoLibrary"
DEFAULT_AUTHOR="Max Mustermann"
FOLDER_STRUCTURE="{year}-{month}-{day}"
```

```yaml
# .import.yaml auf SD-Karte - Per-Import Einstellungen
event: "Endurotraining Tag 1"
location: "Stadtoldendorf"
```

**Priorität:** CLI-Argumente → Umgebungsvariablen → .env → .import.yaml

## Dokumentation

- [Workflow](doc/workflow.de.md) - Vollständiger Arbeitsablauf
- [Konfiguration](doc/configuration.de.md) - Alle Einstellungen erklärt
- [Script-Referenz](doc/scripts.de.md) - Detaillierte Optionen aller Scripts
- [Beispiele](doc/examples.de.md) - Vollständige Workflow-Beispiele

Englische Dokumentation:
- [Workflow (EN)](doc/workflow.en.md)
- [Configuration (EN)](doc/configuration.en.md)
- [Script Reference (EN)](doc/scripts.en.md)
- [Examples (EN)](doc/examples.en.md)

## Tests

Führe die Tests vor dem Einreichen von Änderungen aus:

```bash
make test          # Alle Tests ausführen
make test-fast     # Langsame Tests überspringen
make test-coverage # Coverage-Report erstellen
```

Tests befinden sich in `tests/` und verwenden pytest. Alle neuen Features benötigen Tests.

## Beitragen mit KI

Dieses Projekt verwendet Cursor-Regeln (`.cursor/rules/*.mdc`) zur Steuerung von KI-Assistenten:

| Regel | Zweck |
|-------|-------|
| `languages.mdc` | Nur Bash und Python; Python muss im venv laufen |
| `bash-compatibility.mdc` | Bash 3.2 Kompatibilität erzwingen (macOS Standard) |
| `bilingual-docs.mdc` | Dokumentation in Deutsch und Englisch pflegen |
| `shellcheck.mdc` | ShellCheck-Validierung für alle Scripts verlangen |
| `testing-requirements.mdc` | Alle Features benötigen Tests die bestehen |
| `git-commits.mdc` | Kleine Commits mit Action-Prefix in der Nachricht |

Bei Beiträgen mit einem KI-Assistenten sorgen diese Regeln für einheitlichen Code-Stil und Projektkonventionen.

## Lizenz

[Unlicense](https://unlicense.org) - Public Domain. Siehe [LICENSE](LICENSE).
