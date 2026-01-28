#!/usr/bin/env bash
# PixelGroomer - Utility Functions
# Logging, colors, prompts, and common helpers

set -euo pipefail

# =============================================================================
# Colors and Formatting
# =============================================================================

# Check if terminal supports colors
if [[ -t 1 ]] && command -v tput &>/dev/null && [[ $(tput colors 2>/dev/null || echo 0) -ge 8 ]]; then
    COLOR_RESET="\033[0m"
    COLOR_RED="\033[0;31m"
    COLOR_GREEN="\033[0;32m"
    COLOR_YELLOW="\033[0;33m"
    COLOR_BLUE="\033[0;34m"
    COLOR_MAGENTA="\033[0;35m"
    COLOR_CYAN="\033[0;36m"
    COLOR_BOLD="\033[1m"
    COLOR_DIM="\033[2m"
else
    COLOR_RESET=""
    COLOR_RED=""
    COLOR_GREEN=""
    COLOR_YELLOW=""
    COLOR_BLUE=""
    # shellcheck disable=SC2034  # COLOR_MAGENTA reserved for future use
    COLOR_MAGENTA=""
    COLOR_CYAN=""
    COLOR_BOLD=""
    COLOR_DIM=""
fi

# =============================================================================
# Logging Functions
# =============================================================================

log_info() {
    echo -e "${COLOR_BLUE}[INFO]${COLOR_RESET} $*" >&2
}

log_success() {
    echo -e "${COLOR_GREEN}[OK]${COLOR_RESET} $*" >&2
}

log_warn() {
    echo -e "${COLOR_YELLOW}[WARN]${COLOR_RESET} $*" >&2
}

log_error() {
    echo -e "${COLOR_RED}[ERROR]${COLOR_RESET} $*" >&2
}

log_debug() {
    if [[ "${DEBUG:-false}" == "true" ]]; then
        echo -e "${COLOR_DIM}[DEBUG] $*${COLOR_RESET}" >&2
    fi
}

log_step() {
    echo -e "${COLOR_CYAN}==>${COLOR_RESET} ${COLOR_BOLD}$*${COLOR_RESET}" >&2
}

# Progress indicator for long operations
log_progress() {
    local current="$1"
    local total="$2"
    local message="${3:-Processing}"
    
    local percent=$((current * 100 / total))
    local filled=$((percent / 2))
    local empty=$((50 - filled))
    
    # shellcheck disable=SC2046  # Word splitting intended for seq output
    printf "\r${COLOR_CYAN}[%-50s]${COLOR_RESET} %3d%% %s" \
        "$(printf '#%.0s' $(seq 1 $filled 2>/dev/null || true))$(printf ' %.0s' $(seq 1 $empty 2>/dev/null || true))" \
        "$percent" "$message" >&2
    
    if [[ $current -eq $total ]]; then
        echo "" >&2
    fi
}

# =============================================================================
# User Prompts
# =============================================================================

# Ask for yes/no confirmation
confirm() {
    local message="${1:-Continue?}"
    local default="${2:-n}"
    
    # Non-interactive mode: return based on default
    if [[ "${PG_NON_INTERACTIVE:-}" == "1" ]]; then
        if [[ "$default" == "y" ]]; then
            return 0
        else
            return 1
        fi
    fi
    
    local prompt
    if [[ "$default" == "y" ]]; then
        prompt="[Y/n]"
    else
        prompt="[y/N]"
    fi
    
    while true; do
        echo -en "${COLOR_YELLOW}$message${COLOR_RESET} $prompt "
        read -r response
        response="${response:-$default}"
        
        case "$(echo "$response" | tr '[:upper:]' '[:lower:]')" in
            y|yes) return 0 ;;
            n|no) return 1 ;;
            *) echo "Please answer yes or no." ;;
        esac
    done
}

# Prompt for input with optional default
prompt_input() {
    local message="$1"
    local default="${2:-}"
    local var_name="${3:-REPLY}"
    
    # Non-interactive mode: use default value
    if [[ "${PG_NON_INTERACTIVE:-}" == "1" ]]; then
        printf -v "$var_name" '%s' "$default"
        echo "$default"
        return 0
    fi
    
    local prompt_text="$message"
    if [[ -n "$default" ]]; then
        prompt_text="$message [$default]"
    fi
    
    echo -en "${COLOR_CYAN}$prompt_text:${COLOR_RESET} "
    read -r input
    
    # Use default if input is empty
    if [[ -z "$input" && -n "$default" ]]; then
        input="$default"
    fi
    
    # Set the variable
    printf -v "$var_name" '%s' "$input"
    echo "$input"
}

# Select from a list of options
prompt_select() {
    local message="$1"
    shift
    local options=("$@")
    
    echo -e "${COLOR_CYAN}$message${COLOR_RESET}"
    
    local i=1
    for opt in "${options[@]}"; do
        echo "  $i) $opt"
        ((i++))
    done
    
    while true; do
        echo -en "${COLOR_CYAN}Selection [1-${#options[@]}]:${COLOR_RESET} "
        read -r selection
        
        if [[ "$selection" =~ ^[0-9]+$ ]] && \
           [[ "$selection" -ge 1 ]] && \
           [[ "$selection" -le "${#options[@]}" ]]; then
            echo "${options[$((selection-1))]}"
            return 0
        else
            log_warn "Invalid selection. Please enter a number between 1 and ${#options[@]}"
        fi
    done
}

# =============================================================================
# File Operations
# =============================================================================

# Get file extension (lowercase)
get_extension() {
    local file="$1"
    local ext="${file##*.}"
    echo "$ext" | tr '[:upper:]' '[:lower:]'
}

# Get filename without extension
get_basename() {
    local file="$1"
    local name="${file##*/}"
    echo "${name%.*}"
}

# Generate checksum for a file
generate_checksum() {
    local file="$1"
    local algorithm="${2:-sha256}"
    
    case "$algorithm" in
        sha256)
            if command -v sha256sum &>/dev/null; then
                sha256sum "$file" | cut -d' ' -f1
            elif command -v shasum &>/dev/null; then
                shasum -a 256 "$file" | cut -d' ' -f1
            else
                log_error "No sha256 tool found"
                return 1
            fi
            ;;
        md5)
            if command -v md5sum &>/dev/null; then
                md5sum "$file" | cut -d' ' -f1
            elif command -v md5 &>/dev/null; then
                md5 -q "$file"
            else
                log_error "No md5 tool found"
                return 1
            fi
            ;;
        *)
            log_error "Unknown checksum algorithm: $algorithm"
            return 1
            ;;
    esac
}

# Verify checksum
verify_checksum() {
    local file="$1"
    local expected="$2"
    local algorithm="${3:-sha256}"
    
    local actual
    actual=$(generate_checksum "$file" "$algorithm")
    
    [[ "$actual" == "$expected" ]]
}

# Safe copy with verification
safe_copy() {
    local source="$1"
    local dest="$2"
    local verify="${3:-true}"
    
    # Copy the file
    cp "$source" "$dest"
    
    if [[ "$verify" == "true" ]]; then
        local src_sum dest_sum
        src_sum=$(generate_checksum "$source")
        dest_sum=$(generate_checksum "$dest")
        
        if [[ "$src_sum" != "$dest_sum" ]]; then
            log_error "Checksum mismatch for: $dest"
            rm -f "$dest"
            return 1
        fi
    fi
    
    return 0
}

# Find files by extension in a directory
find_files_by_extension() {
    local dir="$1"
    local extensions="$2"  # comma-separated
    
    local find_args=()
    local first=true
    
    IFS=',' read -ra exts <<< "$extensions"
    for ext in "${exts[@]}"; do
        ext="${ext// /}"  # trim whitespace
        if [[ "$first" == "true" ]]; then
            find_args+=(-iname "*.$ext")
            first=false
        else
            find_args+=(-o -iname "*.$ext")
        fi
    done
    
    find "$dir" -type f \( "${find_args[@]}" \) 2>/dev/null | sort
}

# =============================================================================
# Date/Time Helpers
# =============================================================================

# Parse EXIF date to components
# Input: "YYYY:MM:DD HH:MM:SS" or similar
# Output: YYYYMMDD
parse_exif_date() {
    local exif_date="$1"
    
    # Try to extract date components
    if [[ "$exif_date" =~ ^([0-9]{4})[:-]([0-9]{2})[:-]([0-9]{2}) ]]; then
        echo "${BASH_REMATCH[1]}${BASH_REMATCH[2]}${BASH_REMATCH[3]}"
    else
        # Return current date as fallback
        date +%Y%m%d
    fi
}

# Parse EXIF time to components
# Input: "YYYY:MM:DD HH:MM:SS" or similar
# Output: HHMMSS
parse_exif_time() {
    local exif_datetime="$1"
    
    if [[ "$exif_datetime" =~ ([0-9]{2})[:-]([0-9]{2})[:-]([0-9]{2})[[:space:]]*$ ]]; then
        echo "${BASH_REMATCH[1]}${BASH_REMATCH[2]}${BASH_REMATCH[3]}"
    else
        echo "000000"
    fi
}

# =============================================================================
# Validation
# =============================================================================

# Check if a command exists
require_command() {
    local cmd="$1"
    local package="${2:-$cmd}"
    
    if ! command -v "$cmd" &>/dev/null; then
        log_error "Required command not found: $cmd"
        log_error "Please install it: brew install $package (macOS) or apt install $package (Ubuntu)"
        return 1
    fi
}

# Validate that a path exists
require_path() {
    local path="$1"
    local type="${2:-any}"  # any, file, dir
    
    if [[ ! -e "$path" ]]; then
        log_error "Path does not exist: $path"
        return 1
    fi
    
    case "$type" in
        file)
            if [[ ! -f "$path" ]]; then
                log_error "Not a file: $path"
                return 1
            fi
            ;;
        dir)
            if [[ ! -d "$path" ]]; then
                log_error "Not a directory: $path"
                return 1
            fi
            ;;
    esac
    
    return 0
}

# =============================================================================
# String Helpers
# =============================================================================

# Sanitize a string for use in filenames
sanitize_filename() {
    local input="$1"
    
    # Replace problematic characters with underscore
    # Keep: alphanumeric, dash, underscore, period
    echo "$input" | sed -E 's/[^a-zA-Z0-9._-]+/_/g' | sed -E 's/_+/_/g' | sed -E 's/^_|_$//g'
}

# Pad a number with leading zeros
pad_number() {
    local number="$1"
    local width="${2:-3}"
    
    printf "%0${width}d" "$number"
}

# =============================================================================
# Associative Array Simulation (Bash 3.2 compatible)
# Uses temp files to simulate key-value storage
# =============================================================================

# Initialize a "map" (creates temp file, echoes path)
map_init() {
    mktemp
}

# Set value in map: map_set <mapfile> <key> <value>
map_set() {
    local mapfile="$1"
    local key="$2"
    local value="$3"
    
    # Remove existing key if present
    if grep -q "^${key}=" "$mapfile" 2>/dev/null; then
        local tmpfile
        tmpfile=$(mktemp)
        grep -v "^${key}=" "$mapfile" > "$tmpfile"
        mv "$tmpfile" "$mapfile"
    fi
    
    # Add new value
    echo "${key}=${value}" >> "$mapfile"
}

# Get value from map: map_get <mapfile> <key> [default]
map_get() {
    local mapfile="$1"
    local key="$2"
    local default="${3:-}"
    
    local value
    value=$(grep "^${key}=" "$mapfile" 2>/dev/null | head -1 | cut -d= -f2-)
    
    if [[ -n "$value" ]]; then
        echo "$value"
    else
        echo "$default"
    fi
}

# Check if key exists: map_has <mapfile> <key>
map_has() {
    local mapfile="$1"
    local key="$2"
    
    grep -q "^${key}=" "$mapfile" 2>/dev/null
}

# Increment numeric value: map_incr <mapfile> <key>
# Returns new value
map_incr() {
    local mapfile="$1"
    local key="$2"
    
    local current
    current=$(map_get "$mapfile" "$key" "0")
    local new=$((current + 1))
    map_set "$mapfile" "$key" "$new"
    echo "$new"
}

# Cleanup map file
map_cleanup() {
    local mapfile="$1"
    rm -f "$mapfile"
}
