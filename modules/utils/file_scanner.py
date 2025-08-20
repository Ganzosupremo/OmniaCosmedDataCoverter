"""
File Scanner Module
Handles file discovery and scanning operations
"""
import os
from typing import List, Dict, Any, Optional
from .path_validator import PathValidator

class FileScanner:
    """File scanning utilities for COSMED XML files"""
    
    def __init__(self):
        self.path_validator = PathValidator()
    
    def find_xml_files(self, directory: str, recursive: bool = True) -> List[str]:
        """
        Find all XML files in directory
        
        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories
            
        Returns:
            List of XML file paths
        """
        validated_dir = self.path_validator.validate_directory(directory)
        xml_files = []
        
        if recursive:
            # Walk through all subdirectories
            for root, dirs, files in os.walk(validated_dir):
                for filename in files:
                    if self.path_validator.is_xml_file(filename):
                        file_path = os.path.join(root, filename)
                        xml_files.append(file_path)
        else:
            # Only scan the specified directory
            try:
                for filename in os.listdir(validated_dir):
                    if self.path_validator.is_xml_file(filename):
                        file_path = os.path.join(validated_dir, filename)
                        if os.path.isfile(file_path):
                            xml_files.append(file_path)
            except OSError as e:
                raise ValueError(f"Error scanning directory: {e}")
        
        return sorted(xml_files)  # Return sorted for consistent ordering
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed information about a file
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
        try:
            stat = os.stat(file_path)
            return {
                'path': file_path,
                'filename': os.path.basename(file_path),
                'directory': os.path.dirname(file_path),
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'is_xml': self.path_validator.is_xml_file(file_path),
                'exists': True
            }
        except OSError:
            return {
                'path': file_path,
                'filename': os.path.basename(file_path),
                'directory': os.path.dirname(file_path),
                'size': 0,
                'modified': None,
                'is_xml': self.path_validator.is_xml_file(file_path),
                'exists': False
            }
    
    def scan_directory_summary(self, directory: str) -> Dict[str, Any]:
        """
        Get summary information about directory contents
        
        Args:
            directory: Directory to scan
            
        Returns:
            Dictionary with directory scan summary
        """
        validated_dir = self.path_validator.validate_directory(directory)
        
        summary = {
            'directory': validated_dir,
            'xml_files': [],
            'xml_count': 0,
            'total_size': 0,
            'subdirectories': [],
            'scan_error': None
        }
        
        try:
            xml_files = self.find_xml_files(validated_dir)
            summary['xml_files'] = xml_files
            summary['xml_count'] = len(xml_files)
            
            # Calculate total size
            total_size = 0
            for file_path in xml_files:
                try:
                    total_size += os.path.getsize(file_path)
                except OSError:
                    pass  # Skip files that can't be accessed
            summary['total_size'] = total_size
            
            # Find subdirectories
            subdirs = []
            for item in os.listdir(validated_dir):
                item_path = os.path.join(validated_dir, item)
                if os.path.isdir(item_path):
                    subdirs.append(item_path)
            summary['subdirectories'] = sorted(subdirs)
            
        except Exception as e:
            summary['scan_error'] = str(e)
        
        return summary
    
    def filter_files_by_pattern(self, files: List[str], pattern: str) -> List[str]:
        """
        Filter files by filename pattern
        
        Args:
            files: List of file paths
            pattern: Pattern to match (case-insensitive)
            
        Returns:
            Filtered list of files
        """
        if not pattern:
            return files
        
        pattern_lower = pattern.lower()
        filtered_files = []
        
        for file_path in files:
            filename = os.path.basename(file_path).lower()
            if pattern_lower in filename:
                filtered_files.append(file_path)
        
        return filtered_files
    
    def get_relative_paths(self, files: List[str], base_directory: str) -> List[Dict[str, str]]:
        """
        Get relative paths for files from base directory
        
        Args:
            files: List of absolute file paths
            base_directory: Base directory for relative paths
            
        Returns:
            List of dictionaries with absolute and relative paths
        """
        base_dir = self.path_validator.validate_directory(base_directory)
        result = []
        
        for file_path in files:
            try:
                rel_path = os.path.relpath(file_path, base_dir)
                result.append({
                    'absolute_path': file_path,
                    'relative_path': rel_path,
                    'filename': os.path.basename(file_path),
                    'directory': os.path.dirname(rel_path) if os.path.dirname(rel_path) != '.' else ''
                })
            except ValueError:
                # Can't compute relative path (different drives on Windows)
                result.append({
                    'absolute_path': file_path,
                    'relative_path': file_path,
                    'filename': os.path.basename(file_path),
                    'directory': os.path.dirname(file_path)
                })
        
        return result
    
    def validate_files_accessible(self, files: List[str]) -> Dict[str, List[str]]:
        """
        Validate that all files are accessible
        
        Args:
            files: List of file paths to validate
            
        Returns:
            Dictionary with 'accessible' and 'inaccessible' file lists
        """
        accessible = []
        inaccessible = []
        
        for file_path in files:
            try:
                with open(file_path, 'rb') as f:
                    # Try to read first byte to ensure file is accessible
                    f.read(1)
                accessible.append(file_path)
            except (OSError, IOError, PermissionError):
                inaccessible.append(file_path)
        
        return {
            'accessible': accessible,
            'inaccessible': inaccessible,
            'total_count': len(files),
            'accessible_count': len(accessible),
            'inaccessible_count': len(inaccessible)
        }
