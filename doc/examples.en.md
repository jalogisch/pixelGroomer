# Example Workflows

*[Deutsche Version](examples.de.md)*

This document shows how to combine PixelGroomer tools into complete workflows.

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
