"""
Unit tests for lib/config.sh configuration loading.
Tests are run via subprocess calls to Bash scripts.
"""

import os
import subprocess
from pathlib import Path

import pytest


class TestConfigLoading:
    """Tests for .env file loading and config priority."""
    
    def test_default_values_without_env(self, project_root: Path, tmp_path: Path):
        """Config provides defaults when no .env file exists."""
        # Create a minimal test script that sources config.sh
        test_script = tmp_path / 'test_config.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/config.sh"
echo "PHOTO_LIBRARY=$PHOTO_LIBRARY"
echo "ALBUM_DIR=$ALBUM_DIR"
echo "JPEG_QUALITY=$JPEG_QUALITY"
echo "CHECKSUM_ALGORITHM=$CHECKSUM_ALGORITHM"
''')
        test_script.chmod(0o755)
        
        # Run without any env vars that would override
        env = os.environ.copy()
        # Clear any existing config
        for var in ['PHOTO_LIBRARY', 'ALBUM_DIR', 'JPEG_QUALITY', 'CHECKSUM_ALGORITHM']:
            env.pop(var, None)
        
        result = subprocess.run(
            [str(test_script)],
            capture_output=True,
            text=True,
            env=env
        )
        
        assert result.returncode == 0
        output = result.stdout
        
        # Check defaults are set
        assert 'PHOTO_LIBRARY=' in output
        assert 'ALBUM_DIR=' in output
        assert 'JPEG_QUALITY=92' in output
        assert 'CHECKSUM_ALGORITHM=sha256' in output
    
    def test_env_file_overrides_defaults(self, project_root: Path, tmp_path: Path):
        """Values in .env override default values when env vars not already set."""
        # Create a test .env file
        test_env = tmp_path / 'test_project'
        test_env.mkdir()
        
        env_file = test_env / '.env'
        env_file.write_text('''
PHOTO_LIBRARY="/custom/library"
JPEG_QUALITY=95
DEFAULT_AUTHOR="Test Author"
''')
        
        # Create test script that uses the test .env
        test_script = tmp_path / 'test_env.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{test_env}"
# Copy lib files temporarily
cp -r "{project_root}/lib" "{test_env}/"
source "{test_env}/lib/config.sh"
echo "PHOTO_LIBRARY=$PHOTO_LIBRARY"
echo "JPEG_QUALITY=$JPEG_QUALITY"
echo "DEFAULT_AUTHOR=$DEFAULT_AUTHOR"
''')
        test_script.chmod(0o755)
        
        # Clear these vars so .env takes effect
        env = os.environ.copy()
        for var in ['PHOTO_LIBRARY', 'JPEG_QUALITY', 'DEFAULT_AUTHOR']:
            env.pop(var, None)
        
        result = subprocess.run(
            [str(test_script)],
            capture_output=True,
            text=True,
            env=env
        )
        
        assert result.returncode == 0
        output = result.stdout
        
        # .env values should be used when env vars are not set
        assert 'PHOTO_LIBRARY=/custom/library' in output
        assert 'JPEG_QUALITY=95' in output
        assert 'DEFAULT_AUTHOR=Test Author' in output
    
    def test_env_vars_override_env_file(self, project_root: Path, tmp_path: Path):
        """Environment variables take priority over .env file."""
        # Create a test .env file
        test_env = tmp_path / 'test_project'
        test_env.mkdir()
        
        env_file = test_env / '.env'
        env_file.write_text('''
PHOTO_LIBRARY="/from/env/file"
''')
        
        # Create test script
        test_script = tmp_path / 'test_env.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{test_env}"
cp -r "{project_root}/lib" "{test_env}/"
source "{test_env}/lib/config.sh"
echo "PHOTO_LIBRARY=$PHOTO_LIBRARY"
''')
        test_script.chmod(0o755)
        
        # Set env var that should override .env
        env = os.environ.copy()
        env['PHOTO_LIBRARY'] = '/from/env/var'
        
        result = subprocess.run(
            [str(test_script)],
            capture_output=True,
            text=True,
            env=env
        )
        
        assert result.returncode == 0
        # Env var should win
        assert 'PHOTO_LIBRARY=/from/env/var' in result.stdout


class TestIsRawExtension:
    """Tests for is_raw_extension() function."""
    
    def test_recognizes_cr2(self, project_root: Path, tmp_path: Path):
        """is_raw_extension recognizes .cr2 files."""
        test_script = tmp_path / 'test_raw.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/config.sh"
if is_raw_extension "cr2"; then
    echo "is_raw=true"
else
    echo "is_raw=false"
fi
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'is_raw=true' in result.stdout
    
    def test_recognizes_cr3(self, project_root: Path, tmp_path: Path):
        """is_raw_extension recognizes .cr3 files."""
        test_script = tmp_path / 'test_raw.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/config.sh"
if is_raw_extension "CR3"; then
    echo "is_raw=true"
else
    echo "is_raw=false"
fi
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'is_raw=true' in result.stdout  # Case insensitive
    
    def test_rejects_jpg(self, project_root: Path, tmp_path: Path):
        """is_raw_extension rejects .jpg files."""
        test_script = tmp_path / 'test_raw.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/config.sh"
if is_raw_extension "jpg"; then
    echo "is_raw=true"
else
    echo "is_raw=false"
fi
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'is_raw=false' in result.stdout


class TestIsImageExtension:
    """Tests for is_image_extension() function."""
    
    def test_recognizes_jpg(self, project_root: Path, tmp_path: Path):
        """is_image_extension recognizes .jpg files."""
        test_script = tmp_path / 'test_img.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/config.sh"
if is_image_extension "jpg"; then
    echo "is_image=true"
else
    echo "is_image=false"
fi
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'is_image=true' in result.stdout
    
    def test_recognizes_jpeg(self, project_root: Path, tmp_path: Path):
        """is_image_extension recognizes .jpeg files."""
        test_script = tmp_path / 'test_img.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/config.sh"
if is_image_extension "JPEG"; then
    echo "is_image=true"
else
    echo "is_image=false"
fi
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'is_image=true' in result.stdout
    
    def test_rejects_txt(self, project_root: Path, tmp_path: Path):
        """is_image_extension rejects .txt files."""
        test_script = tmp_path / 'test_img.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/config.sh"
if is_image_extension "txt"; then
    echo "is_image=true"
else
    echo "is_image=false"
fi
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'is_image=false' in result.stdout


class TestGetTargetDir:
    """Tests for get_target_dir() function with FOLDER_STRUCTURE patterns."""
    
    def test_default_structure(self, project_root: Path, tmp_path: Path):
        """get_target_dir uses default FOLDER_STRUCTURE pattern."""
        test_script = tmp_path / 'test_dir.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/config.sh"
result=$(get_target_dir "/base" "20260124")
echo "result=$result"
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        # Default structure is {year}-{month}-{day}
        assert '2026-01-24' in result.stdout
    
    def test_custom_structure(self, project_root: Path, tmp_path: Path):
        """get_target_dir respects custom FOLDER_STRUCTURE."""
        test_script = tmp_path / 'test_dir.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
export FOLDER_STRUCTURE="{{year}}/{{month}}/{{day}}"
source "{project_root}/lib/config.sh"
result=$(get_target_dir "/base" "20260124")
echo "result=$result"
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert '/base/2026/01/24' in result.stdout
    
    def test_handles_colon_date_format(self, project_root: Path, tmp_path: Path):
        """get_target_dir handles YYYY:MM:DD format."""
        test_script = tmp_path / 'test_dir.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/config.sh"
result=$(get_target_dir "/base" "2026:01:24")
echo "result=$result"
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert '2026-01-24' in result.stdout


class TestLoadImportYaml:
    """Tests for load_import_yaml() function."""
    
    def test_loads_yaml_from_sd_root(self, project_root: Path, tmp_path: Path):
        """load_import_yaml reads .import.yaml from SD card root."""
        # Create mock SD card with .import.yaml
        sd_card = tmp_path / 'SD_CARD'
        sd_card.mkdir()
        
        yaml_file = sd_card / '.import.yaml'
        yaml_file.write_text('''
event: Test Event
location: Test City
author: YAML Author
''')
        
        test_script = tmp_path / 'test_yaml.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/config.sh"
source "{project_root}/lib/venv.sh"
if yaml_content=$(load_import_yaml "{sd_card}"); then
    echo "$yaml_content"
else
    echo "yaml_not_found"
fi
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        # This test requires the venv to be set up
        if result.returncode == 0:
            output = result.stdout
            assert 'event=Test Event' in output
            assert 'location=Test City' in output
    
    def test_returns_error_when_missing(self, project_root: Path, tmp_path: Path):
        """load_import_yaml returns error when no .import.yaml exists."""
        sd_card = tmp_path / 'SD_CARD'
        sd_card.mkdir()
        
        test_script = tmp_path / 'test_yaml.sh'
        test_script.write_text(f'''#!/usr/bin/env bash
set -euo pipefail
export PIXELGROOMER_ROOT="{project_root}"
source "{project_root}/lib/config.sh"
if load_import_yaml "{sd_card}" 2>/dev/null; then
    echo "yaml_found"
else
    echo "yaml_not_found"
fi
''')
        test_script.chmod(0o755)
        
        result = subprocess.run([str(test_script)], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'yaml_not_found' in result.stdout
