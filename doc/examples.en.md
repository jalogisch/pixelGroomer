# Example Workflows

*[Deutsche Version](examples.de.md)*

This document shows how to combine PixelGroomer tools into complete workflows.

## Available Example Workflows

| Script | Purpose |
|--------|---------|
| `holiday-import.sh` | Import from SD card in trip mode (identity only, one folder per day) |
| `daily-offload.sh` | Simple daily SD card import for multi-day events |
| `develop-album.sh` | Develop RAW files with unified darktable preset |
| `album-export.sh` | Export album with licensing metadata and watermark |
| `enduro-workflow.sh` | Complete workflow with development and web export |

---

## Holiday Import Workflow

The `examples/holiday-import.sh` script imports all photos from an SD card in trip mode. No event or location — only author, copyright, and credit from the card's `.import.yaml` or .env. One folder per day by EXIF date. Ideal for post-holiday import.

### Usage

```bash
./examples/holiday-import.sh /Volumes/CARD [--no-delete] [--dry-run] [--output DIR]
```

See [Workflow: Holiday import (SD card)](workflow.en.md#holiday-import-sd-card).

---

## Daily Offload Workflow

The `examples/daily-offload.sh` script provides a simple, repeatable import workflow for multi-day events. Perfect for offloading SD cards daily with consistent metadata.

### Use Case

- Multi-day motorcycle event (rally, tour, training)
- Daily SD card offload to archive
- Consistent metadata across all days
- No development or export - just safe archiving

### Configuration

Customize the script header for your event:

```bash
# Event information
EVENT_NAME="GS Treffen 2026"           # Base name for the event
EVENT_LOCATION="Garmisch-Partenkirchen"
EVENT_GPS="47.5000,11.1000"            # GPS coordinates

# Photographer metadata
AUTHOR="Jan Doberstein"
ARTIST="pixelpiste"
COPYRIGHT="Unlicense - Public Domain"
```

### Basic Usage

```bash
# Daily offload - date is automatic
./examples/daily-offload.sh /Volumes/EOS_DIGITAL

# Explicit day number
./examples/daily-offload.sh /Volumes/EOS_DIGITAL --day 2

# Preview without changes
./examples/daily-offload.sh /Volumes/EOS_DIGITAL --dry-run
```

### Workflow Steps

The script performs these steps:

1. **Import** - Copy photos from SD card with organization by date
2. **EXIF Metadata** - Set author, artist, GPS coordinates
3. **Checksums** - Generate integrity verification files

### Output Structure

Running daily creates organized folders:

```
~/Pictures/PhotoLibrary/
├── 2026-07-10/                              # Day 1
│   ├── 20260710_GS_Treffen_2026_001.cr3
│   ├── 20260710_GS_Treffen_2026_002.cr3
│   └── .checksums
├── 2026-07-11/                              # Day 2
│   ├── 20260711_GS_Treffen_2026_001.cr3
│   └── .checksums
└── 2026-07-12/                              # Day 3
    └── ...
```

### Multi-Day Event Tips

1. **Before the event:** Copy `daily-offload.sh` and customize configuration
2. **Each evening:** Insert SD card, run script, format card for next day
3. **After event:** Use `develop-album.sh` for unified styling, then `album-export.sh` for sharing

---

## Album Development Workflow

The `examples/develop-album.sh` script batch-develops RAW files using a consistent darktable preset, ensuring all photos from an event have the same look and feel.

### Use Case

- Develop all RAW photos from a rally with consistent styling
- Apply your signature look to all event photos
- Batch convert RAW to high-quality JPEG

### Configuration

Customize the script header:

```bash
# Default darktable preset/style to apply
DEFAULT_PRESET="Adventure"

# Output quality
JPEG_QUALITY=92

# Output subfolder name
OUTPUT_SUBFOLDER="developed"
```

### Creating Darktable Presets

1. Open a representative photo in darktable
2. Edit with your desired look (exposure, colors, contrast)
3. Go to 'styles' module (left panel in darkroom)
4. Click 'create style' and name it (e.g., "Enduro Action")

### Basic Usage

```bash
# Develop album with default preset
./examples/develop-album.sh "GS_Treffen_Highlights"

# Use specific preset
./examples/develop-album.sh "Alps_Tour" --preset "Vivid Landscape"

# Develop folder with custom output
./examples/develop-album.sh ~/Pictures/PhotoLibrary/2026-07-10 --output ~/Desktop/Developed

# List available presets
./examples/develop-album.sh --list-presets
```

### Output Structure

Developed JPEGs are placed in a subfolder:

```
Albums/GS_Treffen_Highlights/
├── IMG_001.cr3                    # Original RAW (symlink)
├── IMG_002.cr3
├── IMG_003.cr3
└── developed/                     # Created by script
    ├── IMG_001.jpg                # Developed JPEG
    ├── IMG_002.jpg
    └── IMG_003.jpg
```

### Workflow: Development → Export

Combine with `album-export.sh` for complete workflow:

```bash
# 1. Develop with unified style
./examples/develop-album.sh "Rally_Photos" --preset "Enduro Action"

# 2. Export developed photos with licensing
./examples/album-export.sh "Rally_Photos/developed" --output ~/Desktop/Share
```

---

## Album Export Workflow

The `examples/album-export.sh` script exports an album or folder with proper licensing metadata and optional watermark. Perfect for sharing photos with clear usage rights.

### Use Case

- Share photos from an event with participants
- Publish photos with proper licensing (CC BY-NC-SA 4.0)
- Add watermark for attribution
- Set contact information in metadata

### Configuration

Customize the script header:

```bash
# Creator information
CREATOR_NAME="Jan Doberstein"
CREATOR_EMAIL="foto@pixelpiste.de"

# Licensing
LICENSE="CC BY-NC-SA 4.0"
COPYRIGHT_STATUS="protected"
USAGE_TERMS="Privatnutzung frei mit Namensnennung. Kommerzielle Nutzung nur nach Rücksprache."

# Watermark
WATERMARK_TEXT="pixelPiste"
WATERMARK_COLOR="white"
WATERMARK_OPACITY="0.6"

# Export settings
EXPORT_QUALITY=85
```

### Metadata Applied

The script sets these metadata fields:

| Field | Value |
|-------|-------|
| License | CC BY-NC-SA 4.0 |
| Copyright | (c) 2026 Jan Doberstein. Alle Rechte vorbehalten. |
| Copyright Status | protected |
| Usage Terms | Privatnutzung frei mit Namensnennung... |
| Creator | Jan Doberstein |
| Contact Email | foto@pixelpiste.de |

### Basic Usage

```bash
# Export album with watermark
./examples/album-export.sh "GS_Treffen_Highlights" --output ~/Desktop/Share

# Export a folder directly
./examples/album-export.sh ~/Pictures/PhotoLibrary/2026-07-10 --output ~/Desktop/Export

# Higher quality for print, no watermark
./examples/album-export.sh "Alps_Tour" --output ~/Desktop/Print --quality 95 --no-watermark

# Preview without changes
./examples/album-export.sh "Rally_Photos" --output ~/Desktop/Test --dry-run
```

### Workflow Steps

1. **Prepare** - Copy images (develop RAW if needed)
2. **Metadata** - Set licensing and copyright information
3. **Export** - Add watermark and compress to JPEG

### Watermark

The watermark is:
- Small and unobtrusive (about 1% of image width)
- White with subtle shadow for visibility
- Positioned in lower right corner
- Can be disabled with `--no-watermark`

### Typical Use After Event

```bash
# 1. Create album with best photos
pg-album create "GS_Treffen_Best"
pg-album add "GS_Treffen_Best" ~/Pictures/PhotoLibrary/2026-07-10/*.cr3

# 2. Export for sharing
./examples/album-export.sh "GS_Treffen_Best" --output ~/Desktop/ForParticipants
```

---

## Enduro Event Workflow

The `examples/enduro-workflow.sh` script demonstrates a complete photo processing pipeline for motorcycle enduro training events at [enduroxperience.de](https://www.enduroxperience.de/).

### Use Case

- Two-day enduro training event
- Location: Stadtoldendorf (GPS: 51°52'30.8"N 9°38'53.2"E)
- Process photos from SD card
- Add metadata (author, artist, location, GPS)
- Develop RAW files with darktable
- Create web-ready exports with watermark
- Compress to ~2MB for easy download

### Configuration

The script has built-in defaults that can be customized:

```bash
# Event location
EVENT_LOCATION="Stadtoldendorf"
EVENT_GPS="51.875222,9.648111"

# Metadata
AUTHOR="Jan Doberstein"
ARTIST="pixelpiste"
COPYRIGHT="Unlicense - Public Domain"

# Watermark (lower right corner)
WATERMARK="Jan Doberstein - enduroeXperience"

# Export settings
MAX_FILE_SIZE_KB=2048  # ~2MB target
```

### Basic Usage

```bash
# Full workflow from SD card
./examples/enduro-workflow.sh /Volumes/EOS_DIGITAL

# Specify output directory
./examples/enduro-workflow.sh /Volumes/EOS_DIGITAL --output ~/Desktop/Event2026

# Day 2 of a multi-day event
./examples/enduro-workflow.sh /Volumes/EOS_DIGITAL --day 2
```

### Confirmation Before Processing

The script shows a detailed plan before any processing starts:

```
╔══════════════════════════════════════════════════════════════════════╗
║                    ENDURO EVENT WORKFLOW - PLAN                      ║
╚══════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────┐
│  SOURCE ANALYSIS                                                     │
├──────────────────────────────────────────────────────────────────────┤
│  Path: /Volumes/EOS_DIGITAL                                          │
│  Files found:                                                        │
│    RAW files (CR2/CR3/NEF/ARW/etc.): 247                            │
│    JPG files:                        0                               │
│    Total photos:                     247                             │
│  Total size: 8.2 GB                                                  │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  METADATA TO BE APPLIED                                             │
├──────────────────────────────────────────────────────────────────────┤
│  Event:     2026-01-24 Endurotraining                               │
│  Location:  Stadtoldendorf                                          │
│  GPS:       51.875222,9.648111 (if missing on photos)               │
│  Author:    Jan Doberstein                                          │
│  Artist:    pixelpiste                                              │
│  Copyright: Unlicense - Public Domain                               │
└──────────────────────────────────────────────────────────────────────┘

...

╔══════════════════════════════════════════════════════════════════════╗
║  Type YES to start processing, or anything else to abort            ║
╚══════════════════════════════════════════════════════════════════════╝

Confirm: YES
```

Only typing `YES` (exactly, case-sensitive) will start the processing. Any other input aborts.

Use `-y` or `--yes` to skip confirmation for automated workflows:

```bash
./examples/enduro-workflow.sh /Volumes/EOS_DIGITAL --yes
```

### Workflow Steps

The script performs these steps automatically:

1. **Import** - Copy photos from SD card to library with organization
2. **EXIF Metadata** - Set author, artist, GPS coordinates
3. **RAW Development** - Convert RAW files to JPG using darktable
4. **Web Export** - Add watermark and compress for web delivery
5. **Checksums** - Generate integrity verification files

### Options

| Option | Description |
|--------|-------------|
| `-o, --output DIR` | Export directory (default: ~/Desktop/EnduroExport) |
| `-e, --event NAME` | Custom event name |
| `-d, --day NUMBER` | Day number for multi-day events |
| `--darktable-preset P` | Apply specific darktable preset |
| `--skip-import` | Process existing library folder |
| `--skip-develop` | Skip RAW development step |
| `-y, --yes` | Skip confirmation, start immediately |

### Examples

```bash
# Process already imported photos
./examples/enduro-workflow.sh --skip-import ~/Pictures/PhotoLibrary/2026-01-24

# Use a specific darktable preset for development
./examples/enduro-workflow.sh /Volumes/EOS_DIGITAL --darktable-preset "Enduro Action"

# Custom event name
./examples/enduro-workflow.sh /Volumes/EOS_DIGITAL --event "GS Trophy Training 2026"

# Skip confirmation (for automated scripts)
./examples/enduro-workflow.sh /Volumes/EOS_DIGITAL --yes
```

### Output Structure

After running the workflow:

```
~/Pictures/PhotoLibrary/
└── 2026-01-24/
    ├── 20260124_Endurotraining_001.cr3    # Original RAW
    ├── 20260124_Endurotraining_002.cr3
    ├── developed/
    │   ├── 20260124_Endurotraining_001.jpg  # Developed JPG
    │   └── 20260124_Endurotraining_002.jpg
    └── .checksums

~/Desktop/EnduroExport/
├── 20260124_Endurotraining_001.jpg    # Watermarked, compressed
├── 20260124_Endurotraining_002.jpg
└── .checksums
```

### Watermark

The watermark is placed in the lower right corner with:
- Semi-transparent white text with subtle shadow
- Font size scales with image dimensions (1.5% of width)
- 2% margin from edges

### Compression

Images are compressed to the target size (~2MB) by:
1. Reducing JPEG quality (starting at 85, down to 50)
2. If still too large, scaling down the image (90%, 80%, etc.)

This ensures photos are small enough for easy download while maintaining reasonable quality.

## Creating Your Own Workflow

Use the enduro workflow as a template:

1. Copy `examples/enduro-workflow.sh` to a new file
2. Adjust the configuration section for your use case
3. Modify or remove steps as needed
4. Add custom processing steps

The script sources the PixelGroomer libraries, so all utility functions are available:

```bash
source "$PIXELGROOMER_ROOT/lib/config.sh"
source "$PIXELGROOMER_ROOT/lib/utils.sh"

# Now you can use:
log_info "Message"
log_success "Done"
log_error "Failed"
log_progress 1 10 "Processing"
```
