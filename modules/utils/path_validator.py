"""
Path Validator Module
Handles file and directory path validation for COSMED data processing
"""
import os
from typing import Optional

class PathValidator:
    """Validates file and directory paths"""
    
    @staticmethod
    def validate_directory(dir_path: Optional[str]) -> str:
        """
        Validate and normalize directory path
        
        Args:
            dir_path: Directory path to validate
            
        Returns:
            Normalized absolute path
            
        Raises:
            ValueError: If path is invalid
        """
        if not dir_path:
            raise ValueError("Directory path must be provided.")
            
        # Normalize path
        normalized_path = os.path.abspath(dir_path)
        
        # Validate existence
        if not os.path.exists(normalized_path):
            raise ValueError(f"Path does not exist: {normalized_path}")
            
        # Validate it's a directory
        if not os.path.isdir(normalized_path):
            raise ValueError(f"Provided path is not a directory: {normalized_path}")
            
        return normalized_path
    
    @staticmethod
    def validate_file_path(file_path: str, must_exist: bool = False) -> str:
        """
        Validate file path
        
        Args:
            file_path: File path to validate
            must_exist: Whether file must already exist
            
        Returns:
            Normalized absolute path
            
        Raises:
            ValueError: If path is invalid
        """
        if not file_path:
            raise ValueError("File path must be provided.")
            
        # Normalize path
        normalized_path = os.path.abspath(file_path)
        
        if must_exist:
            if not os.path.exists(normalized_path):
                raise ValueError(f"File does not exist: {normalized_path}")
            if not os.path.isfile(normalized_path):
                raise ValueError(f"Path is not a file: {normalized_path}")
        else:
            # Validate parent directory exists
            parent_dir = os.path.dirname(normalized_path)
            if not os.path.exists(parent_dir):
                raise ValueError(f"Parent directory does not exist: {parent_dir}")
                
        return normalized_path
    
    @staticmethod
    def is_xml_file(file_path: str) -> bool:
        """Check if file has XML extension"""
        return file_path.lower().endswith('.xml')
    
    @staticmethod
    def is_excel_file(file_path: str) -> bool:
        """Check if file has Excel extension"""
        return file_path.lower().endswith(('.xlsx', '.xls'))
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    @staticmethod
    def ensure_directory_exists(dir_path: str) -> str:
        """Create directory if it doesn't exist"""
        normalized_path = os.path.abspath(dir_path)
        os.makedirs(normalized_path, exist_ok=True)
        return normalized_path
