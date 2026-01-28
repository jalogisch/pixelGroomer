#!/usr/bin/env bash
# PixelGroomer - Daily Offload Workflow
# Simple SD card offload for multi-day events
#
# This script is designed for repeated daily use during multi-day events.
# It imports photos from SD card to the archive with consistent metadata.
# Date is automatically determined from when the script runs.
#
# Usage:
#   1. Copy this script and customize the configuration section
#   2. Run daily: ./daily-offload.sh /Volumes/EOS_DIGITAL
#   3. Photos are imported with consistent metadata, organized by date

set -euo pipefail

# Get script directory and load libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIXELGROOMER_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=../lib/config.sh disable=SC1091
source "$PIXELGROOMER_ROOT/lib/config.sh"
# shellcheck source=../lib/utils.sh disable=SC1091
source "$PIXELGROOMER_ROOT/lib/utils.sh"

# =============================================================================
# Configuration - Customize these for your event
# =============================================================================

# Event information
EVENT_NAME="GS Treffen 2026"           # Base name for the event
EVENT_LOCATION="Garmisch-Partenkirchen"
EVENT_GPS="47.5000,11.1000"            # GPS coordinates (decimal format)

# Photographer metadata
AUTHOR="Jan Doberstein"
ARTIST="pixelpiste"
COPYRIGHT="Unlicense - Public Domain"

# =============================================================================
# Functions
# =============================================================================

show_help() {
    cat << 'EOF'
Daily Offload - Simple SD card import for multi-day events

Usage: daily-offload.sh [OPTIONS] <source>

Arguments:
  <source>              SD card path or folder with photos

Options:
  -o, --output DIR      Override archive directory
  -d, --day NUMBER      Manual day number (default: auto from date)
  -y, --yes             Skip confirmation
  -n, --dry-run         Show what would be done without changes
  -h, --help            Show this help

Examples:
  # Day 1 of event
  daily-offload.sh /Volumes/EOS_DIGITAL

  # Explicit day number
  daily-offload.sh /Volumes/EOS_DIGITAL --day 2

  # Different archive location
  daily-offload.sh /Volumes/EOS_DIGITAL --output /Volumes/Archive

EOF
}

# Count photo files
count_photos() {
    local dir="$1"
    local count=0
    
    while IFS= read -r -d '' _; do
        ((++count))
    done < <(find "$dir" -type f \( \
        -iname "*.cr2" -o -iname "*.cr3" -o -iname "*.nef" -o \
        -iname "*.arw" -o -iname "*.orf" -o -iname "*.rw2" -o \
        -iname "*.dng" -o -iname "*.raf" -o -iname "*.jpg" -o \
        -iname "*.jpeg" \) -print0 2>/dev/null)
    
    echo "$count"
}

# Calculate total size
calculate_size() {
    local dir="$1"
    local total_bytes=0
    
    while IFS= read -r -d '' file; do
        local size
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
        total_bytes=$((total_bytes + size))
    done < <(find "$dir" -type f \( \
        -iname "*.cr2" -o -iname "*.cr3" -o -iname "*.nef" -o \
        -iname "*.arw" -o -iname "*.orf" -o -iname "*.rw2" -o \
        -iname "*.dng" -o -iname "*.raf" -o -iname "*.jpg" -o \
        -iname "*.jpeg" \) -print0 2>/dev/null)
    
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

# Show plan and confirm
show_plan() {
    local source="$1"
    local output_dir="$2"
    local event_full="$3"
    local auto_yes="$4"
    local dry_run="$5"
    
    local photo_count size_bytes
    photo_count=$(count_photos "$source")
    size_bytes=$(calculate_size "$source")
    
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║                     DAILY OFFLOAD - PLAN                             ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    echo ""
    
    echo "┌──────────────────────────────────────────────────────────────────────┐"
    echo "│  SOURCE                                                              │"
    echo "├──────────────────────────────────────────────────────────────────────┤"
    printf "│  %-68s │\n" "Path:   $source"
    printf "│  %-68s │\n" "Photos: $photo_count files"
    printf "│  %-68s │\n" "Size:   $(format_size "$size_bytes")"
    echo "└──────────────────────────────────────────────────────────────────────┘"
    echo ""
    
    echo "┌──────────────────────────────────────────────────────────────────────┐"
    echo "│  METADATA                                                            │"
    echo "├──────────────────────────────────────────────────────────────────────┤"
    printf "│  %-68s │\n" "Event:     $event_full"
    printf "│  %-68s │\n" "Location:  $EVENT_LOCATION"
    printf "│  %-68s │\n" "GPS:       $EVENT_GPS"
    printf "│  %-68s │\n" "Author:    $AUTHOR"
    printf "│  %-68s │\n" "Artist:    $ARTIST"
    printf "│  %-68s │\n" "Copyright: $COPYRIGHT"
    echo "└──────────────────────────────────────────────────────────────────────┘"
    echo ""
    
    echo "┌──────────────────────────────────────────────────────────────────────┐"
    echo "│  TARGET                                                              │"
    echo "├──────────────────────────────────────────────────────────────────────┤"
    printf "│  %-68s │\n" "Archive: $output_dir"
    echo "└──────────────────────────────────────────────────────────────────────┘"
    echo ""
    
    if [[ $photo_count -eq 0 ]]; then
        log_error "No photos found in source directory!"
        exit 1
    fi
    
    if [[ "$dry_run" == "true" ]]; then
        log_info "Dry run - no changes will be made"
        return 0
    fi
    
    if [[ "$auto_yes" == "true" ]]; then
        log_info "Auto-confirmed with --yes flag"
        return 0
    fi
    
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║  Type YES to start import, or anything else to abort                 ║"
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
}

# =============================================================================
# Main Script
# =============================================================================

main() {
    local source=""
    local output_dir=""
    local day_number=""
    local auto_yes=false
    local dry_run=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -o|--output)
                output_dir="$2"
                shift 2
                ;;
            -d|--day)
                day_number="$2"
                shift 2
                ;;
            -y|--yes)
                auto_yes=true
                shift
                ;;
            -n|--dry-run)
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
    
    # Validate source
    if [[ -z "$source" ]]; then
        log_error "Source path required"
        show_help
        exit 1
    fi
    
    if [[ ! -d "$source" ]]; then
        log_error "Source not found: $source"
        exit 1
    fi
    
    # Build event name with day
    local date_str event_full
    date_str=$(date +%Y-%m-%d)
    
    if [[ -n "$day_number" ]]; then
        event_full="${EVENT_NAME} - Tag ${day_number}"
    else
        event_full="${EVENT_NAME} - ${date_str}"
    fi
    
    # Use default archive if not specified
    [[ -z "$output_dir" ]] && output_dir="${PHOTO_LIBRARY:-$HOME/Pictures/PhotoLibrary}"
    
    # Show plan
    show_plan "$source" "$output_dir" "$event_full" "$auto_yes" "$dry_run"
    
    if [[ "$dry_run" == "true" ]]; then
        log_info "Dry run complete - no changes made"
        exit 0
    fi
    
    # -------------------------------------------------------------------------
    # Step 1: Import photos
    # -------------------------------------------------------------------------
    log_info "[1/3] Importing photos..."
    
    "$PIXELGROOMER_ROOT/bin/pg-import" "$source" \
        --event "$event_full" \
        --location "$EVENT_LOCATION" \
        --author "$AUTHOR" \
        --copyright "$COPYRIGHT"
    
    # Get the import target directory
    local library_dir="${output_dir}/${date_str}"
    
    echo ""
    
    # -------------------------------------------------------------------------
    # Step 2: Set additional EXIF metadata
    # -------------------------------------------------------------------------
    log_info "[2/3] Setting additional metadata..."
    
    # Set artist field
    "$PIXELGROOMER_ROOT/bin/pg-exif" set "$library_dir" \
        --artist "$ARTIST" \
        --recursive
    
    # Set GPS if configured and not present
    if [[ -n "$EVENT_GPS" ]]; then
        "$PIXELGROOMER_ROOT/bin/pg-exif" set "$library_dir" \
            --gps "$EVENT_GPS" \
            --if-missing \
            --recursive
    fi
    
    echo ""
    
    # -------------------------------------------------------------------------
    # Step 3: Generate checksums
    # -------------------------------------------------------------------------
    log_info "[3/3] Generating checksums..."
    
    "$PIXELGROOMER_ROOT/bin/pg-verify" generate "$library_dir"
    
    echo ""
    log_success "======================================"
    log_success "Daily offload complete!"
    log_success "======================================"
    log_info "Photos imported to: $library_dir"
    echo ""
}

# Run main
main "$@"
