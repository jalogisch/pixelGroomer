#!/usr/bin/env bash
# PixelGroomer - Configuration Loader
# Sources .env file and provides config access functions
#
# Priority (highest to lowest):
#   1. Environment variables passed to script
#   2. .env file values
#   3. Default values in this file

set -euo pipefail

# Get the directory where this script is located
PIXELGROOMER_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Load venv helper
# shellcheck disable=SC1090  # Dynamic path from PIXELGROOMER_ROOT
source "${PIXELGROOMER_ROOT}/lib/venv.sh"

# Track which variables were set by the caller (before we do anything)
# This allows us to preserve caller's env vars while still letting .env override defaults
_pg_caller_vars=""
[[ -n "${PHOTO_LIBRARY:-}" ]] && _pg_caller_vars="$_pg_caller_vars PHOTO_LIBRARY"
[[ -n "${ALBUM_DIR:-}" ]] && _pg_caller_vars="$_pg_caller_vars ALBUM_DIR"
[[ -n "${EXPORT_DIR:-}" ]] && _pg_caller_vars="$_pg_caller_vars EXPORT_DIR"
[[ -n "${GENERATE_CHECKSUMS:-}" ]] && _pg_caller_vars="$_pg_caller_vars GENERATE_CHECKSUMS"
[[ -n "${FOLDER_STRUCTURE:-}" ]] && _pg_caller_vars="$_pg_caller_vars FOLDER_STRUCTURE"
[[ -n "${NAMING_PATTERN:-}" ]] && _pg_caller_vars="$_pg_caller_vars NAMING_PATTERN"

# Load .env file if it exists
# Only overrides variables NOT set by calling environment
load_config() {
    local env_file="${PIXELGROOMER_ROOT}/.env"
    
    if [[ -f "$env_file" ]]; then
        # Source the .env file, but only export valid variable assignments
        # that weren't set by the caller
        while IFS= read -r line || [[ -n "$line" ]]; do
            # Skip comments and empty lines
            [[ "$line" =~ ^[[:space:]]*# ]] && continue
            [[ -z "${line// }" ]] && continue
            
            # Only process valid variable assignments
            if [[ "$line" =~ ^([A-Za-z_][A-Za-z0-9_]*)= ]]; then
                local var_name="${BASH_REMATCH[1]}"
                # Only set if not set by caller
                if [[ "$_pg_caller_vars" != *" $var_name"* ]]; then
                    # Evaluate the line to expand variables like $HOME
                    eval "export $line" 2>/dev/null || true
                fi
            fi
        done < "$env_file"
    fi
}

# Load .env first (so it can override defaults but not caller's vars)
load_config

# Default values (applied after .env, only if still not set)
: "${PHOTO_LIBRARY:=$HOME/Pictures/PhotoLibrary}"
: "${ALBUM_DIR:=$HOME/Pictures/Albums}"
: "${EXPORT_DIR:=$HOME/Pictures/Export}"
: "${DEFAULT_AUTHOR:=}"
: "${DEFAULT_COPYRIGHT:=}"
[[ -z "${NAMING_PATTERN:-}" ]] && NAMING_PATTERN='{date}_{event}_{seq:03d}'
: "${RAW_PROCESSOR:=darktable}"
: "${JPEG_QUALITY:=92}"
: "${DARKTABLE_STYLE:=}"
: "${RAW_EXTENSIONS:=cr2,cr3,nef,arw,raf,dng,orf,rw2}"
: "${IMAGE_EXTENSIONS:=jpg,jpeg,png,tiff,tif,heic,heif}"
: "${CONFIRM_DELETE:=true}"
: "${GENERATE_CHECKSUMS:=true}"
: "${CHECKSUM_ALGORITHM:=sha256}"
[[ -z "${FOLDER_STRUCTURE:-}" ]] && FOLDER_STRUCTURE='{year}-{month}-{day}'
: "${PROMPT_ARCHIVE_DIR:=false}"

# Load .import.yaml from a directory (typically SD card)
# Returns key=value pairs on stdout
load_import_yaml() {
    local source_dir="$1"
    local yaml_file=""
    
    # Check common locations for .import.yaml
    for location in "$source_dir/.import.yaml" "$source_dir/DCIM/.import.yaml"; do
        if [[ -f "$location" ]]; then
            yaml_file="$location"
            break
        fi
    done
    
    if [[ -z "$yaml_file" ]]; then
        return 1
    fi
    
    # Parse YAML using Python (more reliable than bash parsing)
    run_python "
import yaml
import sys

try:
    with open('$yaml_file', 'r') as f:
        data = yaml.safe_load(f)
    if data:
        for key, value in data.items():
            if isinstance(value, list):
                print(f'{key}={chr(44).join(str(v) for v in value)}')
            else:
                print(f'{key}={value}')
except Exception as e:
    sys.exit(1)
" 2>/dev/null
}

# Get a config value with optional default
config_get() {
    local key="$1"
    local default="${2:-}"
    
    # Use indirect reference to get the variable value
    local value="${!key:-$default}"
    echo "$value"
}

# Check if a file extension is a RAW format
is_raw_extension() {
    local ext
    ext=$(echo "$1" | tr '[:upper:]' '[:lower:]')
    local raw_exts
    raw_exts=$(echo "$RAW_EXTENSIONS" | tr '[:upper:]' '[:lower:]')
    
    [[ ",$raw_exts," == *",$ext,"* ]]
}

# Check if a file extension is an image format
is_image_extension() {
    local ext
    ext=$(echo "$1" | tr '[:upper:]' '[:lower:]')
    local img_exts
    img_exts=$(echo "$IMAGE_EXTENSIONS" | tr '[:upper:]' '[:lower:]')
    
    [[ ",$img_exts," == *",$ext,"* ]]
}

# Check if a file is a supported format (RAW or image)
is_supported_file() {
    local file="$1"
    local ext="${file##*.}"
    
    is_raw_extension "$ext" || is_image_extension "$ext"
}

# Ensure required directories exist
ensure_directories() {
    mkdir -p "$PHOTO_LIBRARY"
    mkdir -p "$ALBUM_DIR"
    mkdir -p "$EXPORT_DIR"
}

# Get the target directory for a given date
# Supports configurable folder structure via FOLDER_STRUCTURE variable
get_target_dir() {
    local base_dir="$1"
    local date="$2"  # Expected format: YYYY:MM:DD or YYYY-MM-DD or YYYYMMDD
    
    # Normalize date format
    local year month day
    if [[ "$date" =~ ^([0-9]{4})[:-]?([0-9]{2})[:-]?([0-9]{2}) ]]; then
        year="${BASH_REMATCH[1]}"
        month="${BASH_REMATCH[2]}"
        day="${BASH_REMATCH[3]}"
    else
        # Fallback to current date
        year=$(date +%Y)
        month=$(date +%m)
        day=$(date +%d)
    fi
    
    # Apply folder structure pattern
    local structure="$FOLDER_STRUCTURE"
    structure="${structure//\{year\}/$year}"
    structure="${structure//\{month\}/$month}"
    structure="${structure//\{day\}/$day}"
    
    echo "${base_dir}/${structure}"
}

# Note: load_config is called early in this file, before defaults are set
# This allows .env to override defaults while caller's env vars take priority
