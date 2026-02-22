# PixelGroomer Workflow

*[Deutsche Version](workflow.de.md)*

This document describes the typical photo workflow with PixelGroomer - from import to sharing.

## Prerequisites

Before first use, you need to run the setup:

```bash
# Install external tools (macOS)
brew install exiftool python3 darktable imagemagick

# Run setup (creates venv, .env, etc.)
./setup.sh
```

The setup:
- Creates a Python virtual environment (`.venv/`)
- Installs Python dependencies (PyYAML)
- Checks external tools
- Creates `.env` from template

All scripts automatically check if the venv exists and show an error pointing to `setup.sh` if not.

## Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  SD Card    │────▶│   Import    │────▶│   Archive   │────▶│   Share     │
│  (Camera)   │     │  pg-import  │     │  sorted     │     │  pg-develop │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                   │
                           ▼                   ▼
                    ┌─────────────┐     ┌─────────────┐
                    │   EXIF      │     │   Albums    │
                    │  pg-exif    │     │  pg-album   │
                    └─────────────┘     └─────────────┘
```

## Phase 1: Preparation (optional)

Before the shoot you can prepare a `.import.yaml` on the SD card:

```bash
# Create on SD card: /DCIM/.import.yaml
cat > /Volumes/EOS_DIGITAL/DCIM/.import.yaml << 'EOF'
event: "Endurotraining Tag 1"
location: "Stadtoldendorf"
tags:
  - wedding
  - outdoor
EOF
```

This file is automatically detected during import and used as base configuration.

## Phase 2: Import

### Simple Import

```bash
# With event as CLI argument (overrides .import.yaml)
pg-import /Volumes/EOS_DIGITAL --event "Endurotraining" --location "Stadtoldendorf"

# Uses .import.yaml or prompts interactively
pg-import /Volumes/EOS_DIGITAL

# Import to specific archive
pg-import /Volumes/EOS_DIGITAL --output /Volumes/PhotoArchive/2026
```

### Trip / multi-day import

For a trip or multi-day shoot, run import once with `--trip`: no event or location prompts. Files are placed in one folder per day by EXIF date (e.g. `2026-01-24/`, `2026-01-25/`). Filenames use date and sequence only (e.g. `20260124_001.jpg`) when no event is set. You can still put event and location in `.import.yaml` on the card; they will be used if present.

```bash
pg-import /Volumes/CARD --trip
```

### Identity file for all cards

Copy `templates/.import.yaml.identity` to each SD card as `DCIM/.import.yaml`. It sets author, copyright (e.g. Unlicense), and credit (artist name). Leave event and location unset for trip import.

### What happens during import?

1. **Load configuration** (Priority: SD card → .env → CLI)
2. **Scan files** - Find all RAW and JPG files
3. **Sort by date** - Read EXIF date
4. **Create folders** - e.g. `2026-01-24/`
5. **Copy & rename** - e.g. `20260124_Endurotraining_001.cr3`
6. **Set EXIF tags** - Author, Copyright, Event, Location
7. **Generate checksums** - For integrity verification
8. **Optional: Delete source** - After confirmation

### Result structure

```
PhotoLibrary/
├── 2026-01-24/                         # Folder structure: {year}-{month}-{day}
│   ├── 20260124_Endurotraining_001.cr3
│   ├── 20260124_Endurotraining_002.cr3
│   ├── 20260124_Endurotraining_003.jpg
│   └── .checksums
├── 2026-01-25/
│   └── ...
```

The folder structure is configurable via `FOLDER_STRUCTURE` in `.env` (see [Configuration](configuration.en.md)).

## Phase 3: Selection & Organization

### Create albums

After import, you select your best photos and organize them in albums:

```bash
# Create album
pg-album create "Endurotraining_Highlights"

# Add best photos (symlinks, no storage used)
pg-album add "Endurotraining_Highlights" \
    ~/Pictures/PhotoLibrary/2026-01-24/20260124_Endurotraining_001.cr3 \
    ~/Pictures/PhotoLibrary/2026-01-24/20260124_Endurotraining_015.cr3 \
    ~/Pictures/PhotoLibrary/2026-01-24/20260124_Endurotraining_042.jpg

# Or with wildcards
pg-album add "Endurotraining_Highlights" ~/Pictures/PhotoLibrary/2026-01-24/*.jpg
```

### Album structure

```
Albums/
├── Endurotraining_Highlights/
│   ├── 20260124_Endurotraining_001.cr3 -> ../../PhotoLibrary/2026-01-24/...
│   ├── 20260124_Endurotraining_015.cr3 -> ...
│   └── 20260124_Endurotraining_042.jpg -> ...
└── .albums.json
```

**Advantages of symlink albums:**
- No additional storage space
- Originals stay in archive
- One photo can be in multiple albums
- Easy adding/removing

### Album management

```bash
# List all albums
pg-album list

# Show album content
pg-album show "Endurotraining_Highlights"

# Album info (size, count, etc.)
pg-album info "Endurotraining_Highlights"

# Remove photo from album (original stays)
pg-album remove "Endurotraining_Highlights" photo.jpg
```

## Phase 4: RAW Development

### For social media / sharing

```bash
# Develop all RAWs in a folder
pg-develop ~/Pictures/PhotoLibrary/2026-01-24/*.cr3 \
    --output ~/Pictures/Export/Endurotraining/

# With resize for web
pg-develop ~/Pictures/PhotoLibrary/2026-01-24/*.cr3 \
    --output ~/Pictures/Export/Web/ \
    --resize 1920x \
    --quality 85

# Develop album
pg-album export "Endurotraining_Highlights" --to /tmp/highlights_raw/
pg-develop /tmp/highlights_raw/*.cr3 --output ~/Desktop/ForRiders/
```

### Using darktable presets

If you created presets/styles in darktable:

```bash
# With specific preset
pg-develop photo.cr3 --preset "vivid" --quality 95

# Set preset as default in .env
echo 'DARKTABLE_STYLE="my_preset"' >> .env
```

### XMP sidecars

If you edited RAWs in darktable, the XMP sidecars are automatically used:

```
photo.cr3           # RAW file
photo.cr3.xmp       # Darktable edits
```

```bash
# pg-develop automatically uses XMP settings
pg-develop photo.cr3 --output ./export/
```

## Phase 5: Sharing & Export

### Export album for family/friends

```bash
# Export album as real copies (not symlinks)
pg-album export "Endurotraining_Highlights" --to ~/Desktop/ForRiders/

# Create JPGs from RAWs
pg-develop ~/Desktop/ForRiders/*.cr3 \
    --output ~/Desktop/ForRiders/ \
    --quality 90

# Remove RAWs, keep only JPGs
rm ~/Desktop/ForRiders/*.cr3
```

### For different platforms

```bash
# Instagram (1080px, high quality)
pg-develop ./photos/*.cr3 \
    --output ./instagram/ \
    --resize 1080x \
    --quality 95

# WhatsApp (smaller, faster upload)
pg-develop ./photos/*.cr3 \
    --output ./whatsapp/ \
    --resize 1600x \
    --quality 80

# Print (full resolution)
pg-develop ./photos/*.cr3 \
    --output ./print/ \
    --quality 100
```

## Phase 6: Maintenance & Backup

### Check integrity

```bash
# Generate checksums for new archive
pg-verify ~/Pictures/PhotoLibrary --generate

# Check regularly
pg-verify ~/Pictures/PhotoLibrary --check

# After backup: verify backup
pg-verify /Volumes/Backup/PhotoLibrary --check
```

### Change metadata later

```bash
# Set author for all photos of an event
pg-exif ~/Pictures/PhotoLibrary/2026-01-24/ \
    --author "Max Mustermann" \
    --copyright "© 2026 Max Mustermann"

# Add location later
pg-exif ~/Pictures/PhotoLibrary/2026-01-24/ \
    --location "Stadtoldendorf, Germany" \
    --gps "52.52,13.405"

# Show metadata
pg-exif photo.jpg --show
```

## Typical daily workflow

```bash
# 1. After the shoot: insert SD card
# 2. Start import
pg-import /Volumes/EOS_DIGITAL --event "Street Festival"

# 3. Review and edit in darktable/Lightroom
open -a Darktable ~/Pictures/PhotoLibrary/2026-01-24/

# 4. Mark best photos and create album
pg-album create "Festival_Best"
pg-album add "Festival_Best" ~/Pictures/PhotoLibrary/2026-01-24/20260124_Festival_{001,015,023,042}.cr3

# 5. Develop for social media
pg-develop ~/Pictures/PhotoLibrary/2026-01-24/*.cr3 \
    --output ~/Pictures/Export/Festival/ \
    --resize 1920x

# 6. Done! Photos are:
#    - Organized in archive: ~/Pictures/PhotoLibrary/2026-01-24/
#    - Linked in album: ~/Pictures/Albums/Festival_Best/
#    - Ready to share: ~/Pictures/Export/Festival/
```

## Tips

### Optimize SD card workflow

1. **Before each shoot:** Create `.import.yaml` on SD card
2. **Multiple events per card?** Different `.import.yaml` per DCIM subfolder
3. **Backup card?** Same `.import.yaml` on both cards

### Save disk space

- **Use albums:** Symlinks instead of copies
- **Keep originals:** RAWs only once in archive
- **Delete exports:** Can be deleted after sharing

### Data safety

```bash
# After each import: generate checksums
pg-verify ~/Pictures/PhotoLibrary --update

# Before backup: check integrity
pg-verify ~/Pictures/PhotoLibrary --check

# After backup: verify backup
pg-verify /Volumes/Backup/PhotoLibrary --check
```

### After system updates

If Python was updated, the venv might become invalid:

```bash
# Recreate venv
./setup.sh

# Or manually
rm -rf .venv && ./setup.sh
```

---

Continue to [Configuration](configuration.en.md) | [Script Reference](scripts.en.md)
