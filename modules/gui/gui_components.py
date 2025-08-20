"""
GUI Components Module
Reusable GUI components and widgets for the COSMED converter
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Callable, Optional, Dict, Any, List
from .theme_manager import ThemeManager
from .progress_tracker import ProgressState

class FileSelector(ctk.CTkFrame):
    """Reusable file/folder selector component"""
    
    def __init__(self, parent, title: str, mode: str = "folder", **kwargs):
        """
        Initialize file selector
        
        Args:
            parent: Parent widget
            title: Title for the selector
            mode: Selection mode ("folder", "file_open", "file_save")
        """
        super().__init__(parent, **kwargs)
        self.mode = mode
        self.selected_path = ctk.StringVar()
        self.callback: Optional[Callable] = None
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        
        # Title label
        self.title_label = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=14, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5))
        
        # Path entry
        self.path_entry = ctk.CTkEntry(self, textvariable=self.selected_path, height=35)
        self.path_entry.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(10, 5), pady=(0, 10))
        
        # Browse button
        self.browse_button = ctk.CTkButton(
            self, 
            text="Browse", 
            width=100, 
            height=35,
            command=self._browse
        )
        self.browse_button.grid(row=1, column=2, padx=(0, 10), pady=(0, 10))
    
    def _browse(self):
        """Handle browse button click"""
        if self.mode == "folder":
            path = filedialog.askdirectory(
                title=f"Select folder",
                initialdir=self.selected_path.get() or "."
            )
        elif self.mode == "file_open":
            path = filedialog.askopenfilename(
                title=f"Select file",
                initialdir=self.selected_path.get() or ".",
                filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
            )
        elif self.mode == "file_save":
            path = filedialog.asksaveasfilename(
                title=f"Save file as",
                initialdir=self.selected_path.get() or ".",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
        else:
            path = None
        
        if path:
            self.selected_path.set(path)
            if self.callback:
                self.callback(path)
    
    def set_callback(self, callback: Callable[[str], None]):
        """Set callback for path selection"""
        self.callback = callback
    
    def get_path(self) -> str:
        """Get selected path"""
        return self.selected_path.get()
    
    def set_path(self, path: str):
        """Set path programmatically"""
        self.selected_path.set(path)

class ProgressPanel(ctk.CTkFrame):
    """Progress display panel with status and progress bar"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_var = ctk.DoubleVar()
        self.progress_bar = ctk.CTkProgressBar(self, variable=self.progress_var, height=20)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        self.progress_bar.set(0)
        
        # Status label
        self.status_var = ctk.StringVar(value="Ready")
        self.status_label = ctk.CTkLabel(
            self, 
            textvariable=self.status_var,
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 10))
        
        # Details label (smaller, for additional info)
        self.details_var = ctk.StringVar(value="")
        self.details_label = ctk.CTkLabel(
            self,
            textvariable=self.details_var,
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.details_label.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 20))
    
    def update_progress(self, progress_state: ProgressState):
        """Update progress display with ProgressState"""
        if progress_state.is_indeterminate:
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start()
        else:
            self.progress_bar.configure(mode="determinate")
            self.progress_bar.stop()
            self.progress_var.set(progress_state.percentage / 100.0)
        
        # Update status
        self.status_var.set(progress_state.message)
        
        # Update details
        if progress_state.stage:
            details = f"Stage: {progress_state.stage}"
            if progress_state.current > 0 and progress_state.total > 0:
                details += f" ({progress_state.current}/{progress_state.total})"
            self.details_var.set(details)
        else:
            self.details_var.set("")

class ExportTypeSelector(ctk.CTkFrame):
    """Export type selection component"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.export_type = ctk.StringVar(value="selected")
        self.callback: Optional[Callable] = None
        
        # Title
        self.title_label = ctk.CTkLabel(
            self, 
            text="Export Type", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.title_label.pack(pady=(15, 10))
        
        # Radio buttons
        self.selected_radio = ctk.CTkRadioButton(
            self,
            text="Selected Parameters",
            variable=self.export_type,
            value="selected",
            command=self._on_change
        )
        self.selected_radio.pack(pady=5, anchor="w", padx=20)
        
        self.max_radio = ctk.CTkRadioButton(
            self,
            text="Max Values Only",
            variable=self.export_type,
            value="max",
            command=self._on_change
        )
        self.max_radio.pack(pady=5, anchor="w", padx=20)
        
        self.complete_radio = ctk.CTkRadioButton(
            self,
            text="Complete Dataset",
            variable=self.export_type,
            value="complete",
            command=self._on_change
        )
        self.complete_radio.pack(pady=5, anchor="w", padx=20)
        
        # Description
        self.description_label = ctk.CTkLabel(
            self,
            text=self._get_description("selected"),
            wraplength=250,
            justify="left",
            font=ctk.CTkFont(size=11)
        )
        self.description_label.pack(pady=(15, 20), padx=15)
    
    def _on_change(self):
        """Handle export type change"""
        export_type = self.export_type.get()
        self.description_label.configure(text=self._get_description(export_type))
        if self.callback:
            self.callback(export_type)
    
    def _get_description(self, export_type: str) -> str:
        """Get description for export type"""
        descriptions = {
            "selected": "15 key cardiopulmonary parameters including VO2/kg, VCO2/kg, VE/kg, and HR at specific phases.",
            "max": "Maximum values for all parameters. Simplified dataset for peak performance analysis.",
            "complete": "All measurement phases and parameters. Comprehensive dataset for detailed analysis."
        }
        return descriptions.get(export_type, "")
    
    def set_callback(self, callback: Callable[[str], None]):
        """Set callback for export type changes"""
        self.callback = callback
    
    def get_export_type(self) -> str:
        """Get selected export type"""
        return self.export_type.get()

class FileListDisplay(ctk.CTkFrame):
    """Display component for file lists with scrolling"""
    
    def __init__(self, parent, title: str = "Files", **kwargs):
        super().__init__(parent, **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self, 
            text=title, 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        # Count label
        self.count_label = ctk.CTkLabel(
            self, 
            text="No files", 
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.count_label.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 10))
        
        # File list text area
        self.file_text = ctk.CTkTextbox(
            self, 
            height=150,
            font=ctk.CTkFont(family="Consolas", size=10)
        )
        self.file_text.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))
    
    def update_files(self, files: List[str], base_directory: str = None):
        """
        Update file list display
        
        Args:
            files: List of file paths
            base_directory: Base directory for relative paths
        """
        self.file_text.delete("0.0", "end")
        
        if not files:
            self.file_text.insert("0.0", "No files found")
            self.count_label.configure(text="No files")
            return
        
        # Update count
        self.count_label.configure(text=f"{len(files)} files found")
        
        # Add files to display
        for i, file_path in enumerate(files, 1):
            filename = file_path.split("/")[-1] if "/" in file_path else file_path.split("\\")[-1]
            
            if base_directory:
                try:
                    import os
                    rel_path = os.path.relpath(file_path, base_directory)
                    if rel_path != filename:  # Show directory if different
                        directory = "/".join(rel_path.split("/")[:-1]) if "/" in rel_path else "\\".join(rel_path.split("\\")[:-1])
                        self.file_text.insert("end", f"{i:3d}. {filename}\n     📂 {directory}\n")
                    else:
                        self.file_text.insert("end", f"{i:3d}. {filename}\n")
                except:
                    self.file_text.insert("end", f"{i:3d}. {filename}\n")
            else:
                self.file_text.insert("end", f"{i:3d}. {filename}\n")

class StatusBar(ctk.CTkFrame):
    """Status bar component for showing application status"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, height=30, **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_propagate(False)  # Maintain fixed height
        
        # Status label
        self.status_var = ctk.StringVar(value="Ready")
        self.status_label = ctk.CTkLabel(
            self,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        self.status_label.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
    
    def set_status(self, message: str, status_type: str = "info"):
        """
        Set status message
        
        Args:
            message: Status message
            status_type: Type of status ("info", "success", "warning", "error")
        """
        # Add emoji based on status type
        emoji_map = {
            "info": "ℹ️",
            "success": "✅", 
            "warning": "⚠️",
            "error": "❌",
            "processing": "⚡"
        }
        
        emoji = emoji_map.get(status_type, "")
        display_message = f"{emoji} {message}" if emoji else message
        self.status_var.set(display_message)

class GUIComponents:
    """Factory class for creating standardized GUI components"""
    
    @staticmethod
    def create_file_selector(parent, title: str, mode: str = "folder", callback: Callable = None) -> FileSelector:
        """Create standardized file selector"""
        selector = FileSelector(parent, title, mode)
        if callback:
            selector.set_callback(callback)
        return selector
    
    @staticmethod
    def create_progress_panel(parent) -> ProgressPanel:
        """Create standardized progress panel"""
        return ProgressPanel(parent)
    
    @staticmethod
    def create_export_selector(parent, callback: Callable = None) -> ExportTypeSelector:
        """Create standardized export type selector"""
        selector = ExportTypeSelector(parent)
        if callback:
            selector.set_callback(callback)
        return selector
    
    @staticmethod
    def create_file_list(parent, title: str = "Files") -> FileListDisplay:
        """Create standardized file list display"""
        return FileListDisplay(parent, title)
    
    @staticmethod
    def create_status_bar(parent) -> StatusBar:
        """Create standardized status bar"""
        return StatusBar(parent)
    
    @staticmethod
    def show_info_dialog(title: str, message: str) -> None:
        """Show information dialog"""
        messagebox.showinfo(title, message)
    
    @staticmethod
    def show_error_dialog(title: str, message: str) -> None:
        """Show error dialog"""
        messagebox.showerror(title, message)
    
    @staticmethod
    def show_confirmation_dialog(title: str, message: str) -> bool:
        """Show confirmation dialog"""
        return messagebox.askyesno(title, message)
    
    @staticmethod
    def create_themed_button(parent, text: str, command: Callable = None, 
                           button_type: str = "primary", **kwargs) -> ctk.CTkButton:
        """
        Create themed button
        
        Args:
            parent: Parent widget
            text: Button text
            command: Button command
            button_type: Button style type ("primary", "secondary", "success", "warning", "danger")
            **kwargs: Additional button arguments
        """
        # Default button configuration
        button_config = {
            "text": text,
            "command": command,
            "height": 35,
            "font": ctk.CTkFont(size=12, weight="bold"),
            **kwargs
        }
        
        # Apply theme-specific colors based on button type
        if button_type == "success":
            button_config.update({"fg_color": "#28A745", "hover_color": "#218838"})
        elif button_type == "warning":
            button_config.update({"fg_color": "#FFC107", "hover_color": "#E0A800", "text_color": "black"})
        elif button_type == "danger":
            button_config.update({"fg_color": "#DC3545", "hover_color": "#C82333"})
        elif button_type == "secondary":
            button_config.update({"fg_color": "transparent", "border_width": 2})
        
        return ctk.CTkButton(parent, **button_config)
