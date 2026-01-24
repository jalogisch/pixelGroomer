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
  --dry-run             Show what would be done without doing it
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
    local dry_run=false
    
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
            --dry-run)
                dry_run=true
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
    
    log_info "======================================"
    log_info "Enduro Event Workflow"
    log_info "======================================"
    log_info "Event:    $event_name"
    log_info "Location: $EVENT_LOCATION"
    log_info "Author:   $AUTHOR"
    log_info "Source:   $source"
    log_info "Output:   $output_dir"
    echo ""
    
    if [[ "$dry_run" == "true" ]]; then
        log_warn "DRY RUN - No changes will be made"
        echo ""
    fi
    
    local library_dir="$source"
    
    # -------------------------------------------------------------------------
    # Step 1: Import from SD card
    # -------------------------------------------------------------------------
    if [[ "$skip_import" == "false" ]]; then
        log_info "[1/5] Importing photos..."
        
        if [[ "$dry_run" == "true" ]]; then
            log_info "Would run: pg-import '$source' --event '$event_name' --location '$EVENT_LOCATION'"
        else
            "$PIXELGROOMER_ROOT/bin/pg-import" "$source" \
                --event "$event_name" \
                --location "$EVENT_LOCATION" \
                --author "$AUTHOR" \
                --copyright "$COPYRIGHT"
            
            # Get the import target directory
            local date_str
            date_str=$(date +%Y-%m-%d)
            library_dir="${PHOTO_LIBRARY}/${date_str}"
        fi
    else
        log_info "[1/5] Skipping import (--skip-import)"
        library_dir="$source"
    fi
    
    echo ""
    
    # -------------------------------------------------------------------------
    # Step 2: Set additional EXIF metadata
    # -------------------------------------------------------------------------
    log_info "[2/5] Setting EXIF metadata..."
    
    if [[ "$dry_run" == "true" ]]; then
        log_info "Would run: pg-exif set '$library_dir' --artist '$ARTIST' --gps '$EVENT_GPS'"
    else
        # Set artist field
        "$PIXELGROOMER_ROOT/bin/pg-exif" set "$library_dir" \
            --artist "$ARTIST" \
            --recursive
        
        # Set GPS if not present on photos
        "$PIXELGROOMER_ROOT/bin/pg-exif" set "$library_dir" \
            --gps "$EVENT_GPS" \
            --if-missing \
            --recursive
    fi
    
    echo ""
    
    # -------------------------------------------------------------------------
    # Step 3: Develop RAW files
    # -------------------------------------------------------------------------
    if [[ "$skip_develop" == "false" ]]; then
        log_info "[3/5] Developing RAW files..."
        
        local develop_dir="${library_dir}/developed"
        
        if [[ "$dry_run" == "true" ]]; then
            local preset_arg=""
            [[ -n "$darktable_preset" ]] && preset_arg="--preset '$darktable_preset'"
            log_info "Would run: pg-develop '$library_dir' --output '$develop_dir' $preset_arg"
        else
            local -a develop_args=("$library_dir" "--output" "$develop_dir" "--recursive")
            
            if [[ -n "$darktable_preset" ]]; then
                develop_args+=("--preset" "$darktable_preset")
            fi
            
            "$PIXELGROOMER_ROOT/bin/pg-develop" "${develop_args[@]}"
        fi
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
    local search_dir="${library_dir}/developed"
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
            ((i++))
            local basename
            basename=$(basename "$file")
            local output_file="${output_dir}/${basename}"
            
            log_progress "$i" "$total" "Exporting"
            
            if [[ "$dry_run" == "false" ]]; then
                # Create temp file for watermarked version
                local temp_file
                temp_file=$(mktemp -t enduro_export.XXXXXX.jpg)
                
                # Add watermark
                add_watermark "$file" "$temp_file"
                
                # Compress to target size
                compress_to_size "$temp_file" "$output_file" "$MAX_FILE_SIZE_KB"
                
                rm -f "$temp_file"
            fi
        done
        
        echo ""  # Clear progress line
        log_success "Exported $total images to $output_dir"
    fi
    
    echo ""
    
    # -------------------------------------------------------------------------
    # Step 5: Generate checksums
    # -------------------------------------------------------------------------
    log_info "[5/5] Generating checksums..."
    
    if [[ "$dry_run" == "true" ]]; then
        log_info "Would run: pg-verify generate '$library_dir'"
        log_info "Would run: pg-verify generate '$output_dir'"
    else
        "$PIXELGROOMER_ROOT/bin/pg-verify" generate "$library_dir"
        "$PIXELGROOMER_ROOT/bin/pg-verify" generate "$output_dir"
    fi
    
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
