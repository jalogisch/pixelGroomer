# Script Reference

*[Deutsche Version](scripts.de.md)*

Detailed documentation for all PixelGroomer scripts.

## Prerequisites

All scripts require a configured Python virtual environment. If missing:

```bash
./setup.sh
```

The scripts automatically check the venv and show an error with instructions if missing.

## pg-import

Imports photos from SD cards or directories with automatic organization.

### Syntax

```bash
pg-import <source> [options]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `<source>` | Source directory (e.g. `/Volumes/EOS_DIGITAL`) |

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--event <name>` | `-e` | Event name for metadata and filename |
| `--location <loc>` | `-l` | Location for EXIF metadata |
| `--author <name>` | `-a` | Override author |
| `--output <dir>` | `-o` | Target archive (overrides PHOTO_LIBRARY and .import.yaml) |
| `--dry-run` | `-n` | Preview without changes |
| `--no-delete` | | Don't delete source (don't even ask) |
| `--trip` | `-t` | Trip mode: skip event/location prompts; date-only filenames when event not set |
| `--verbose` | `-v` | Detailed output |
| `--help` | `-h` | Show help |

### Configuration Priority

Settings are loaded in this order (later overrides earlier):

1. `.import.yaml` on SD card (lowest priority)
2. `.env` configuration file
3. CLI arguments (highest priority)
4. Interactive prompt (only if value missing)

### Examples

```bash
# Standard import with event
pg-import /Volumes/EOS_DIGITAL --event "Endurotraining"

# With location and author
pg-import /Volumes/SD -e "Vacation" -l "Mallorca" -a "Max"

# To specific archive (overrides .env and .import.yaml)
pg-import /Volumes/SD --output /Volumes/Archive/2026 --event "Test"

# Trip import (no prompts; date-only names when no event)
pg-import /Volumes/CARD --trip

# Preview
pg-import /Volumes/SD --dry-run --verbose
```

### Process

1. Check venv (error if missing)
2. Load configuration (CLI → ENV → .env → .import.yaml)
3. Scan files (RAW + JPG)
4. Group by EXIF date
5. Create target folders (default: `YYYY-MM-DD/`, configurable)
6. Copy and rename files
7. Set EXIF tags
8. Generate checksums
9. Optional: Delete source after confirmation

---

## pg-rename

Renames photos according to configurable pattern.

### Syntax

```bash
pg-rename <path> [options]
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--pattern <pat>` | `-p` | Override naming pattern |
| `--event <name>` | `-e` | Event name for `{event}` placeholder |
| `--recursive` | `-r` | Include subdirectories |
| `--dry-run` | `-n` | Preview without changes |
| `--verbose` | `-v` | Detailed output |

### Pattern Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{date}` | Date from EXIF | `20260124` |
| `{time}` | Time from EXIF | `143022` |
| `{event}` | Event name | `Endurotraining` |
| `{seq}` | Sequence number | `1` |
| `{seq:03d}` | With padding | `001` |
| `{camera}` | Camera model | `EOS5D` |

### Examples

```bash
# With event
pg-rename ./photos --event "Vacation"

# Custom pattern
pg-rename ./photos --pattern "{date}_{time}_{seq:03d}" --dry-run

# Recursive
pg-rename ./archive --event "2026" --recursive
```

---

## pg-exif

Manages EXIF/IPTC/XMP metadata.

### Syntax

```bash
pg-exif <files...> [options]
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--author <name>` | `-a` | Set Artist/Creator |
| `--copyright <text>` | `-c` | Set Copyright |
| `--event <name>` | `-e` | Set Event name |
| `--location <loc>` | `-l` | Set Location |
| `--gps <lat,lon>` | | Set GPS coordinates |
| `--title <text>` | `-t` | Set Title |
| `--description <text>` | `-d` | Set Description |
| `--keywords <k1,k2>` | `-k` | Set Keywords |
| `--show` | `-s` | Show metadata (no changes) |
| `--remove` | | Remove metadata |

### EXIF Fields Set

| Option | EXIF/IPTC/XMP Fields |
|--------|---------------------|
| `--author` | Artist, XMP:Creator, IPTC:By-line |
| `--copyright` | Copyright, XMP:Rights, IPTC:CopyrightNotice |
| `--event` | XMP:Event, IPTC:Caption-Abstract |
| `--location` | XMP:Location, IPTC:City |
| `--gps` | GPSLatitude, GPSLongitude + Refs |

### Examples

```bash
# Show metadata
pg-exif photo.jpg --show

# Set author and copyright
pg-exif ./photos --author "Max" --copyright "© 2026 Max"

# Add GPS
pg-exif photo.jpg --gps "52.52,13.405"

# Remove all metadata
pg-exif photo.jpg --remove
```

---

## pg-album

Manages photo albums with symlinks.

### Syntax

```bash
pg-album <command> [arguments]
```

### Commands

| Command | Description |
|---------|-------------|
| `create <name>` | Create new album |
| `delete <name>` | Delete album |
| `add <album> <files...>` | Add photos |
| `remove <album> <files...>` | Remove photos |
| `list` | List all albums |
| `show <name>` | Show album content |
| `info <name>` | Show album metadata |
| `export <name> --to <dir>` | Export album (real copies) |

### Examples

```bash
# Create album
pg-album create "Alps_Tour_Highlights"

# Add photos
pg-album add "Alps_Tour_Highlights" ~/Photos/2026-01-24/*.jpg

# Show album
pg-album show "Alps_Tour_Highlights"

# Export album
pg-album export "Alps_Tour_Highlights" --to ~/Desktop/ForRiders/

# Delete album
pg-album delete "Alps_Tour_Highlights"
```

### Notes

- Albums use symlinks (no additional storage)
- Originals stay in archive
- One photo can be in multiple albums
- `export` creates real copies

---

## pg-develop

Develops RAW files to JPG.

### Syntax

```bash
pg-develop <files...> [options]
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--output <dir>` | `-o` | Output directory |
| `--preset <name>` | `-p` | Darktable preset |
| `--quality <1-100>` | `-q` | JPEG quality |
| `--processor <name>` | | `darktable` or `imagemagick` |
| `--resize <WxH>` | | Resize (e.g. `1920x`, `x1080`) |
| `--overwrite` | | Overwrite existing |
| `--dry-run` | `-n` | Preview |

### Examples

```bash
# Standard development
pg-develop photo.cr3

# With output and quality
pg-develop ./raws/*.cr3 --output ./jpgs --quality 95

# With resize for web
pg-develop ./raws/*.cr3 --output ./web --resize 1920x --quality 85

# With darktable preset
pg-develop photo.cr3 --preset "vivid"

# Force ImageMagick
pg-develop photo.cr3 --processor imagemagick
```

### XMP Sidecars

If a `.xmp` file exists next to the RAW, darktable-cli uses it automatically:

```
photo.cr3       # RAW
photo.cr3.xmp   # Darktable edits → will be used
```

---

## pg-verify

Verifies file integrity with checksums.

### Syntax

```bash
pg-verify <path> <mode> [options]
```

### Modes

| Mode | Short | Description |
|------|-------|-------------|
| `--generate` | `-g` | Generate checksums for all files |
| `--check` | `-c` | Verify files against stored checksums |
| `--update` | `-u` | Add new files, keep existing checksums |

### Options

| Option | Description |
|--------|-------------|
| `--no-recursive` | Only specified directory |
| `--verbose` | Detailed output |

### Examples

```bash
# Generate checksums
pg-verify ~/Pictures/PhotoLibrary --generate

# Check integrity
pg-verify ~/Pictures/PhotoLibrary --check

# Add new files
pg-verify ~/Pictures/PhotoLibrary --update

# Verify backup
pg-verify /Volumes/Backup/Photos --check
```

### Checksum File

Checksums are stored in `.checksums` per directory:

```
# .checksums
a1b2c3d4...  20260124_Endurotraining_001.cr3
e5f6g7h8...  20260124_Endurotraining_002.cr3
```

---

## pg-test-processors

Compares RAW processors (darktable vs ImageMagick).

### Syntax

```bash
pg-test-processors <raw-file>
```

### Example

```bash
pg-test-processors photo.cr3
```

### Output

Creates two files for comparison:
- `photo_darktable.jpg`
- `photo_imagemagick.jpg`

Shows processing time and file size for both.

---

## setup.sh

Sets up the development environment.

### Syntax

```bash
./setup.sh
```

### What it does

1. Checks Python 3 and venv module
2. Creates `.venv/` virtual environment
3. Installs Python dependencies from `requirements.txt`
4. Checks external tools (exiftool, darktable, imagemagick)
5. Creates `.env` from `.env.example` (if missing)
6. Makes scripts executable

### When to run

- After cloning the repository
- After changes to `requirements.txt`
- When `.venv/` was deleted

---

## Running Tests

The project includes a comprehensive test suite using pytest.

### Syntax

```bash
make test              # Run all tests
make test-fast         # Skip slow tests  
make test-coverage     # Generate coverage report

# Or directly with pytest
source .venv/bin/activate
pytest tests/ -v                           # All tests
pytest tests/unit/ -v                      # Unit tests only
pytest tests/integration/test_pg_import.py # Specific file
```

### Test Structure

```
tests/
├── conftest.py          # Shared fixtures
├── fixtures/            # Test helpers
├── unit/                # Tests for lib/ modules
├── integration/         # Tests for individual scripts
├── e2e/                 # End-to-end workflow tests
└── matrix/              # Combinatorial option tests
```

### Writing Tests

New features require tests. See `tests/conftest.py` for available fixtures:

- `test_env` - Isolated environment with temp directories
- `run_script` - Execute `bin/pg-*` scripts
- `sample_jpeg` - Create test images
- `temp_sd_card` - Mock SD card structure

---

Back to [Workflow](workflow.en.md) | [Configuration](configuration.en.md)
