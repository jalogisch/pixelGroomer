#!/usr/bin/env bash
# PixelGroomer Setup Script
# Creates virtual environment and installs dependencies

# shellcheck disable=SC1091  # venv activate script generated at runtime

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

echo ""
echo "╔═══════════════════════════════════════╗"
echo "║       PixelGroomer Setup              ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# Minimum required versions
MIN_PYTHON_MAJOR=3
MIN_PYTHON_MINOR=9
MIN_BASH_MAJOR=3
MIN_BASH_MINOR=2

# Check Bash version
log_info "Checking Bash version..."
BASH_MAJOR="${BASH_VERSINFO[0]}"
BASH_MINOR="${BASH_VERSINFO[1]}"

if [[ "$BASH_MAJOR" -lt "$MIN_BASH_MAJOR" ]] || \
   [[ "$BASH_MAJOR" -eq "$MIN_BASH_MAJOR" && "$BASH_MINOR" -lt "$MIN_BASH_MINOR" ]]; then
    log_error "Bash ${MIN_BASH_MAJOR}.${MIN_BASH_MINOR}+ required, found ${BASH_MAJOR}.${BASH_MINOR}"
    echo ""
    echo "Please upgrade Bash:"
    echo "  macOS:  brew install bash"
    echo "  Ubuntu: sudo apt install bash"
    exit 1
fi
log_success "Bash ${BASH_MAJOR}.${BASH_MINOR} found (>= ${MIN_BASH_MAJOR}.${MIN_BASH_MINOR} required)"

# Check Python 3
log_info "Checking Python version..."
if ! command -v python3 &>/dev/null; then
    log_error "Python 3 not found!"
    echo ""
    echo "Please install Python ${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR}+:"
    echo "  macOS:  brew install python3"
    echo "  Ubuntu: sudo apt install python3 python3-venv"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [[ "$PYTHON_MAJOR" -lt "$MIN_PYTHON_MAJOR" ]] || \
   [[ "$PYTHON_MAJOR" -eq "$MIN_PYTHON_MAJOR" && "$PYTHON_MINOR" -lt "$MIN_PYTHON_MINOR" ]]; then
    log_error "Python ${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR}+ required, found ${PYTHON_VERSION}"
    echo ""
    echo "Please upgrade Python:"
    echo "  macOS:  brew install python@3.12"
    echo "  Ubuntu: sudo apt install python3.12 python3.12-venv"
    exit 1
fi
log_success "Python $PYTHON_VERSION found (>= ${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR} required)"

# Check for venv module
log_info "Checking venv module..."
if ! python3 -c "import venv" &>/dev/null; then
    log_error "Python venv module not found!"
    echo ""
    echo "Please install venv:"
    echo "  Ubuntu: sudo apt install python3-venv"
    exit 1
fi
log_success "venv module available"

# Create virtual environment
log_info "Creating virtual environment..."
if [[ -d "$VENV_DIR" ]]; then
    log_warn "Virtual environment already exists at $VENV_DIR"
    read -p "Recreate? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$VENV_DIR"
        python3 -m venv "$VENV_DIR"
        log_success "Virtual environment recreated"
    else
        log_info "Using existing virtual environment"
    fi
else
    python3 -m venv "$VENV_DIR"
    log_success "Virtual environment created at $VENV_DIR"
fi

# Activate and install dependencies
log_info "Installing Python dependencies..."
source "${VENV_DIR}/bin/activate"

pip install --upgrade pip --quiet
pip install -r "${SCRIPT_DIR}/requirements.txt" --quiet

log_success "Dependencies installed"

# Check external dependencies
echo ""
log_info "Checking external dependencies..."

check_cmd() {
    local cmd="$1"
    # shellcheck disable=SC2034  # pkg reserved for future install hints
    local pkg="${2:-$1}"
    local required="${3:-true}"
    
    if command -v "$cmd" &>/dev/null; then
        log_success "$cmd found"
        return 0
    else
        if [[ "$required" == "true" ]]; then
            log_error "$cmd not found (required)"
        else
            log_warn "$cmd not found (optional)"
        fi
        return 1
    fi
}

MISSING_REQUIRED=false
MISSING_OPTIONAL=false

check_cmd "exiftool" "exiftool" "true" || MISSING_REQUIRED=true
check_cmd "darktable-cli" "darktable" "false" || MISSING_OPTIONAL=true
check_cmd "convert" "imagemagick" "false" || MISSING_OPTIONAL=true

# Create .env if not exists
echo ""
if [[ ! -f "${SCRIPT_DIR}/.env" ]]; then
    log_info "Creating .env from template..."
    cp "${SCRIPT_DIR}/.env.example" "${SCRIPT_DIR}/.env"
    log_success ".env created - please edit it with your settings"
else
    log_info ".env already exists"
fi

# Make scripts executable
log_info "Making scripts executable..."
chmod +x "${SCRIPT_DIR}"/bin/pg-*
chmod +x "${SCRIPT_DIR}"/setup.sh
log_success "Scripts are executable"

# Summary
echo ""
echo "═══════════════════════════════════════"
echo ""

if [[ "$MISSING_REQUIRED" == "true" ]]; then
    log_error "Setup incomplete - missing required dependencies!"
    echo ""
    echo "Install missing dependencies:"
    echo "  macOS:  brew install exiftool"
    echo "  Ubuntu: sudo apt install libimage-exiftool-perl"
    exit 1
fi

log_success "Setup complete!"
echo ""

if [[ "$MISSING_OPTIONAL" == "true" ]]; then
    log_warn "Optional: Install darktable and/or imagemagick for RAW development"
    echo "  macOS:  brew install darktable imagemagick"
    echo "  Ubuntu: sudo apt install darktable imagemagick"
    echo ""
fi

echo "Next steps:"
echo "  1. Edit .env with your settings"
echo "  2. Add bin/ to your PATH or use full paths:"
echo ""
echo "     export PATH=\"\$PATH:${SCRIPT_DIR}/bin\""
echo ""
echo "  3. Start importing:"
echo ""
echo "     pg-import /Volumes/SD --event \"Test\""
echo ""
