"""
Configuration Manager Module
Manages application configuration and settings
"""
import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

class ConfigManager:
    """Manages application configuration"""
    
    DEFAULT_CONFIG = {
        'appearance': {
            'theme': 'dark',
            'color_theme': 'blue'
        },
        'export': {
            'auto_open_result': True,
            'default_export_type': 'selected',
            'include_summary_sheet': True
        },
        'processing': {
            'recursive_scan': True,
            'validate_structure': True,
            'skip_invalid_files': True
        },
        'selected_parameters': [
            "VO2/kg", "VCO2/kg", "VE/kg", "HR"
        ],
        'file_handling': {
            'backup_existing': False,
            'max_file_size_mb': 50
        },
        'gui': {
            'window_size': [1000, 800],
            'remember_last_folders': True,
            'show_progress_details': True
        }
    }
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_dir: Directory to store config files (None for default)
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Use user's home directory for config
            self.config_dir = Path.home() / '.cosmed_converter'
        
        self.config_file = self.config_dir / 'config.json'
        self.config_dir.mkdir(exist_ok=True)
        
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._merge_config(self.DEFAULT_CONFIG, loaded_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}. Using defaults.")
        
        return self.DEFAULT_CONFIG.copy()
    
    def _merge_config(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with defaults, ensuring all required keys exist"""
        merged = default.copy()
        
        for key, value in loaded.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_config(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def save_config(self) -> bool:
        """
        Save current configuration to file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key_path: Dot-separated key path (e.g., 'appearance.theme')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> None:
        """
        Set configuration value using dot notation
        
        Args:
            key_path: Dot-separated key path
            value: Value to set
        """
        keys = key_path.split('.')
        config_ref = self.config
        
        # Navigate to the parent of the final key
        for key in keys[:-1]:
            if key not in config_ref:
                config_ref[key] = {}
            config_ref = config_ref[key]
        
        # Set the final value
        config_ref[keys[-1]] = value
    
    def get_selected_parameters(self) -> List[str]:
        """Get list of selected parameters for export"""
        return self.get('selected_parameters', self.DEFAULT_CONFIG['selected_parameters'])
    
    def set_selected_parameters(self, parameters: List[str]) -> None:
        """Set selected parameters for export"""
        self.set('selected_parameters', parameters)
    
    def get_appearance_settings(self) -> Dict[str, Any]:
        """Get appearance settings"""
        return self.get('appearance', self.DEFAULT_CONFIG['appearance'])
    
    def set_appearance_settings(self, theme: str = None, color_theme: str = None) -> None:
        """Set appearance settings"""
        if theme:
            self.set('appearance.theme', theme)
        if color_theme:
            self.set('appearance.color_theme', color_theme)
    
    def get_export_settings(self) -> Dict[str, Any]:
        """Get export settings"""
        return self.get('export', self.DEFAULT_CONFIG['export'])
    
    def set_export_settings(self, **kwargs) -> None:
        """Set export settings"""
        for key, value in kwargs.items():
            if key in self.DEFAULT_CONFIG['export']:
                self.set(f'export.{key}', value)
    
    def get_gui_settings(self) -> Dict[str, Any]:
        """Get GUI settings"""
        return self.get('gui', self.DEFAULT_CONFIG['gui'])
    
    def set_gui_settings(self, **kwargs) -> None:
        """Set GUI settings"""
        for key, value in kwargs.items():
            if key in self.DEFAULT_CONFIG['gui']:
                self.set(f'gui.{key}', value)
    
    def get_last_folders(self) -> Dict[str, str]:
        """Get last used folders"""
        return self.get('last_folders', {})
    
    def set_last_folder(self, folder_type: str, path: str) -> None:
        """
        Set last used folder
        
        Args:
            folder_type: Type of folder ('input', 'output')
            path: Folder path
        """
        if not self.config.get('last_folders'):
            self.config['last_folders'] = {}
        self.config['last_folders'][folder_type] = path
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        self.config = self.DEFAULT_CONFIG.copy()
    
    def export_config(self, export_path: str) -> bool:
        """
        Export configuration to file
        
        Args:
            export_path: Path to export config file
            
        Returns:
            True if successful
        """
        try:
            with open(export_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except IOError:
            return False
    
    def import_config(self, import_path: str) -> bool:
        """
        Import configuration from file
        
        Args:
            import_path: Path to import config file
            
        Returns:
            True if successful
        """
        try:
            with open(import_path, 'r') as f:
                imported_config = json.load(f)
            self.config = self._merge_config(self.DEFAULT_CONFIG, imported_config)
            return True
        except (json.JSONDecodeError, IOError):
            return False
    
    def validate_config(self) -> Dict[str, Any]:
        """
        Validate current configuration
        
        Returns:
            Validation result dictionary
        """
        issues = []
        
        # Validate appearance settings
        valid_themes = ['dark', 'light', 'system']
        if self.get('appearance.theme') not in valid_themes:
            issues.append(f"Invalid theme: {self.get('appearance.theme')}")
        
        valid_color_themes = ['blue', 'green', 'dark-blue']
        if self.get('appearance.color_theme') not in valid_color_themes:
            issues.append(f"Invalid color theme: {self.get('appearance.color_theme')}")
        
        # Validate export settings
        if not isinstance(self.get('selected_parameters'), list):
            issues.append("Selected parameters must be a list")
        
        # Validate GUI settings
        window_size = self.get('gui.window_size')
        if not isinstance(window_size, list) or len(window_size) != 2:
            issues.append("Window size must be a list of two numbers")
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'config_file': str(self.config_file)
        }
