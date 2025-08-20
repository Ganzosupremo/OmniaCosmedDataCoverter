"""
Theme Manager Module
Manages GUI themes and appearance settings
"""
import customtkinter as ctk
from typing import Dict, Callable, Optional

class ThemeManager:
    """Manages GUI themes and appearance"""
    
    AVAILABLE_THEMES = {
        'light': 'Light',
        'dark': 'Dark', 
        'system': 'System'
    }
    
    AVAILABLE_COLOR_THEMES = {
        'blue': 'Blue',
        'green': 'Green',
        'dark-blue': 'Dark Blue'
    }
    
    def __init__(self, initial_theme: str = 'dark', initial_color: str = 'blue'):
        """
        Initialize theme manager
        
        Args:
            initial_theme: Initial appearance theme
            initial_color: Initial color theme
        """
        self.current_theme = initial_theme
        self.current_color = initial_color
        self.theme_callbacks: list[Callable] = []
        
        # Apply initial themes
        self.apply_theme(initial_theme, initial_color)
    
    def apply_theme(self, theme_name: str, color_theme: str = None) -> None:
        """
        Apply theme to the application
        
        Args:
            theme_name: Theme name ('light', 'dark', 'system')
            color_theme: Color theme name
        """
        if theme_name in self.AVAILABLE_THEMES:
            ctk.set_appearance_mode(theme_name)
            self.current_theme = theme_name
        
        if color_theme and color_theme in self.AVAILABLE_COLOR_THEMES:
            ctk.set_default_color_theme(color_theme)
            self.current_color = color_theme
        
        # Notify callbacks about theme change
        self._notify_theme_change()
    
    def get_current_theme(self) -> str:
        """Get current theme name"""
        return self.current_theme
    
    def get_current_color_theme(self) -> str:
        """Get current color theme name"""
        return self.current_color
    
    def get_available_themes(self) -> Dict[str, str]:
        """Get dictionary of available themes"""
        return self.AVAILABLE_THEMES.copy()
    
    def get_available_color_themes(self) -> Dict[str, str]:
        """Get dictionary of available color themes"""
        return self.AVAILABLE_COLOR_THEMES.copy()
    
    def register_theme_callback(self, callback: Callable) -> None:
        """
        Register callback to be called when theme changes
        
        Args:
            callback: Function to call on theme change
        """
        if callback not in self.theme_callbacks:
            self.theme_callbacks.append(callback)
    
    def unregister_theme_callback(self, callback: Callable) -> None:
        """
        Unregister theme callback
        
        Args:
            callback: Function to remove from callbacks
        """
        if callback in self.theme_callbacks:
            self.theme_callbacks.remove(callback)
    
    def _notify_theme_change(self) -> None:
        """Notify all registered callbacks about theme change"""
        for callback in self.theme_callbacks:
            try:
                callback(self.current_theme, self.current_color)
            except Exception as e:
                print(f"Error in theme callback: {e}")
    
    def get_theme_colors(self) -> Dict[str, str]:
        """
        Get color values for current theme
        
        Returns:
            Dictionary with theme color information
        """
        # These are approximate values - actual colors may vary
        if self.current_theme == 'light':
            return {
                'bg_color': '#FFFFFF',
                'fg_color': '#000000',
                'button_color': '#1F6AA5',
                'button_hover': '#144870',
                'entry_color': '#F9F9FA',
                'text_color': '#000000',
                'disabled_color': '#A0A0A0'
            }
        else:  # dark or system (defaulting to dark)
            return {
                'bg_color': '#212121',
                'fg_color': '#FFFFFF', 
                'button_color': '#1F6AA5',
                'button_hover': '#14375E',
                'entry_color': '#343638',
                'text_color': '#FFFFFF',
                'disabled_color': '#6B6B6B'
            }
    
    def create_themed_font(self, size: int = 12, weight: str = "normal") -> ctk.CTkFont:
        """
        Create font with theme-appropriate settings
        
        Args:
            size: Font size
            weight: Font weight ("normal", "bold")
            
        Returns:
            Themed CTkFont object
        """
        return ctk.CTkFont(size=size, weight=weight)
    
    def get_status_colors(self) -> Dict[str, str]:
        """Get colors for different status types"""
        return {
            'success': '#28A745',
            'warning': '#FFC107', 
            'error': '#DC3545',
            'info': '#17A2B8',
            'processing': '#6610F2'
        }
    
    def apply_widget_theme(self, widget, widget_type: str = "default") -> None:
        """
        Apply theme-specific styling to widget
        
        Args:
            widget: Widget to style
            widget_type: Type of widget for specific styling
        """
        colors = self.get_theme_colors()
        
        try:
            if widget_type == "header":
                widget.configure(
                    font=self.create_themed_font(size=16, weight="bold"),
                    text_color=colors['fg_color']
                )
            elif widget_type == "button_primary":
                widget.configure(
                    fg_color=colors['button_color'],
                    hover_color=colors['button_hover'],
                    font=self.create_themed_font(weight="bold")
                )
            elif widget_type == "button_secondary":
                widget.configure(
                    fg_color="transparent",
                    border_width=2,
                    border_color=colors['button_color'],
                    text_color=colors['button_color'],
                    hover_color=colors['button_color']
                )
            elif widget_type == "status":
                widget.configure(
                    text_color=colors['fg_color'],
                    font=self.create_themed_font(size=11)
                )
        except Exception as e:
            print(f"Error applying theme to widget: {e}")
    
    def get_progress_colors(self) -> Dict[str, str]:
        """Get colors for progress indicators"""
        status_colors = self.get_status_colors()
        return {
            'normal': status_colors['info'],
            'success': status_colors['success'],
            'error': status_colors['error'],
            'warning': status_colors['warning']
        }
    
    def create_themed_window_geometry(self, base_width: int = 800, base_height: int = 600) -> str:
        """
        Create window geometry string appropriate for current theme
        
        Args:
            base_width: Base window width
            base_height: Base window height
            
        Returns:
            Geometry string
        """
        # Adjust size slightly based on theme for optimal appearance
        if self.current_theme == 'light':
            width = base_width
            height = base_height
        else:
            width = base_width + 20  # Slightly larger for dark theme
            height = base_height + 20
        
        return f"{width}x{height}"
