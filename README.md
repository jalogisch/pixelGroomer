# PixelGroomer

*[Deutsche Version](README.de.md)*

Modular CLI toolset for automating photo workflows.

> **Note:** This project serves as an experiment for AI-assisted development using [Cursor](https://cursor.com) as IDE. The codebase is a mix of hand-written and AI-generated code, developed in parallel. Project rules are defined in `.cursor/rules/*.mdc` to ensure consistent AI behaviour. Contributors are welcome to use these rules or add new ones.

**Features:**
- Import from SD cards with automatic sorting and renaming
- EXIF/IPTC/XMP metadata management
- Album management with symlinks (saves disk space)
- RAW development to JPG (darktable-cli or ImageMagick)
- Integrity verification with checksums

## Installation

```bash
# 1. External dependencies (macOS)
brew install exiftool python3 darktable imagemagick

# 2. Run setup (creates venv, installs Python deps)
./setup.sh

# 3. Optional: Add to PATH
echo 'export PATH="$PATH:'$(pwd)'/bin"' >> ~/.zshrc
```

The setup script:
- Creates a Python virtual environment (`.venv/`)
- Installs Python dependencies
- Checks external tools (exiftool, darktable, etc.)
- Creates `.env` from template

## Quickstart

### 1. Import photos

```bash
pg-import /Volumes/EOS_DIGITAL --event "Wedding" --location "Berlin"
```

Photos are sorted into `~/Pictures/PhotoLibrary/2026-01-24/` and renamed.

### 2. Create album

```bash
pg-album create "Wedding_Highlights"
pg-album add "Wedding_Highlights" ~/Pictures/PhotoLibrary/2026-01-24/*.jpg
```

### 3. Develop RAW files

```bash
pg-develop ~/Pictures/PhotoLibrary/2026-01-24/*.cr3 --output ~/Desktop/jpgs/
```

### 4. Export album

```bash
pg-album export "Wedding_Highlights" --to ~/Desktop/ForFamily/
```

## Scripts

| Script | Description |
|--------|-------------|
| `pg-import` | Import from SD card with sorting and EXIF tagging |
| `pg-rename` | Rename according to configurable pattern |
| `pg-exif` | Set/show EXIF metadata |
| `pg-album` | Album management with symlinks |
| `pg-develop` | RAW to JPG development |
| `pg-verify` | Checksum-based integrity verification |
| `pg-web` | Start web interface (opens browser) |

## Configuration

```bash
# .env - Global settings
PHOTO_LIBRARY="$HOME/Pictures/PhotoLibrary"
DEFAULT_AUTHOR="Max Mustermann"
FOLDER_STRUCTURE="{year}-{month}-{day}"
```

```yaml
# .import.yaml on SD card - Per-import settings
event: "Wedding Meyer"
location: "Berlin"
```

**Priority:** SD card → .env → CLI arguments

## Documentation

- [Workflow](doc/workflow.en.md) - Complete workflow guide
- [Configuration](doc/configuration.en.md) - All settings explained
- [Script Reference](doc/scripts.en.md) - Detailed options for all scripts
- [Examples](doc/examples.en.md) - Complete workflow examples
- [Web Planner](doc/web-planner.en.md) - Web interface architecture

German documentation:
- [Workflow (DE)](doc/workflow.de.md)
- [Konfiguration (DE)](doc/configuration.de.md)
- [Script-Referenz (DE)](doc/scripts.de.md)
- [Beispiele (DE)](doc/examples.de.md)
- [Web Planner (DE)](doc/web-planner.de.md)

## Contributing with AI

This project uses Cursor rules (`.cursor/rules/*.mdc`) to guide AI assistants:

| Rule | Purpose |
|------|---------|
| `languages.mdc` | Only Bash and Python; Python must run in venv |
| `python-style.mdc` | Python code style for web application |
| `bash-compatibility.mdc` | Enforce Bash 3.2 compatibility (macOS default) |
| `bilingual-docs.mdc` | Maintain documentation in German and English |
| `shellcheck.mdc` | Require ShellCheck validation for all scripts |

When contributing with an AI assistant, these rules ensure consistent code style and project conventions.

## License

[Unlicense](https://unlicense.org) - Public Domain. See [LICENSE](LICENSE).
