# COSMED Data Converter Modules
# Modular architecture for better code organization and maintenance

__version__ = "2.0.0"
__author__ = "COSMED Data Converter Team"

# Core modules for COSMED XML data processing
from .core.xml_parser import XmlParser
from .utils.path_validator import PathValidator
from .core.data_extractor import DataExtractor
from .core.excel_formatter import ExcelFormatter
from .core.export_manager import ExportManager

# GUI modules
from .gui.gui_components import GUIComponents
from .gui.theme_manager import ThemeManager
from .gui.progress_tracker import ProgressTracker

# Utility modules
from .utils.file_scanner import FileScanner
from .utils.error_handler import ErrorHandler, safe_execute
from .gui.config_manager import ConfigManager

__all__ = [
    # Core modules
    'XmlParser',
    'PathValidator', 
    'DataExtractor',
    'ExcelFormatter',
    'ExportManager',
    
    # GUI modules
    'GUIComponents',
    'ThemeManager',
    'ProgressTracker',
    
    # Utility modules
    'FileScanner',
    'ErrorHandler',
    'ConfigManager',
    'safe_execute'
]
