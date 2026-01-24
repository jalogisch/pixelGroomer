#!/usr/bin/env python3
"""
PixelGroomer - EXIF Utilities
Wrapper around exiftool for reading and writing metadata
"""

import subprocess
import json
import os
import sys
from typing import Optional, Dict, List, Any, Union
from datetime import datetime
from pathlib import Path


class ExifTool:
    """Wrapper for exiftool command-line utility"""
    
    # Mapping of our field names to exiftool tags
    FIELD_MAP = {
        'author': ['-Artist', '-XMP:Creator', '-IPTC:By-line'],
        'copyright': ['-Copyright', '-XMP:Rights', '-IPTC:CopyrightNotice'],
        'event': ['-XMP:Event', '-IPTC:Caption-Abstract'],
        'location': ['-XMP:Location', '-IPTC:City'],
        'description': ['-ImageDescription', '-XMP:Description', '-IPTC:Caption-Abstract'],
        'title': ['-XMP:Title', '-IPTC:ObjectName'],
        'keywords': ['-XMP:Subject', '-IPTC:Keywords'],
    }
    
    # Tags to read for common metadata
    READ_TAGS = [
        'FileName',
        'DateTimeOriginal',
        'CreateDate',
        'ModifyDate',
        'Make',
        'Model',
        'LensModel',
        'Artist',
        'Copyright',
        'ImageWidth',
        'ImageHeight',
        'ISO',
        'ExposureTime',
        'FNumber',
        'FocalLength',
        'GPSLatitude',
        'GPSLongitude',
        'XMP:Event',
        'XMP:Location',
        'IPTC:Caption-Abstract',
    ]
    
    def __init__(self, exiftool_path: str = 'exiftool'):
        self.exiftool_path = exiftool_path
        self._check_exiftool()
    
    def _check_exiftool(self):
        """Verify exiftool is available"""
        try:
            subprocess.run(
                [self.exiftool_path, '-ver'],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "exiftool not found. Please install it:\n"
                "  macOS: brew install exiftool\n"
                "  Ubuntu: apt install libimage-exiftool-perl"
            )
    
    def _run(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run exiftool with given arguments"""
        cmd = [self.exiftool_path] + args
        return subprocess.run(cmd, capture_output=True, text=True, check=check)
    
    def read(self, filepath: Union[str, Path]) -> Dict[str, Any]:
        """Read metadata from a file"""
        filepath = str(filepath)
        
        args = ['-json', '-G'] + [f'-{tag}' for tag in self.READ_TAGS] + [filepath]
        result = self._run(args, check=False)
        
        if result.returncode != 0:
            return {}
        
        try:
            data = json.loads(result.stdout)
            return data[0] if data else {}
        except json.JSONDecodeError:
            return {}
    
    def read_date(self, filepath: Union[str, Path]) -> Optional[datetime]:
        """Extract the original date/time from a file"""
        metadata = self.read(filepath)
        
        # Try different date fields in order of preference
        for field in ['EXIF:DateTimeOriginal', 'EXIF:CreateDate', 'File:FileModifyDate']:
            date_str = metadata.get(field)
            if date_str:
                try:
                    # Handle EXIF date format: "YYYY:MM:DD HH:MM:SS"
                    return datetime.strptime(date_str[:19], '%Y:%m:%d %H:%M:%S')
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def read_camera(self, filepath: Union[str, Path]) -> Optional[str]:
        """Get camera model from file"""
        metadata = self.read(filepath)
        return metadata.get('EXIF:Model') or metadata.get('EXIF:Make')
    
    def write(self, filepath: Union[str, Path], **kwargs) -> bool:
        """
        Write metadata to a file
        
        Args:
            filepath: Path to the file
            **kwargs: Field names and values (author, copyright, event, location, etc.)
        
        Returns:
            True if successful
        """
        filepath = str(filepath)
        args = ['-overwrite_original']
        
        for field, value in kwargs.items():
            if value is None:
                continue
                
            field_lower = field.lower()
            
            if field_lower in self.FIELD_MAP:
                # Map to multiple tags
                for tag in self.FIELD_MAP[field_lower]:
                    args.append(f'{tag}={value}')
            elif field_lower == 'gps':
                # Handle GPS as "lat,lon"
                try:
                    lat, lon = map(float, str(value).split(','))
                    args.extend([
                        f'-GPSLatitude={abs(lat)}',
                        f'-GPSLatitudeRef={"N" if lat >= 0 else "S"}',
                        f'-GPSLongitude={abs(lon)}',
                        f'-GPSLongitudeRef={"E" if lon >= 0 else "W"}',
                    ])
                except (ValueError, TypeError):
                    print(f"Warning: Invalid GPS format: {value}", file=sys.stderr)
            else:
                # Direct tag assignment
                args.append(f'-{field}={value}')
        
        args.append(filepath)
        
        try:
            result = self._run(args)
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False
    
    def write_batch(self, filepaths: List[Union[str, Path]], **kwargs) -> int:
        """
        Write metadata to multiple files at once
        
        Returns:
            Number of successfully updated files
        """
        if not filepaths:
            return 0
        
        args = ['-overwrite_original']
        
        for field, value in kwargs.items():
            if value is None:
                continue
            
            field_lower = field.lower()
            
            if field_lower in self.FIELD_MAP:
                for tag in self.FIELD_MAP[field_lower]:
                    args.append(f'{tag}={value}')
            elif field_lower == 'gps':
                try:
                    lat, lon = map(float, str(value).split(','))
                    args.extend([
                        f'-GPSLatitude={abs(lat)}',
                        f'-GPSLatitudeRef={"N" if lat >= 0 else "S"}',
                        f'-GPSLongitude={abs(lon)}',
                        f'-GPSLongitudeRef={"E" if lon >= 0 else "W"}',
                    ])
                except (ValueError, TypeError):
                    print(f"Warning: Invalid GPS format: {value}", file=sys.stderr)
            else:
                args.append(f'-{field}={value}')
        
        args.extend(str(f) for f in filepaths)
        
        try:
            result = self._run(args, check=False)
            # Parse output to count successes
            if 'image files updated' in result.stdout:
                import re
                match = re.search(r'(\d+) image files updated', result.stdout)
                if match:
                    return int(match.group(1))
            return len(filepaths) if result.returncode == 0 else 0
        except subprocess.CalledProcessError:
            return 0
    
    def copy_metadata(self, source: Union[str, Path], dest: Union[str, Path]) -> bool:
        """Copy all metadata from source to destination file"""
        try:
            result = self._run([
                '-overwrite_original',
                '-TagsFromFile', str(source),
                '-all:all',
                str(dest)
            ])
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False
    
    def remove_metadata(self, filepath: Union[str, Path], keep_orientation: bool = True) -> bool:
        """Remove all metadata from a file"""
        args = ['-overwrite_original', '-all=']
        
        if keep_orientation:
            args.append('-TagsFromFile')
            args.append('@')
            args.append('-Orientation')
        
        args.append(str(filepath))
        
        try:
            result = self._run(args)
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False
    
    def show(self, filepath: Union[str, Path]) -> str:
        """Get a human-readable summary of metadata"""
        metadata = self.read(filepath)
        
        if not metadata:
            return "No metadata found"
        
        lines = []
        
        # File info
        lines.append(f"File: {metadata.get('File:FileName', 'Unknown')}")
        
        # Date
        date = metadata.get('EXIF:DateTimeOriginal') or metadata.get('EXIF:CreateDate')
        if date:
            lines.append(f"Date: {date}")
        
        # Camera
        camera = metadata.get('EXIF:Model')
        if camera:
            make = metadata.get('EXIF:Make', '')
            lines.append(f"Camera: {make} {camera}".strip())
        
        # Lens
        lens = metadata.get('EXIF:LensModel')
        if lens:
            lines.append(f"Lens: {lens}")
        
        # Exposure
        iso = metadata.get('EXIF:ISO')
        shutter = metadata.get('EXIF:ExposureTime')
        aperture = metadata.get('EXIF:FNumber')
        focal = metadata.get('EXIF:FocalLength')
        
        exposure_parts = []
        if iso:
            exposure_parts.append(f"ISO {iso}")
        if shutter:
            exposure_parts.append(f"{shutter}s")
        if aperture:
            exposure_parts.append(f"f/{aperture}")
        if focal:
            exposure_parts.append(focal)
        
        if exposure_parts:
            lines.append(f"Exposure: {', '.join(exposure_parts)}")
        
        # Dimensions
        width = metadata.get('File:ImageWidth') or metadata.get('EXIF:ImageWidth')
        height = metadata.get('File:ImageHeight') or metadata.get('EXIF:ImageHeight')
        if width and height:
            lines.append(f"Dimensions: {width}x{height}")
        
        # GPS
        lat = metadata.get('EXIF:GPSLatitude')
        lon = metadata.get('EXIF:GPSLongitude')
        if lat and lon:
            lines.append(f"GPS: {lat}, {lon}")
        
        # Custom metadata
        lines.append("")
        lines.append("--- Custom Metadata ---")
        
        artist = metadata.get('EXIF:Artist')
        if artist:
            lines.append(f"Author: {artist}")
        
        copyright_info = metadata.get('EXIF:Copyright')
        if copyright_info:
            lines.append(f"Copyright: {copyright_info}")
        
        event = metadata.get('XMP:Event')
        if event:
            lines.append(f"Event: {event}")
        
        location = metadata.get('XMP:Location')
        if location:
            lines.append(f"Location: {location}")
        
        return '\n'.join(lines)


def main():
    """CLI interface for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='EXIF utilities')
    parser.add_argument('file', help='Image file to process')
    parser.add_argument('--show', '-s', action='store_true', help='Show metadata')
    parser.add_argument('--author', '-a', help='Set author')
    parser.add_argument('--copyright', '-c', help='Set copyright')
    parser.add_argument('--event', '-e', help='Set event')
    parser.add_argument('--location', '-l', help='Set location')
    parser.add_argument('--gps', help='Set GPS (lat,lon)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    exif = ExifTool()
    
    if args.show:
        if args.json:
            print(json.dumps(exif.read(args.file), indent=2))
        else:
            print(exif.show(args.file))
    else:
        # Build kwargs from arguments
        kwargs = {}
        if args.author:
            kwargs['author'] = args.author
        if args.copyright:
            kwargs['copyright'] = args.copyright
        if args.event:
            kwargs['event'] = args.event
        if args.location:
            kwargs['location'] = args.location
        if args.gps:
            kwargs['gps'] = args.gps
        
        if kwargs:
            if exif.write(args.file, **kwargs):
                print(f"Updated: {args.file}")
            else:
                print(f"Failed to update: {args.file}", file=sys.stderr)
                sys.exit(1)
        else:
            # Default to showing metadata
            print(exif.show(args.file))


if __name__ == '__main__':
    main()
