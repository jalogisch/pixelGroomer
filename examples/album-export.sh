#!/usr/bin/env bash
# PixelGroomer - Album Export Workflow
# Export album with proper licensing metadata and watermark
#
# This script prepares photos for sharing:
# - Sets licensing metadata (CC BY-NC-SA 4.0)
# - Adds copyright and usage terms
# - Exports with watermark and compression
#
# Usage:
#   ./album-export.sh "Album_Name" --output ~/Desktop/Export

set -euo pipefail

# Get script directory and load libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIXELGROOMER_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=../lib/config.sh disable=SC1091
source "$PIXELGROOMER_ROOT/lib/config.sh"
# shellcheck source=../lib/utils.sh disable=SC1091
source "$PIXELGROOMER_ROOT/lib/utils.sh"

# =============================================================================
# Configuration - Customize these for your needs
# =============================================================================

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

# =============================================================================
# Functions
# =============================================================================

show_help() {
    cat << 'EOF'
Album Export - Export with licensing metadata and watermark

Usage: album-export.sh [OPTIONS] <album-name-or-folder>

Arguments:
  <album-name-or-folder>   Album name or path to folder with photos

Options:
  -o, --output DIR         Export directory (required)
  -q, --quality NUM        JPEG quality 1-100 (default: 85)
  --no-watermark           Skip watermark
  -y, --yes                Skip confirmation
  -n, --dry-run            Show what would be done
  -h, --help               Show this help

Examples:
  # Export album with watermark
  album-export.sh "GS_Treffen_Highlights" --output ~/Desktop/Export

  # Export folder directly
  album-export.sh ~/Pictures/PhotoLibrary/2026-07-10 --output ~/Desktop/Share

  # Higher quality, no watermark
  album-export.sh "Alps_Tour" --output ~/Desktop/Print --quality 95 --no-watermark

EOF
}

# Build copyright string with current year
get_copyright_string() {
    local year
    year=$(date +%Y)
    echo "(c) ${year} ${CREATOR_NAME}. Alle Rechte vorbehalten."
}

# Count image files
count_images() {
    local dir="$1"
    local count=0
    
    while IFS= read -r -d '' _; do
        ((++count))
    done < <(find "$dir" -type f \( \
        -iname "*.jpg" -o -iname "*.jpeg" -o \
        -iname "*.cr2" -o -iname "*.cr3" -o -iname "*.nef" -o \
        -iname "*.arw" -o -iname "*.dng" \) -print0 2>/dev/null)
    
    echo "$count"
}

# Resolve album name to folder path
resolve_album_path() {
    local input="$1"
    
    # If it's already a directory, return it
    if [[ -d "$input" ]]; then
        echo "$input"
        return 0
    fi
    
    # Try as album name
    local album_dir="${ALBUM_DIR:-$HOME/Pictures/Albums}"
    local album_path="${album_dir}/${input}"
    
    if [[ -d "$album_path" ]]; then
        echo "$album_path"
        return 0
    fi
    
    # Not found
    return 1
}

# Add watermark to image
add_watermark() {
    local input="$1"
    local output="$2"
    
    # Get image dimensions
    local width height
    width=$(identify -format "%w" "$input")
    height=$(identify -format "%h" "$input")
    
    # Calculate font size (small - about 1% of width, min 10px, max 24px)
    local fontsize=$((width / 100))
    [[ $fontsize -lt 10 ]] && fontsize=10
    [[ $fontsize -gt 24 ]] && fontsize=24
    
    # Margin from edge (1.5% of smaller dimension)
    local margin
    if [[ $width -lt $height ]]; then
        margin=$((width * 15 / 1000))
    else
        margin=$((height * 15 / 1000))
    fi
    [[ $margin -lt 8 ]] && margin=8
    
    # Apply watermark with shadow for visibility
    convert "$input" \
        -gravity SouthEast \
        -fill "rgba(255,255,255,${WATERMARK_OPACITY})" \
        -stroke "rgba(0,0,0,0.3)" \
        -strokewidth 1 \
        -pointsize "$fontsize" \
        -annotate +"$margin"+"$margin" "$WATERMARK_TEXT" \
        -quality "$EXPORT_QUALITY" \
        "$output"
}

# Export without watermark
export_plain() {
    local input="$1"
    local output="$2"
    
    convert "$input" -quality "$EXPORT_QUALITY" "$output"
}

# Show plan and confirm
show_plan() {
    local source_path="$1"
    local output_dir="$2"
    local use_watermark="$3"
    local auto_yes="$4"
    local dry_run="$5"
    
    local image_count
    image_count=$(count_images "$source_path")
    local copyright_str
    copyright_str=$(get_copyright_string)
    
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║                     ALBUM EXPORT - PLAN                              ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    echo ""
    
    echo "┌──────────────────────────────────────────────────────────────────────┐"
    echo "│  SOURCE                                                              │"
    echo "├──────────────────────────────────────────────────────────────────────┤"
    printf "│  %-68s │\n" "Path:   $source_path"
    printf "│  %-68s │\n" "Images: $image_count files"
    echo "└──────────────────────────────────────────────────────────────────────┘"
    echo ""
    
    echo "┌──────────────────────────────────────────────────────────────────────┐"
    echo "│  LICENSING METADATA                                                  │"
    echo "├──────────────────────────────────────────────────────────────────────┤"
    printf "│  %-68s │\n" "License:          $LICENSE"
    printf "│  %-68s │\n" "Copyright:        $copyright_str"
    printf "│  %-68s │\n" "Copyright Status: $COPYRIGHT_STATUS"
    printf "│  %-68s │\n" "Creator:          $CREATOR_NAME"
    printf "│  %-68s │\n" "Contact:          $CREATOR_EMAIL"
    printf "│  %-68s │\n" ""
    printf "│  %-68s │\n" "Usage Terms:"
    printf "│    %-66s │\n" "$USAGE_TERMS"
    echo "└──────────────────────────────────────────────────────────────────────┘"
    echo ""
    
    echo "┌──────────────────────────────────────────────────────────────────────┐"
    echo "│  EXPORT SETTINGS                                                     │"
    echo "├──────────────────────────────────────────────────────────────────────┤"
    printf "│  %-68s │\n" "Output:    $output_dir"
    printf "│  %-68s │\n" "Quality:   ${EXPORT_QUALITY}%"
    if [[ "$use_watermark" == "true" ]]; then
        printf "│  %-68s │\n" "Watermark: \"$WATERMARK_TEXT\" (lower right, $WATERMARK_COLOR)"
    else
        printf "│  %-68s │\n" "Watermark: disabled"
    fi
    echo "└──────────────────────────────────────────────────────────────────────┘"
    echo ""
    
    if [[ $image_count -eq 0 ]]; then
        log_error "No images found in source!"
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
    echo "║  Type YES to start export, or anything else to abort                 ║"
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
    local input=""
    local output_dir=""
    local use_watermark=true
    local auto_yes=false
    local dry_run=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -o|--output)
                output_dir="$2"
                shift 2
                ;;
            -q|--quality)
                EXPORT_QUALITY="$2"
                shift 2
                ;;
            --no-watermark)
                use_watermark=false
                shift
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
                input="$1"
                shift
                ;;
        esac
    done
    
    # Validate input
    if [[ -z "$input" ]]; then
        log_error "Album name or folder path required"
        show_help
        exit 1
    fi
    
    if [[ -z "$output_dir" ]]; then
        log_error "Output directory required (use --output)"
        show_help
        exit 1
    fi
    
    # Resolve source path
    local source_path
    if ! source_path=$(resolve_album_path "$input"); then
        log_error "Album or folder not found: $input"
        exit 1
    fi
    
    # Show plan
    show_plan "$source_path" "$output_dir" "$use_watermark" "$auto_yes" "$dry_run"
    
    if [[ "$dry_run" == "true" ]]; then
        log_info "Dry run complete - no changes made"
        exit 0
    fi
    
    # Create output directory
    mkdir -p "$output_dir"
    
    # Create temp directory for intermediate files
    local temp_dir
    temp_dir=$(mktemp -d -t album_export.XXXXXX)
    # shellcheck disable=SC2064
    trap "rm -rf '$temp_dir'" EXIT
    
    # -------------------------------------------------------------------------
    # Step 1: Copy/develop images to temp
    # -------------------------------------------------------------------------
    log_info "[1/3] Preparing images..."
    
    local -a source_files=()
    while IFS= read -r -d '' file; do
        source_files+=("$file")
    done < <(find "$source_path" -type f \( \
        -iname "*.jpg" -o -iname "*.jpeg" -o \
        -iname "*.cr2" -o -iname "*.cr3" -o -iname "*.nef" -o \
        -iname "*.arw" -o -iname "*.dng" \) -print0 2>/dev/null | sort -z)
    
    local total=${#source_files[@]}
    local i=0
    local -a temp_files=()
    
    for file in "${source_files[@]}"; do
        ((++i))
        local basename ext temp_file
        basename=$(basename "$file")
        ext=$(echo "${basename##*.}" | tr '[:upper:]' '[:lower:]')
        
        log_progress "$i" "$total" "Preparing"
        
        # If RAW, develop first
        if [[ "$ext" =~ ^(cr2|cr3|nef|arw|dng|orf|rw2|raf)$ ]]; then
            temp_file="${temp_dir}/${basename%.*}.jpg"
            "$PIXELGROOMER_ROOT/bin/pg-develop" "$file" --output "$temp_dir" --quality "$EXPORT_QUALITY" 2>/dev/null
        else
            # Copy JPG
            temp_file="${temp_dir}/${basename}"
            cp "$file" "$temp_file"
        fi
        
        temp_files+=("$temp_file")
    done
    
    echo ""
    
    # -------------------------------------------------------------------------
    # Step 2: Set licensing metadata on temp files
    # -------------------------------------------------------------------------
    log_info "[2/3] Setting licensing metadata..."
    
    local copyright_str
    copyright_str=$(get_copyright_string)
    
    i=0
    for file in "${temp_files[@]}"; do
        ((++i))
        [[ ! -f "$file" ]] && continue
        
        log_progress "$i" "$total" "Metadata"
        
        # Set all licensing metadata using exiftool directly
        exiftool -overwrite_original -q \
            -XMP-dc:Rights="$LICENSE" \
            -XMP-xmpRights:WebStatement="https://creativecommons.org/licenses/by-nc-sa/4.0/" \
            -XMP-xmpRights:UsageTerms="$USAGE_TERMS" \
            -XMP-xmpRights:Marked="True" \
            -XMP-photoshop:Credit="$CREATOR_NAME" \
            -IPTC:CopyrightNotice="$copyright_str" \
            -EXIF:Copyright="$copyright_str" \
            -EXIF:Artist="$CREATOR_NAME" \
            -IPTC:By-line="$CREATOR_NAME" \
            -XMP-dc:Creator="$CREATOR_NAME" \
            -XMP-iptcCore:CreatorContactInfo-CiEmailWork="$CREATOR_EMAIL" \
            -XMP-plus:CopyrightStatus="$COPYRIGHT_STATUS" \
            "$file" 2>/dev/null || true
    done
    
    echo ""
    
    # -------------------------------------------------------------------------
    # Step 3: Export with watermark
    # -------------------------------------------------------------------------
    log_info "[3/3] Exporting with watermark..."
    
    i=0
    for file in "${temp_files[@]}"; do
        ((++i))
        [[ ! -f "$file" ]] && continue
        
        local basename output_file
        basename=$(basename "$file")
        output_file="${output_dir}/${basename}"
        
        log_progress "$i" "$total" "Exporting"
        
        if [[ "$use_watermark" == "true" ]]; then
            add_watermark "$file" "$output_file"
        else
            export_plain "$file" "$output_file"
        fi
    done
    
    echo ""
    
    # -------------------------------------------------------------------------
    # Done
    # -------------------------------------------------------------------------
    log_success "======================================"
    log_success "Album export complete!"
    log_success "======================================"
    log_info "Exported $total images to: $output_dir"
    log_info "License: $LICENSE"
    echo ""
}

# Run main
main "$@"
