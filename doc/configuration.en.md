# Configuration

*[Deutsche Version](configuration.de.md)*

PixelGroomer is configured through multiple layers. This guide explains all options.

## Setup

Before first use, you need to run the setup:

```bash
./setup.sh
```

The setup creates:
- **`.venv/`** - Python virtual environment with all dependencies
- **`.env`** - Configuration file (from `.env.example`)

All scripts automatically check the venv and show an error if missing:

```
[ERROR] Python virtual environment not found!

Please run the setup script first:

    /path/to/pixelGroomer/setup.sh
```

### Makefile commands

```bash
make setup         # Run setup
make check         # Check dependencies
make deps          # Install external tools (macOS)
make clean         # Remove venv
make test          # Run all tests
make test-fast     # Skip slow tests
make test-coverage # Generate coverage report
make lint          # Run ShellCheck on all scripts
```

## Configuration Priority

Settings are loaded in this order (later overrides earlier):

```
1. SD card (.import.yaml)     ← lowest priority
2. Project (.env)              
3. CLI arguments               ← highest priority
4. Interactive prompt          ← only if value missing
```

**Example:**
```bash
# .import.yaml on SD card has: event="Test"
# .env has: DEFAULT_AUTHOR="Max"
# CLI: pg-import /sd --event "Endurotraining"

# Result:
# - Event: "Endurotraining" (CLI wins)
# - Author: "Max" (.env, no CLI override)
```

## Global Configuration (.env)

Create the file in the project directory:

```bash
cp .env.example .env
```

### Paths

```bash
# Main archive for all photos
PHOTO_LIBRARY="$HOME/Pictures/PhotoLibrary"

# Directory for symlink albums
ALBUM_DIR="$HOME/Pictures/Albums"

# Default export directory
EXPORT_DIR="$HOME/Pictures/Export"
```

### Folder Structure

```bash
# Pattern for folder organization
# Available placeholders: {year}, {month}, {day}
FOLDER_STRUCTURE="{year}-{month}-{day}"

# Examples:
# {year}-{month}-{day}        → 2026-01-24/
# {year}/{month}/{day}        → 2026/01/24/
# {year}-{month}/{day}        → 2026-01/24/
# {year}/{year}-{month}-{day} → 2026/2026-01-24/
```

### Metadata Defaults

```bash
# Default author for all imports
DEFAULT_AUTHOR="Max Mustermann"

# Default copyright
DEFAULT_COPYRIGHT="© 2026 Max Mustermann"
```

### Filename Pattern

```bash
# Available placeholders:
#   {date}   - YYYYMMDD from EXIF
#   {time}   - HHMMSS from EXIF
#   {event}  - Event name
#   {seq}    - Sequence number ({seq:03d} for padding)
#   {camera} - Camera model from EXIF
NAMING_PATTERN="{date}_{event}_{seq:03d}"

# Examples:
# {date}_{event}_{seq:03d}     → 20260124_Endurotraining_001.jpg
# {date}_{time}_{seq:03d}      → 20260124_143022_001.jpg
# {event}_{date}_{seq:03d}     → Endurotraining_20260124_001.jpg
```

### RAW Development

```bash
# Preferred processor: darktable, imagemagick, or rawtherapee
RAW_PROCESSOR="darktable"

# JPEG quality (1-100)
JPEG_QUALITY=92

# Default darktable preset (empty = none)
DARKTABLE_STYLE=""

# Default RawTherapee PP3 preset path (empty = none)
RAWTHERAPEE_PRESET=""
```

Resize (`--resize`) is only applied when using the ImageMagick processor; darktable and RawTherapee output is not resized so the developed look is preserved.

### Supported Formats

```bash
# RAW formats (case-insensitive)
RAW_EXTENSIONS="cr2,cr3,nef,arw,raf,dng,orf,rw2"

# Image formats
IMAGE_EXTENSIONS="jpg,jpeg,png,tiff,tif,heic,heif"
```

### Import Behavior

```bash
# Ask before deleting source
CONFIRM_DELETE="true"

# Generate checksums during import
GENERATE_CHECKSUMS="true"

# Checksum algorithm (sha256 or md5)
CHECKSUM_ALGORITHM="sha256"

# Prompt for archive directory on each import
# If true, asks for target directory before each import
# CLI --output overrides this prompt
PROMPT_ARCHIVE_DIR="false"
```

### Python Virtual Environment

The venv is automatically created by setup. If you want to manage it manually:

```bash
# Create venv
python3 -m venv .venv

# Activate
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

The scripts use the venv automatically without activation - they call `.venv/bin/python` directly.

## Per-Import Configuration (.import.yaml)

Place this file on the SD card:
- `/DCIM/.import.yaml` (recommended)
- `/.import.yaml` (card root)

### Basic Options

```yaml
# Event name (used for filename and EXIF)
event: "Endurotraining Tag 1"

# Location for EXIF metadata
location: "Stadtoldendorf, Germany"

# Override author (optional)
# Will be overridden by .env DEFAULT_AUTHOR!
author: "Max Mustermann"

# Copyright notice (optional; falls back to .env DEFAULT_COPYRIGHT)
copyright: "© 2026 Your Name. Released under the Unlicense (https://unlicense.org)"

# Credit line / artist name (optional; IPTC:Credit)
credit: "Your Name"

# Target archive for this import (optional)
# Will be overridden by .env PHOTO_LIBRARY!
archive: "/Volumes/PhotoArchive/2026"
```

A minimal template with only author, copyright, and credit is in `templates/.import.yaml.identity`; copy it to each card as `DCIM/.import.yaml` and edit as needed.

**Important:** Values in `.import.yaml` have the lowest priority. They are overridden by `.env` and CLI arguments. The file is good for event-specific defaults that can be overridden when needed.

### Advanced Options

```yaml
# Keywords for EXIF
tags:
  - wedding
  - family
  - outdoor

# Notes about this import (optional)
# Not written to files, just for reference
notes: "Day 1 of the wedding, ceremony and reception"

# Override naming pattern
pattern: "{date}_{time}_{event}_{seq:03d}"

# GPS coordinates to apply to all photos
# Useful if your camera doesn't have GPS
gps: "52.5200,13.4050"
```

### Multiple Events per SD Card

If you have multiple events on one card, you can use different `.import.yaml` in DCIM subfolders:

```
SD-Card/
├── DCIM/
│   ├── 100CANON/
│   │   ├── .import.yaml  ← event: "Event 1"
│   │   └── IMG_001.CR3
│   └── 101CANON/
│       ├── .import.yaml  ← event: "Event 2"
│       └── IMG_100.CR3
```

## CLI Arguments

CLI arguments always have the highest priority:

```bash
pg-import /source [options]

Options:
  -e, --event <name>    Event name
  -l, --location <loc>  Location
  -a, --author <name>   Author
  -o, --output <dir>    Target archive
  -n, --dry-run         Preview without changes
  --no-delete           Don't delete source
  -v, --verbose         Detailed output
```

**Examples:**

```bash
# Override event and location
pg-import /Volumes/SD --event "Alps Tour" --location "Sölk Pass"

# Import to specific archive
pg-import /Volumes/SD --output /Volumes/Backup/Photos

# Preview without changes
pg-import /Volumes/SD --dry-run --verbose
```

## Environment Variables

All `.env` variables can also be set as environment variables:

```bash
# Temporarily for one command
PHOTO_LIBRARY=/tmp/test pg-import /source --event "Test"

# In the shell session
export PHOTO_LIBRARY="/Volumes/Archive"
pg-import /source --event "Test"
```

## Example Configurations

### Minimal .env

```bash
PHOTO_LIBRARY="$HOME/Pictures/Archive"
DEFAULT_AUTHOR="Max Mustermann"
```

### Complete .env

```bash
# Paths
PHOTO_LIBRARY="$HOME/Pictures/PhotoLibrary"
ALBUM_DIR="$HOME/Pictures/Albums"
EXPORT_DIR="$HOME/Pictures/Export"

# Structure
FOLDER_STRUCTURE="{year}-{month}-{day}"
NAMING_PATTERN="{date}_{event}_{seq:03d}"

# Metadata
DEFAULT_AUTHOR="Max Mustermann"
DEFAULT_COPYRIGHT="© 2026 Max Mustermann"

# RAW development
RAW_PROCESSOR="darktable"
JPEG_QUALITY=92
DARKTABLE_STYLE="vivid"

# RAW formats
RAW_EXTENSIONS="cr2,cr3,nef,arw,raf,dng,orf,rw2"
IMAGE_EXTENSIONS="jpg,jpeg,png,tiff,tif,heic,heif"

# Behavior
CONFIRM_DELETE="true"
GENERATE_CHECKSUMS="true"
CHECKSUM_ALGORITHM="sha256"
PROMPT_ARCHIVE_DIR="false"
```

### Typical .import.yaml

```yaml
event: "Endurotraining Tag 1"
location: "Stadtoldendorf"
tags:
  - wedding
  - family
```

---

Back to [Workflow](workflow.en.md) | Continue to [Script Reference](scripts.en.md)
