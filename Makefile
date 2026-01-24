# PixelGroomer Makefile
# Installation and development helpers

PREFIX ?= /usr/local
BINDIR = $(PREFIX)/bin
VENV = .venv

SCRIPTS = pg-import pg-rename pg-exif pg-album pg-develop pg-verify pg-test-processors

.PHONY: all setup install uninstall check deps clean lint help

all: help

help:
	@echo "PixelGroomer - Photo Workflow Automation"
	@echo ""
	@echo "Usage:"
	@echo "  make setup       Setup virtual environment and dependencies"
	@echo "  make check       Verify dependencies are installed"
	@echo "  make lint        Run ShellCheck validation"
	@echo "  make deps        Install external dependencies (macOS only)"
	@echo "  make install     Install scripts to $(BINDIR)"
	@echo "  make uninstall   Remove scripts from $(BINDIR)"
	@echo "  make clean       Remove virtual environment"
	@echo ""
	@echo "Quick start:"
	@echo "  1. make deps     # Install exiftool, darktable, etc."
	@echo "  2. make setup    # Create venv and configure"

setup:
	@./setup.sh

install:
	@echo "Installing PixelGroomer to $(BINDIR)..."
	@mkdir -p $(BINDIR)
	@for script in $(SCRIPTS); do \
		cp bin/$$script $(BINDIR)/$$script; \
		chmod +x $(BINDIR)/$$script; \
		echo "  Installed $$script"; \
	done
	@echo ""
	@echo "Note: Scripts require the venv at $(CURDIR)/.venv"
	@echo "Make sure to run 'make setup' first."

uninstall:
	@echo "Removing PixelGroomer from $(BINDIR)..."
	@for script in $(SCRIPTS); do \
		rm -f $(BINDIR)/$$script; \
		echo "  Removed $$script"; \
	done

check:
	@echo "Checking dependencies..."
	@echo ""
	@echo "External tools:"
	@command -v exiftool >/dev/null 2>&1 && echo "  ✓ exiftool" || echo "  ✗ exiftool (required)"
	@command -v python3 >/dev/null 2>&1 && echo "  ✓ python3" || echo "  ✗ python3 (required)"
	@command -v darktable-cli >/dev/null 2>&1 && echo "  ✓ darktable-cli" || echo "  ○ darktable-cli (optional)"
	@command -v convert >/dev/null 2>&1 && echo "  ✓ imagemagick" || echo "  ○ imagemagick (optional)"
	@echo ""
	@echo "Virtual environment:"
	@test -d $(VENV) && echo "  ✓ .venv exists" || echo "  ✗ .venv missing (run: make setup)"
	@test -f $(VENV)/bin/python && echo "  ✓ Python in venv" || echo "  ✗ Python not in venv"
	@$(VENV)/bin/python -c "import yaml" 2>/dev/null && echo "  ✓ PyYAML installed" || echo "  ✗ PyYAML missing"

deps:
	@echo "Installing external dependencies (macOS)..."
	@command -v brew >/dev/null 2>&1 || (echo "Homebrew not found. Please install it first." && exit 1)
	brew install exiftool python3 darktable imagemagick
	@echo ""
	@echo "External dependencies installed. Now run: make setup"

clean:
	@echo "Removing virtual environment..."
	rm -rf $(VENV)
	@echo "Done. Run 'make setup' to recreate."

lint:
	@echo "Running ShellCheck..."
	shellcheck bin/pg-* lib/*.sh setup.sh
	@echo "All scripts passed ShellCheck validation."
