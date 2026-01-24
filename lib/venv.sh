#!/usr/bin/env bash
# PixelGroomer - Virtual Environment Helper
# Ensures Python runs in the project's venv

# Get the project root (parent of lib/)
PIXELGROOMER_ROOT="${PIXELGROOMER_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
PIXELGROOMER_VENV="${PIXELGROOMER_ROOT}/.venv"

# Check if venv exists and is valid
check_venv() {
    if [[ ! -d "$PIXELGROOMER_VENV" ]]; then
        return 1
    fi
    
    if [[ ! -f "${PIXELGROOMER_VENV}/bin/python" ]]; then
        return 1
    fi
    
    if [[ ! -f "${PIXELGROOMER_VENV}/bin/activate" ]]; then
        return 1
    fi
    
    return 0
}

# Get the Python executable from venv
get_python() {
    echo "${PIXELGROOMER_VENV}/bin/python"
}

# Ensure venv exists, exit with error if not
require_venv() {
    if ! check_venv; then
        echo -e "\033[0;31m[ERROR]\033[0m Python virtual environment not found!" >&2
        echo "" >&2
        echo "Please run the setup script first:" >&2
        echo "" >&2
        echo "    ${PIXELGROOMER_ROOT}/setup.sh" >&2
        echo "" >&2
        exit 1
    fi
}

# Run Python command in venv
# Usage: run_python "import sys; print(sys.version)"
# Usage: run_python_script script.py arg1 arg2
run_python() {
    require_venv
    "${PIXELGROOMER_VENV}/bin/python" -c "$1"
}

run_python_script() {
    require_venv
    "${PIXELGROOMER_VENV}/bin/python" "$@"
}

# Run Python with inline script that needs project lib
# Automatically adds lib/ to Python path
run_python_with_lib() {
    require_venv
    local script="$1"
    
    "${PIXELGROOMER_VENV}/bin/python" -c "
import sys
sys.path.insert(0, '${PIXELGROOMER_ROOT}/lib')
$script
"
}
