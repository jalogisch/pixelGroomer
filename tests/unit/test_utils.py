"""
Unit tests for lib/utils.sh utility functions.
Tests are run via subprocess calls to Bash scripts.
"""

import os
import subprocess
from pathlib import Path

import pytest


class TestSanitizeFilename:
    """Tests for sanitize_filename() function."""
    
    def test_removes_spaces(self, project_root: Path, tmp_path: Path):
        """sanitize_filename replaces spaces with underscores."""
        test_script = tmp_path / 'test_sanitize.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/utils.sh"
result=$(sanitize_filename "My Photo Name")
echo "result=$result"
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'result=My_Photo_Name' in result.stdout
    
    def test_removes_special_characters(self, project_root: Path, tmp_path: Path):
        """sanitize_filename removes special characters."""
        test_script = tmp_path / 'test_sanitize.sh'
        # Use raw string to avoid escape sequence issues
        script_content = '''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{root}"
source "{root}/lib/utils.sh"
result=$(sanitize_filename "Photo@#$%^&*()")
echo "result=$result"
'''.format(root=project_root)
        test_script.write_text(script_content)
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        # Should only contain alphanumeric, dash, underscore, period
        output = result.stdout.strip()
        assert 'Photo' in output
        assert '@' not in output
        assert '#' not in output
    
    def test_preserves_valid_characters(self, project_root: Path, tmp_path: Path):
        """sanitize_filename preserves valid characters."""
        test_script = tmp_path / 'test_sanitize.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/utils.sh"
result=$(sanitize_filename "Valid-Name_123.test")
echo "result=$result"
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'result=Valid-Name_123.test' in result.stdout
    
    def test_collapses_multiple_underscores(self, project_root: Path, tmp_path: Path):
        """sanitize_filename collapses multiple underscores."""
        test_script = tmp_path / 'test_sanitize.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/utils.sh"
result=$(sanitize_filename "Photo   Multiple   Spaces")
echo "result=$result"
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        output = result.stdout
        # Should not have multiple consecutive underscores
        assert '___' not in output


class TestPadNumber:
    """Tests for pad_number() function."""
    
    def test_pads_single_digit(self, project_root: Path, tmp_path: Path):
        """pad_number pads single digit to specified width."""
        test_script = tmp_path / 'test_pad.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/utils.sh"
result=$(pad_number 5 3)
echo "result=$result"
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'result=005' in result.stdout
    
    def test_pads_double_digit(self, project_root: Path, tmp_path: Path):
        """pad_number pads double digit correctly."""
        test_script = tmp_path / 'test_pad.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/utils.sh"
result=$(pad_number 42 4)
echo "result=$result"
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'result=0042' in result.stdout
    
    def test_no_padding_when_larger(self, project_root: Path, tmp_path: Path):
        """pad_number doesn't truncate larger numbers."""
        test_script = tmp_path / 'test_pad.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/utils.sh"
result=$(pad_number 12345 3)
echo "result=$result"
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'result=12345' in result.stdout


class TestGetExtension:
    """Tests for get_extension() function."""
    
    def test_extracts_extension(self, project_root: Path, tmp_path: Path):
        """get_extension returns lowercase extension."""
        test_script = tmp_path / 'test_ext.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/utils.sh"
result=$(get_extension "photo.JPG")
echo "result=$result"
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'result=jpg' in result.stdout
    
    def test_handles_multiple_dots(self, project_root: Path, tmp_path: Path):
        """get_extension handles files with multiple dots."""
        test_script = tmp_path / 'test_ext.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/utils.sh"
result=$(get_extension "photo.2026.01.24.CR3")
echo "result=$result"
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'result=cr3' in result.stdout


class TestGetBasename:
    """Tests for get_basename() function."""
    
    def test_extracts_basename(self, project_root: Path, tmp_path: Path):
        """get_basename returns filename without extension."""
        test_script = tmp_path / 'test_base.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/utils.sh"
result=$(get_basename "photo.jpg")
echo "result=$result"
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'result=photo' in result.stdout
    
    def test_handles_path(self, project_root: Path, tmp_path: Path):
        """get_basename handles full path."""
        test_script = tmp_path / 'test_base.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/utils.sh"
result=$(get_basename "/path/to/photo.jpg")
echo "result=$result"
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'result=photo' in result.stdout


class TestGenerateChecksum:
    """Tests for generate_checksum() function."""
    
    def test_sha256_checksum(self, project_root: Path, tmp_path: Path):
        """generate_checksum produces sha256 hash."""
        test_file = tmp_path / 'test.txt'
        test_file.write_text('test content')
        
        test_script = tmp_path / 'test_checksum.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/utils.sh"
result=$(generate_checksum "{test_file}" "sha256")
echo "result=$result"
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        # SHA256 hash is 64 hex characters
        output = result.stdout.strip()
        assert 'result=' in output
        hash_value = output.split('result=')[1]
        assert len(hash_value) == 64
    
    def test_md5_checksum(self, project_root: Path, tmp_path: Path):
        """generate_checksum produces md5 hash."""
        test_file = tmp_path / 'test.txt'
        test_file.write_text('test content')
        
        test_script = tmp_path / 'test_checksum.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/utils.sh"
result=$(generate_checksum "{test_file}" "md5")
echo "result=$result"
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        # MD5 hash is 32 hex characters
        output = result.stdout.strip()
        assert 'result=' in output
        hash_value = output.split('result=')[1]
        assert len(hash_value) == 32


class TestMapFunctions:
    """Tests for Bash 3.2 compatible map_* functions."""
    
    def test_map_set_and_get(self, project_root: Path, tmp_path: Path):
        """map_set and map_get work together."""
        test_script = tmp_path / 'test_map.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/utils.sh"

mymap=$(map_init)
trap "map_cleanup '$mymap'" EXIT

map_set "$mymap" "key1" "value1"
map_set "$mymap" "key2" "value2"

result1=$(map_get "$mymap" "key1")
result2=$(map_get "$mymap" "key2")

echo "result1=$result1"
echo "result2=$result2"
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'result1=value1' in result.stdout
        assert 'result2=value2' in result.stdout
    
    def test_map_has(self, project_root: Path, tmp_path: Path):
        """map_has correctly detects key presence."""
        test_script = tmp_path / 'test_map.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/utils.sh"

mymap=$(map_init)
trap "map_cleanup '$mymap'" EXIT

map_set "$mymap" "exists" "value"

if map_has "$mymap" "exists"; then
    echo "has_exists=true"
else
    echo "has_exists=false"
fi

if map_has "$mymap" "missing"; then
    echo "has_missing=true"
else
    echo "has_missing=false"
fi
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'has_exists=true' in result.stdout
        assert 'has_missing=false' in result.stdout
    
    def test_map_incr(self, project_root: Path, tmp_path: Path):
        """map_incr increments numeric values."""
        test_script = tmp_path / 'test_map.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/utils.sh"

mymap=$(map_init)
trap "map_cleanup '$mymap'" EXIT

# First incr should return 1 (starts from 0)
result1=$(map_incr "$mymap" "counter")
result2=$(map_incr "$mymap" "counter")
result3=$(map_incr "$mymap" "counter")

echo "result1=$result1"
echo "result2=$result2"
echo "result3=$result3"
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'result1=1' in result.stdout
        assert 'result2=2' in result.stdout
        assert 'result3=3' in result.stdout


class TestConfirmNonInteractive:
    """Tests for confirm() in non-interactive mode."""
    
    def test_confirm_returns_default_yes(self, project_root: Path, tmp_path: Path):
        """confirm() returns true when default is 'y' in non-interactive mode."""
        test_script = tmp_path / 'test_confirm.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
export PG_NON_INTERACTIVE=1
source "{project_root}/lib/utils.sh"

if confirm "Test?" "y"; then
    echo "confirmed=true"
else
    echo "confirmed=false"
fi
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'confirmed=true' in result.stdout
    
    def test_confirm_returns_default_no(self, project_root: Path, tmp_path: Path):
        """confirm() returns false when default is 'n' in non-interactive mode."""
        test_script = tmp_path / 'test_confirm.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
export PG_NON_INTERACTIVE=1
source "{project_root}/lib/utils.sh"

if confirm "Test?" "n"; then
    echo "confirmed=true"
else
    echo "confirmed=false"
fi
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'confirmed=false' in result.stdout


class TestPromptInputNonInteractive:
    """Tests for prompt_input() in non-interactive mode."""
    
    def test_prompt_input_returns_default(self, project_root: Path, tmp_path: Path):
        """prompt_input() returns default value in non-interactive mode."""
        test_script = tmp_path / 'test_prompt.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
export PG_NON_INTERACTIVE=1
source "{project_root}/lib/utils.sh"

result=$(prompt_input "Enter value" "default_value")
echo "result=$result"
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'result=default_value' in result.stdout
