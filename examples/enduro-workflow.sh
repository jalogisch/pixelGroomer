#!/usr/bin/env bash
# PixelGroomer - Example Workflow Script
# Complete workflow for Enduro training events at enduroxperience.de
#
# This script demonstrates how to combine all pg-* tools into a single
# automated workflow for event photography.

set -euo pipefail

# Get script directory and load libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIXELGROOMER_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=../lib/config.sh disable=SC1091
source "$PIXELGROOMER_ROOT/lib/config.sh"
# shellcheck source=../lib/utils.sh disable=SC1091
source "$PIXELGROOMER_ROOT/lib/utils.sh"

# =============================================================================
# Configuration - Adjust these for your event
# =============================================================================

# Event location
EVENT_LOCATION="Stadtoldendorf"
EVENT_GPS="51.875222,9.648111"  # 51°52'30.8"N 9°38'53.2"E in decimal

# Metadata
AUTHOR="Jan Doberstein"
ARTIST="pixelpiste"
COPYRIGHT="Unlicense - Public Domain"

# Watermark text (placed at lower right corner)
WATERMARK="Jan Doberstein - enduroeXperience"

# Export settings
MAX_FILE_SIZE_KB=2048  # ~2MB target size
EXPORT_QUALITY=85      # JPEG quality (will be reduced if file too large)

# =============================================================================
# Functions
# =============================================================================

show_help() {
    cat << 'EOF'
Enduro Event Workflow - Complete photo processing pipeline

Usage: enduro-workflow.sh [OPTIONS] <source>

Arguments:
  <source>              SD card path or folder with photos

Options:
  -o, --output DIR      Output directory for exports (default: ~/Desktop/EnduroExport)
  -e, --event NAME      Event name (default: "YYYY-MM-DD Endurotraining")
  -d, --day NUMBER      Day number for multi-day events (1 or 2)
  --darktable-preset P  Darktable preset/style to apply
  --skip-import         Skip import, process existing library folder
  --skip-develop        Skip RAW development
  -y, --yes             Skip confirmation, start immediately
  -h, --help            Show this help

Examples:
  # Full workflow from SD card
  enduro-workflow.sh /Volumes/EOS_DIGITAL

  # Day 2 of event
  enduro-workflow.sh /Volumes/EOS_DIGITAL --day 2

  # Process already imported photos
  enduro-workflow.sh --skip-import ~/Pictures/PhotoLibrary/2026-01-24

  # Use specific darktable preset
  enduro-workflow.sh /Volumes/EOS_DIGITAL --darktable-preset "Enduro Action"

EOF
}

# Convert DMS to decimal degrees
# Already converted in config: 51°52'30.8"N 9°38'53.2"E = 51.875222, 9.648111

get_event_name() {
    local day="$1"
    local date_str
    date_str=$(date +%Y-%m-%d)
    
    if [[ -n "$day" ]]; then
        echo "${date_str} Endurotraining Tag ${day}"
    else
        echo "${date_str} Endurotraining"
    fi
}

# Count files by extension in a directory
count_files_by_type() {
    local dir="$1"
    local raw_count=0
    local jpg_count=0
    local other_count=0
    
    while IFS= read -r -d '' file; do
        local ext
        ext=$(echo "${file##*.}" | tr '[:upper:]' '[:lower:]')
        case "$ext" in
            cr2|cr3|nef|arw|orf|rw2|dng|raf)
                ((++raw_count))
                ;;
            jpg|jpeg)
                ((++jpg_count))
                ;;
            *)
                ((++other_count))
                ;;
        esac
    done < <(find "$dir" -type f \( -iname "*.cr2" -o -iname "*.cr3" -o -iname "*.nef" -o -iname "*.arw" -o -iname "*.orf" -o -iname "*.rw2" -o -iname "*.dng" -o -iname "*.raf" -o -iname "*.jpg" -o -iname "*.jpeg" \) -print0 2>/dev/null)
    
    echo "$raw_count $jpg_count $other_count"
}

# Calculate total size of files
calculate_size() {
    local dir="$1"
    local total_bytes=0
    
    while IFS= read -r -d '' file; do
        local size
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
        total_bytes=$((total_bytes + size))
    done < <(find "$dir" -type f \( -iname "*.cr2" -o -iname "*.cr3" -o -iname "*.nef" -o -iname "*.arw" -o -iname "*.orf" -o -iname "*.rw2" -o -iname "*.dng" -o -iname "*.raf" -o -iname "*.jpg" -o -iname "*.jpeg" \) -print0 2>/dev/null)
    
    echo "$total_bytes"
}

# Format bytes to human readable
format_size() {
    local bytes="$1"
    if [[ $bytes -ge 1073741824 ]]; then
        echo "$(echo "scale=1; $bytes / 1073741824" | bc) GB"
    elif [[ $bytes -ge 1048576 ]]; then
        echo "$(echo "scale=1; $bytes / 1048576" | bc) MB"
    elif [[ $bytes -ge 1024 ]]; then
        echo "$(echo "scale=1; $bytes / 1024" | bc) KB"
    else
        echo "$bytes bytes"
    fi
}

# Show detailed plan and ask for confirmation
show_plan_and_confirm() {
    local source="$1"
    local output_dir="$2"
    local event_name="$3"
    local skip_import="$4"
    local skip_develop="$5"
    local darktable_preset="$6"
    local auto_yes="$7"
    
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║                    ENDURO EVENT WORKFLOW - PLAN                      ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Scan source directory
    log_info "Scanning source directory..."
    local counts size_bytes
    counts=$(count_files_by_type "$source")
    size_bytes=$(calculate_size "$source")
    
    local raw_count jpg_count other_count
    raw_count=$(echo "$counts" | cut -d' ' -f1)
    jpg_count=$(echo "$counts" | cut -d' ' -f2)
    other_count=$(echo "$counts" | cut -d' ' -f3)
    local total_count=$((raw_count + jpg_count))
    
    echo ""
    echo "┌──────────────────────────────────────────────────────────────────────┐"
    echo "│  SOURCE ANALYSIS                                                     │"
    echo "├──────────────────────────────────────────────────────────────────────┤"
    printf "│  %-68s │\n" "Path: $source"
    printf "│  %-68s │\n" ""
    printf "│  %-68s │\n" "Files found:"
    printf "│    %-66s │\n" "RAW files (CR2/CR3/NEF/ARW/etc.): $raw_count"
    printf "│    %-66s │\n" "JPG files:                        $jpg_count"
    printf "│    %-66s │\n" "─────────────────────────────────────"
    printf "│    %-66s │\n" "Total photos:                     $total_count"
    printf "│  %-68s │\n" ""
    printf "│  %-68s │\n" "Total size: $(format_size "$size_bytes")"
    echo "└──────────────────────────────────────────────────────────────────────┘"
    echo ""
    
    echo "┌──────────────────────────────────────────────────────────────────────┐"
    echo "│  METADATA TO BE APPLIED                                             │"
    echo "├──────────────────────────────────────────────────────────────────────┤"
    printf "│  %-68s │\n" "Event:     $event_name"
    printf "│  %-68s │\n" "Location:  $EVENT_LOCATION"
    printf "│  %-68s │\n" "GPS:       $EVENT_GPS (if missing on photos)"
    printf "│  %-68s │\n" ""
    printf "│  %-68s │\n" "Author:    $AUTHOR"
    printf "│  %-68s │\n" "Artist:    $ARTIST"
    printf "│  %-68s │\n" "Copyright: $COPYRIGHT"
    echo "└──────────────────────────────────────────────────────────────────────┘"
    echo ""
    
    echo "┌──────────────────────────────────────────────────────────────────────┐"
    echo "│  EXPORT SETTINGS                                                    │"
    echo "├──────────────────────────────────────────────────────────────────────┤"
    printf "│  %-68s │\n" "Output:      $output_dir"
    printf "│  %-68s │\n" "Watermark:   \"$WATERMARK\""
    printf "│  %-68s │\n" "Position:    Lower right corner"
    printf "│  %-68s │\n" "Max size:    ${MAX_FILE_SIZE_KB} KB (~$((MAX_FILE_SIZE_KB / 1024)) MB per image)"
    printf "│  %-68s │\n" "Quality:     ${EXPORT_QUALITY}% (reduced if needed)"
    if [[ -n "$darktable_preset" ]]; then
        printf "│  %-68s │\n" "Preset:      $darktable_preset"
    fi
    echo "└──────────────────────────────────────────────────────────────────────┘"
    echo ""
    
    echo "┌──────────────────────────────────────────────────────────────────────┐"
    echo "│  WORKFLOW STEPS                                                     │"
    echo "├──────────────────────────────────────────────────────────────────────┤"
    if [[ "$skip_import" == "true" ]]; then
        printf "│  %-68s │\n" "[ SKIP ] 1. Import photos from source"
    else
        printf "│  %-68s │\n" "[  DO  ] 1. Import $total_count photos to library"
    fi
    printf "│  %-68s │\n" "[  DO  ] 2. Set EXIF metadata (author, artist, GPS)"
    if [[ "$skip_develop" == "true" ]]; then
        printf "│  %-68s │\n" "[ SKIP ] 3. Develop RAW files to JPG"
    else
        if [[ $raw_count -gt 0 ]]; then
            printf "│  %-68s │\n" "[  DO  ] 3. Develop $raw_count RAW files to JPG"
        else
            printf "│  %-68s │\n" "[  --  ] 3. No RAW files to develop"
        fi
    fi
    printf "│  %-68s │\n" "[  DO  ] 4. Export with watermark + compression"
    printf "│  %-68s │\n" "[  DO  ] 5. Generate checksums"
    echo "└──────────────────────────────────────────────────────────────────────┘"
    echo ""
    
    if [[ $total_count -eq 0 ]]; then
        log_error "No photos found in source directory!"
        exit 1
    fi
    
    # Confirmation
    if [[ "$auto_yes" == "true" ]]; then
        log_info "Auto-confirmed with --yes flag"
        return 0
    fi
    
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║  Type YES to start processing, or anything else to abort            ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo -n "Confirm: "
    read -r confirmation
    
    if [[ "$confirmation" != "YES" ]]; then
        echo ""
        log_warn "Aborted by user."
        exit 0
    fi
    
    echo ""
    log_success "Confirmed. Starting workflow..."
    echo ""
}

# Add watermark to image using ImageMagick
add_watermark() {
    local input="$1"
    local output="$2"
    local text="$WATERMARK"
    
    # Get image dimensions
    local width height
    width=$(identify -format "%w" "$input")
    height=$(identify -format "%h" "$input")
    
    # Calculate font size (approximately 1.5% of image width)
    local fontsize=$((width * 15 / 1000))
    [[ $fontsize -lt 12 ]] && fontsize=12
    [[ $fontsize -gt 48 ]] && fontsize=48
    
    # Margin from edge (2% of smaller dimension)
    local margin
    if [[ $width -lt $height ]]; then
        margin=$((width * 2 / 100))
    else
        margin=$((height * 2 / 100))
    fi
    [[ $margin -lt 10 ]] && margin=10
    
    convert "$input" \
        -gravity SouthEast \
        -fill "rgba(255,255,255,0.7)" \
        -stroke "rgba(0,0,0,0.3)" \
        -strokewidth 1 \
        -pointsize "$fontsize" \
        -annotate +"$margin"+"$margin" "$text" \
        "$output"
}

# Compress image to target size
compress_to_size() {
    local input="$1"
    local output="$2"
    local target_kb="$3"
    local quality="$EXPORT_QUALITY"
    
    cp "$input" "$output"
    
    local current_size
    current_size=$(stat -f%z "$output" 2>/dev/null || stat -c%s "$output")
    local target_bytes=$((target_kb * 1024))
    
    # Reduce quality until file is small enough
    while [[ $current_size -gt $target_bytes ]] && [[ $quality -gt 50 ]]; do
        convert "$output" -quality "$quality" "$output"
        current_size=$(stat -f%z "$output" 2>/dev/null || stat -c%s "$output")
        quality=$((quality - 5))
    done
    
    # If still too large, resize
    if [[ $current_size -gt $target_bytes ]]; then
        local scale=90
        while [[ $current_size -gt $target_bytes ]] && [[ $scale -gt 50 ]]; do
            convert "$input" -resize "${scale}%" -quality 75 "$output"
            current_size=$(stat -f%z "$output" 2>/dev/null || stat -c%s "$output")
            scale=$((scale - 10))
        done
    fi
}

# =============================================================================
# Main Script
# =============================================================================

main() {
    local source=""
    local output_dir="$HOME/Desktop/EnduroExport"
    local event_name=""
    local day=""
    local darktable_preset=""
    local skip_import=false
    local skip_develop=false
    local auto_yes=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -o|--output)
                output_dir="$2"
                shift 2
                ;;
            -e|--event)
                event_name="$2"
                shift 2
                ;;
            -d|--day)
                day="$2"
                shift 2
                ;;
            --darktable-preset)
                darktable_preset="$2"
                shift 2
                ;;
            --skip-import)
                skip_import=true
                shift
                ;;
            --skip-develop)
                skip_develop=true
                shift
                ;;
            -y|--yes)
                auto_yes=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            -*)
                log_error "Unknown option: $1"
                exit 1
                ;;
            *)
                source="$1"
                shift
                ;;
        esac
    done
    
    # Validate
    if [[ -z "$source" ]]; then
        log_error "Source path required"
        show_help
        exit 1
    fi
    
    if [[ ! -d "$source" ]]; then
        log_error "Source not found: $source"
        exit 1
    fi
    
    # Set event name if not provided
    [[ -z "$event_name" ]] && event_name=$(get_event_name "$day")
    
    # Show plan and get confirmation
    show_plan_and_confirm "$source" "$output_dir" "$event_name" \
        "$skip_import" "$skip_develop" "$darktable_preset" "$auto_yes"
    
    local library_dir="$source"
    
    # -------------------------------------------------------------------------
    # Step 1: Import from SD card
    # -------------------------------------------------------------------------
    if [[ "$skip_import" == "false" ]]; then
        log_info "[1/5] Importing photos..."
        
        "$PIXELGROOMER_ROOT/bin/pg-import" "$source" \
            --event "$event_name" \
            --location "$EVENT_LOCATION" \
            --author "$AUTHOR" \
            --copyright "$COPYRIGHT"
        
        # Get the import target directory
        local date_str
        date_str=$(date +%Y-%m-%d)
        library_dir="${PHOTO_LIBRARY}/${date_str}"
    else
        log_info "[1/5] Skipping import (--skip-import)"
        library_dir="$source"
    fi
    
    echo ""
    
    # -------------------------------------------------------------------------
    # Step 2: Set additional EXIF metadata
    # -------------------------------------------------------------------------
    log_info "[2/5] Setting EXIF metadata..."
    
    # Set artist field
    "$PIXELGROOMER_ROOT/bin/pg-exif" set "$library_dir" \
        --artist "$ARTIST" \
        --recursive
    
    # Set GPS if not present on photos
    "$PIXELGROOMER_ROOT/bin/pg-exif" set "$library_dir" \
        --gps "$EVENT_GPS" \
        --if-missing \
        --recursive
    
    echo ""
    
    # -------------------------------------------------------------------------
    # Step 3: Develop RAW files
    # -------------------------------------------------------------------------
    local develop_dir="${library_dir}/developed"
    
    if [[ "$skip_develop" == "false" ]]; then
        log_info "[3/5] Developing RAW files..."
        
        local -a develop_args=("$library_dir" "--output" "$develop_dir" "--recursive")
        
        if [[ -n "$darktable_preset" ]]; then
            develop_args+=("--preset" "$darktable_preset")
        fi
        
        "$PIXELGROOMER_ROOT/bin/pg-develop" "${develop_args[@]}"
    else
        log_info "[3/5] Skipping RAW development (--skip-develop)"
    fi
    
    echo ""
    
    # -------------------------------------------------------------------------
    # Step 4: Create export with watermark and compression
    # -------------------------------------------------------------------------
    log_info "[4/5] Creating web export with watermark..."
    
    mkdir -p "$output_dir"
    
    # Find all JPG files (developed or original)
    local -a jpg_files=()
    local search_dir="$develop_dir"
    [[ ! -d "$search_dir" ]] && search_dir="$library_dir"
    
    while IFS= read -r -d '' file; do
        jpg_files+=("$file")
    done < <(find "$search_dir" -type f \( -iname "*.jpg" -o -iname "*.jpeg" \) -print0 2>/dev/null)
    
    local total=${#jpg_files[@]}
    
    if [[ $total -eq 0 ]]; then
        log_warn "No JPG files found in $search_dir"
    else
        log_info "Processing $total images..."
        
        local i=0
        for file in "${jpg_files[@]}"; do
            ((++i))
            local basename
            basename=$(basename "$file")
            local output_file="${output_dir}/${basename}"
            
            log_progress "$i" "$total" "Exporting"
            
            # Create temp file for watermarked version
            local temp_file
            temp_file=$(mktemp -t enduro_export.XXXXXX.jpg)
            
            # Add watermark
            add_watermark "$file" "$temp_file"
            
            # Compress to target size
            compress_to_size "$temp_file" "$output_file" "$MAX_FILE_SIZE_KB"
            
            rm -f "$temp_file"
        done
        
        echo ""  # Clear progress line
        log_success "Exported $total images to $output_dir"
    fi
    
    echo ""
    
    # -------------------------------------------------------------------------
    # Step 5: Generate checksums
    # -------------------------------------------------------------------------
    log_info "[5/5] Generating checksums..."
    
    "$PIXELGROOMER_ROOT/bin/pg-verify" generate "$library_dir"
    "$PIXELGROOMER_ROOT/bin/pg-verify" generate "$output_dir"
    
    echo ""
    log_success "======================================"
    log_success "Workflow complete!"
    log_success "======================================"
    log_info "Library:  $library_dir"
    log_info "Export:   $output_dir"
    echo ""
    log_info "Participants can download from: $output_dir"
}

# Run main
main "$@"
