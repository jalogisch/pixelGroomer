#!/usr/bin/env bash
# PixelGroomer - Adventure Camp Workflow
# Weekend event: import with event "Adventure Camp" and location "Stadtoldendorf"
# (RAW and JPG in raw/ and jpg/ subfolders with paired names), then develop RAWs
# with RawTherapee and a Kodak-style preset.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIXELGROOMER_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=../lib/config.sh disable=SC1091
source "$PIXELGROOMER_ROOT/lib/config.sh"
# shellcheck source=../lib/utils.sh disable=SC1091
source "$PIXELGROOMER_ROOT/lib/utils.sh"

EVENT_NAME="Adventure Camp"
EVENT_LOCATION="Stadtoldendorf"

# Default preset: project template if present, else from env
get_default_preset() {
    local project_preset="$PIXELGROOMER_ROOT/templates/rawtherapee-kodak-portra.pp3"
    if [[ -f "$project_preset" ]]; then
        echo "$project_preset"
        return
    fi
    if [[ -n "${RAWTHERAPEE_PRESET:-}" && -f "${RAWTHERAPEE_PRESET}" ]]; then
        echo "$RAWTHERAPEE_PRESET"
        return
    fi
    echo ""
}

show_help() {
    cat << EOF
Adventure Camp Workflow - Import + RawTherapee develop (Kodak-style preset)

Usage: adventure-camp-workflow.sh [OPTIONS] <source>
       adventure-camp-workflow.sh [OPTIONS] --skip-import <library-path>

Arguments:
  <source>              SD card path (e.g. /Volumes/EOS_DIGITAL)
  <library-path>        With --skip-import: folder with RAWs (e.g. PhotoLibrary/2026-02-22 or its raw/ subfolder)

Options:
  -o, --output DIR      Output directory for developed JPGs (default: EXPORT_DIR or library/AdventureCamp_developed)
  -p, --preset PATH     RawTherapee PP3 preset path (default: templates/rawtherapee-kodak-portra.pp3 or RAWTHERAPEE_PRESET)
  --skip-import         Skip import; develop only (next arg is library folder)
  --no-delete           Do not delete source files after import
  -n, --dry-run         Show what would be done without changes
  -h, --help            Show this help

Import uses --split-by-type (RAW in raw/, JPG in jpg/ per date; pg-develop finds RAWs in raw/).

Examples:
  adventure-camp-workflow.sh /Volumes/CARD
  adventure-camp-workflow.sh /Volumes/CARD --dry-run
  adventure-camp-workflow.sh --skip-import ~/Pictures/PhotoLibrary/2026-02-22 --output ~/Desktop/Developed

EOF
}

main() {
    local source=""
    local output_dir=""
    local preset_path=""
    local skip_import=false
    local no_delete=true
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -o|--output)
                output_dir="$2"
                shift 2
                ;;
            -p|--preset)
                preset_path="$2"
                shift 2
                ;;
            --skip-import)
                skip_import=true
                shift
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
        log_error "Source path or library path required"
        show_help
        exit 1
    fi

    if [[ ! -d "$source" ]]; then
        log_error "Path not found or not a directory: $source"
        exit 1
    fi

    local develop_dirs=()
    local library_base="${PHOTO_LIBRARY:-$HOME/Pictures/PhotoLibrary}"

    # -------------------------------------------------------------------------
    # Step 1: Import (unless --skip-import)
    # -------------------------------------------------------------------------
    if [[ "$skip_import" == false ]]; then
        log_step "Importing from $source (event: $EVENT_NAME, location: $EVENT_LOCATION)"
        local import_args=("$source" --event "$EVENT_NAME" --location "$EVENT_LOCATION" --split-by-type)
        [[ "$no_delete" == true ]] && import_args+=(--no-delete)
        [[ "$dry_run" == true ]] && import_args+=(--dry-run)
        "$PIXELGROOMER_ROOT/bin/pg-import" "${import_args[@]}"
        # Use two most recent date folders under library (weekend = two days)
        while IFS= read -r d; do
            [[ -n "$d" ]] && develop_dirs+=("$d")
        done < <(find "$library_base" -maxdepth 1 -type d -name "20*" 2>/dev/null | sort -r | head -2)
    else
        develop_dirs+=("$source")
    fi

    if [[ ${#develop_dirs[@]} -eq 0 ]]; then
        if [[ "$dry_run" == true && "$skip_import" == false ]]; then
            log_info "Dry run complete; no folders created so develop step skipped."
            exit 0
        fi
        log_error "No library folders found to develop"
        exit 1
    fi

    # -------------------------------------------------------------------------
    # Step 2: Develop with RawTherapee
    # -------------------------------------------------------------------------
    if [[ -z "$preset_path" ]]; then
        preset_path=$(get_default_preset)
    fi
    if [[ -z "$preset_path" || ! -f "$preset_path" ]]; then
        log_error "RawTherapee preset required. Set RAWTHERAPEE_PRESET in .env or pass --preset /path/to.pp3"
        log_info "You can use a Kodak-style PP3 from RawPedia or create one in RawTherapee."
        exit 1
    fi

    [[ -z "$output_dir" ]] && output_dir="${EXPORT_DIR:-$library_base/AdventureCamp_developed}"

    log_step "Developing RAWs with RawTherapee (preset: $preset_path)"
    local develop_args=(--processor rawtherapee --preset "$preset_path" --output "$output_dir")
    [[ "$dry_run" == true ]] && develop_args+=(--dry-run)
    "$PIXELGROOMER_ROOT/bin/pg-develop" "${develop_dirs[@]}" "${develop_args[@]}"

    log_success "Adventure Camp workflow complete. Output: $output_dir"
}

main "$@"
