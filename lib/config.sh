#!/usr/bin/env bash
# PixelGroomer - Configuration Loader
# Sources .env file and provides config access functions

set -euo pipefail

# Get the directory where this script is located
PIXELGROOMER_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Load venv helper
source "${PIXELGROOMER_ROOT}/lib/venv.sh"

# Default values (can be overridden by .env)
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

# Load .env file if it exists
load_config() {
    local env_file="${PIXELGROOMER_ROOT}/.env"
    
    if [[ -f "$env_file" ]]; then
        # Source the .env file, but only export valid variable assignments
        while IFS= read -r line || [[ -n "$line" ]]; do
            # Skip comments and empty lines
            [[ "$line" =~ ^[[:space:]]*# ]] && continue
            [[ -z "${line// }" ]] && continue
            
            # Only process valid variable assignments
            if [[ "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; then
                # Evaluate the line to expand variables like $HOME
                eval "export $line" 2>/dev/null || true
            fi
        done < "$env_file"
    fi
}

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

# Initialize config on source
load_config
