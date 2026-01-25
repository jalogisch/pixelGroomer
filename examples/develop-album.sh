#!/usr/bin/env bash
# PixelGroomer - Album Development Workflow
# Develop RAW photos from an album with unified styling
#
# This script batch-develops RAW files using a consistent darktable preset,
# ensuring all photos from an event have the same look and feel.
#
# Usage:
#   ./develop-album.sh "Album_Name" --preset "Enduro Action"

set -euo pipefail

# Get script directory and load libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIXELGROOMER_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=../lib/config.sh disable=SC1091
source "$PIXELGROOMER_ROOT/lib/config.sh"
# shellcheck source=../lib/utils.sh disable=SC1091
source "$PIXELGROOMER_ROOT/lib/utils.sh"

# =============================================================================
# Configuration - Customize these for your style
# =============================================================================

# Default darktable preset/style to apply
# Create presets in darktable: styles -> create style from history
DEFAULT_PRESET="Adventure"

# Output quality
JPEG_QUALITY=92

# Output subfolder name (created inside album/source folder)
OUTPUT_SUBFOLDER="developed"

# =============================================================================
# Functions
# =============================================================================

show_help() {
    cat << 'EOF'
Album Development - Develop RAW files with unified styling

Usage: develop-album.sh [OPTIONS] <album-name-or-folder>

Arguments:
  <album-name-or-folder>   Album name or path to folder with RAW files

Options:
  -p, --preset NAME        Darktable preset/style to apply (default: from config)
  -o, --output DIR         Output directory (default: <source>/developed/)
  -q, --quality NUM        JPEG quality 1-100 (default: 92)
  --list-presets           Show available darktable presets
  -y, --yes                Skip confirmation
  -n, --dry-run            Show what would be done
  -h, --help               Show this help

Examples:
  # Develop with default preset
  develop-album.sh "GS_Treffen_Highlights"

  # Use specific preset
  develop-album.sh "Alps_Tour" --preset "Vivid Landscape"

  # Custom output location
  develop-album.sh ~/Pictures/PhotoLibrary/2026-07-10 --output ~/Desktop/Developed

  # List available presets
  develop-album.sh --list-presets

EOF
}

# List available darktable styles/presets
list_presets() {
    local styles_dir="$HOME/.config/darktable/styles"
    
    echo ""
    echo "Available darktable presets:"
    echo "──────────────────────────────"
    
    if [[ -d "$styles_dir" ]]; then
        local count=0
        while IFS= read -r -d '' style_file; do
            local name
            name=$(basename "$style_file" .dtstyle)
            echo "  - $name"
            ((count++))
        done < <(find "$styles_dir" -name "*.dtstyle" -print0 2>/dev/null | sort -z)
        
        if [[ $count -eq 0 ]]; then
            echo "  (no presets found)"
        fi
    else
        echo "  (styles directory not found: $styles_dir)"
    fi
    
    echo ""
    echo "Create presets in darktable:"
    echo "  1. Edit a photo with your desired look"
    echo "  2. Go to 'styles' module (left panel)"
    echo "  3. Click 'create duplicate' or 'create style'"
    echo "  4. Name your style (e.g., 'Enduro Action')"
    echo ""
}

# Count RAW files
count_raw_files() {
    local dir="$1"
    local count=0
    
    while IFS= read -r -d '' _; do
        ((count++))
    done < <(find "$dir" -type f \( \
        -iname "*.cr2" -o -iname "*.cr3" -o -iname "*.nef" -o \
        -iname "*.arw" -o -iname "*.orf" -o -iname "*.rw2" -o \
        -iname "*.dng" -o -iname "*.raf" \) -print0 2>/dev/null)
    
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

# Check if preset exists
check_preset() {
    local preset="$1"
    local styles_dir="$HOME/.config/darktable/styles"
    local style_file="${styles_dir}/${preset}.dtstyle"
    
    if [[ -f "$style_file" ]]; then
        return 0
    fi
    
    return 1
}

# Show plan and confirm
show_plan() {
    local source_path="$1"
    local output_dir="$2"
    local preset="$3"
    local quality="$4"
    local auto_yes="$5"
    local dry_run="$6"
    
    local raw_count
    raw_count=$(count_raw_files "$source_path")
    
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║                   ALBUM DEVELOPMENT - PLAN                           ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    echo ""
    
    echo "┌──────────────────────────────────────────────────────────────────────┐"
    echo "│  SOURCE                                                              │"
    echo "├──────────────────────────────────────────────────────────────────────┤"
    printf "│  %-68s │\n" "Path:      $source_path"
    printf "│  %-68s │\n" "RAW files: $raw_count"
    echo "└──────────────────────────────────────────────────────────────────────┘"
    echo ""
    
    echo "┌──────────────────────────────────────────────────────────────────────┐"
    echo "│  DEVELOPMENT SETTINGS                                                │"
    echo "├──────────────────────────────────────────────────────────────────────┤"
    if [[ -n "$preset" ]]; then
        printf "│  %-68s │\n" "Preset:  $preset"
        if check_preset "$preset"; then
            printf "│  %-68s │\n" "Status:  Found in darktable styles"
        else
            printf "│  %-68s │\n" "Status:  NOT FOUND - will use darktable defaults"
        fi
    else
        printf "│  %-68s │\n" "Preset:  (none - darktable defaults)"
    fi
    printf "│  %-68s │\n" "Quality: ${quality}%"
    printf "│  %-68s │\n" "Output:  $output_dir"
    echo "└──────────────────────────────────────────────────────────────────────┘"
    echo ""
    
    if [[ $raw_count -eq 0 ]]; then
        log_error "No RAW files found in source!"
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
    echo "║  Type YES to start development, or anything else to abort            ║"
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
    local preset="$DEFAULT_PRESET"
    local quality="$JPEG_QUALITY"
    local auto_yes=false
    local dry_run=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -p|--preset)
                preset="$2"
                shift 2
                ;;
            -o|--output)
                output_dir="$2"
                shift 2
                ;;
            -q|--quality)
                quality="$2"
                shift 2
                ;;
            --list-presets)
                list_presets
                exit 0
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
    
    # Resolve source path
    local source_path
    if ! source_path=$(resolve_album_path "$input"); then
        log_error "Album or folder not found: $input"
        exit 1
    fi
    
    # Set default output if not specified
    if [[ -z "$output_dir" ]]; then
        output_dir="${source_path}/${OUTPUT_SUBFOLDER}"
    fi
    
    # Show plan
    show_plan "$source_path" "$output_dir" "$preset" "$quality" "$auto_yes" "$dry_run"
    
    if [[ "$dry_run" == "true" ]]; then
        log_info "Dry run complete - no changes made"
        exit 0
    fi
    
    # Create output directory
    mkdir -p "$output_dir"
    
    # -------------------------------------------------------------------------
    # Collect RAW files
    # -------------------------------------------------------------------------
    log_info "Collecting RAW files..."
    
    local -a raw_files=()
    while IFS= read -r -d '' file; do
        raw_files+=("$file")
    done < <(find "$source_path" -type f \( \
        -iname "*.cr2" -o -iname "*.cr3" -o -iname "*.nef" -o \
        -iname "*.arw" -o -iname "*.orf" -o -iname "*.rw2" -o \
        -iname "*.dng" -o -iname "*.raf" \) -print0 2>/dev/null | sort -z)
    
    local total=${#raw_files[@]}
    
    # -------------------------------------------------------------------------
    # Develop RAW files
    # -------------------------------------------------------------------------
    log_info "Developing $total RAW files with preset '$preset'..."
    echo ""
    
    local i=0
    local success=0
    local failed=0
    
    for file in "${raw_files[@]}"; do
        ((i++))
        local basename
        basename=$(basename "$file")
        
        log_progress "$i" "$total" "Developing"
        
        # Build pg-develop command
        local -a develop_args=("$file" "--output" "$output_dir" "--quality" "$quality")
        
        if [[ -n "$preset" ]]; then
            develop_args+=("--preset" "$preset")
        fi
        
        # Run development
        if "$PIXELGROOMER_ROOT/bin/pg-develop" "${develop_args[@]}" 2>/dev/null; then
            ((success++))
        else
            ((failed++))
            log_warn "Failed to develop: $basename"
        fi
    done
    
    echo ""
    
    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    echo ""
    log_success "======================================"
    log_success "Album development complete!"
    log_success "======================================"
    log_info "Developed: $success of $total files"
    if [[ $failed -gt 0 ]]; then
        log_warn "Failed:    $failed files"
    fi
    log_info "Preset:    $preset"
    log_info "Output:    $output_dir"
    echo ""
}

# Run main
main "$@"
