#!/usr/bin/env bash
# PixelGroomer - Holiday Import
# Import photos from SD card in trip mode (identity only, one folder per day)
#
# Use after a holiday: no event or location, only author/copyright/credit from
# the card's .import.yaml or .env. One folder per day by EXIF date.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIXELGROOMER_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=../lib/config.sh disable=SC1091
source "$PIXELGROOMER_ROOT/lib/config.sh"
# shellcheck source=../lib/utils.sh disable=SC1091
source "$PIXELGROOMER_ROOT/lib/utils.sh"

show_help() {
    cat << 'EOF'
Holiday Import - SD card import in trip mode (identity only)

Usage: holiday-import.sh [OPTIONS] <source>

Arguments:
  <source>              SD card path (e.g. /Volumes/EOS_DIGITAL)

Options:
  -o, --output DIR      Override archive directory
  --no-delete           Do not delete source files after import (default)
  -n, --dry-run         Show what would be done without changes
  -h, --help            Show this help

Examples:
  holiday-import.sh /Volumes/CARD
  holiday-import.sh /Volumes/CARD --no-delete --dry-run

EOF
}

main() {
    local source=""
    local output_dir=""
    local no_delete=true
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -o|--output)
                output_dir="$2"
                shift 2
                ;;
            --no-delete)
                no_delete=true
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
                show_help
                exit 1
                ;;
            *)
                source="$1"
                shift
                ;;
        esac
    done

    if [[ -z "$source" ]]; then
        log_error "Source path required"
        show_help
        exit 1
    fi

    if [[ ! -d "$source" ]]; then
        log_error "Source not found or not a directory: $source"
        exit 1
    fi

    local args=("$source" --trip)
    [[ "$no_delete" == true ]] && args+=(--no-delete)
    [[ -n "$output_dir" ]] && args+=(--output "$output_dir")
    [[ "$dry_run" == true ]] && args+=(--dry-run)

    "$PIXELGROOMER_ROOT/bin/pg-import" "${args[@]}"
}

main "$@"
