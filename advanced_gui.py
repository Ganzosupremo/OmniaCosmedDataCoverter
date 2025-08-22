import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
from xml_data_reader import XmlDataReader
from excel_exporter import ExcelExporter
import webbrowser

class AdvancedCosmedGUI:
    """
    GUI for COSMED XML Data Converter.
    """
    def __init__(self):
        # Set the appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.window: ctk.CTk = ctk.CTk()
        self.window.title("COSMED XML Data Converter")
        self.window.geometry("1000x800")
        self.window.minsize(900, 700)
        
        # Configure grid weights
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        # Variables
        self.input_folder: ctk.StringVar = ctk.StringVar()
        self.output_file: ctk.StringVar = ctk.StringVar()
        self.export_type: ctk.StringVar = ctk.StringVar(value="selected")
        self.progress_var: ctk.DoubleVar = ctk.DoubleVar()
        self.status_var: ctk.StringVar = ctk.StringVar(value="Ready to process XML files")
        self.xml_files: list = []
        self.processing: bool = False
        
        # Custom parameters variables
        self.available_parameters: list = []  # Will be populated after scanning
        self.custom_parameters: dict = {}  # Dictionary: {param_name: [phases]}
        self.available_phases: list = ['Value', 'Rest', 'Warmup', 'MFO', 'AT', 'RC', 'Max', 'Pred', 'PercPred', 'Normal', 'Class']
        
        # Create UI
        self.create_widgets()
        self.update_ui_state()
        
    def create_widgets(self):
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Create bottom panel
        self.create_bottom_panel()
    
    def create_sidebar(self):
        # Sidebar frame
        self.sidebar_frame = ctk.CTkFrame(self.window, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)
        
        # Logo and title
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="🫁 COSMED\nConverter", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))
        
        # Export type section
        self.export_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.export_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        self.export_title = ctk.CTkLabel(
            self.export_frame, 
            text="Export Type", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.export_title.pack(pady=(0, 10))
        
        # Radio buttons for export type
        self.export_selected = ctk.CTkRadioButton(
            self.export_frame,
            text="Selected Parameters",
            variable=self.export_type,
            value="selected",
            command=self.on_export_type_change
        )
        self.export_selected.pack(pady=5, anchor="w")
        
        self.export_max = ctk.CTkRadioButton(
            self.export_frame,
            text="Max Values Only",
            variable=self.export_type,
            value="max",
            command=self.on_export_type_change
        )
        self.export_max.pack(pady=5, anchor="w")
        
        self.export_complete = ctk.CTkRadioButton(
            self.export_frame,
            text="Complete Dataset",
            variable=self.export_type,
            value="complete",
            command=self.on_export_type_change
        )
        self.export_complete.pack(pady=5, anchor="w")
        
        self.export_custom = ctk.CTkRadioButton(
            self.export_frame,
            text="Custom Parameters",
            variable=self.export_type,
            value="custom",
            command=self.on_export_type_change
        )
        self.export_custom.pack(pady=5, anchor="w")
        
        # Custom parameters button
        self.custom_params_button = ctk.CTkButton(
            self.export_frame,
            text="⚙️ Select Parameters",
            command=self.show_custom_params_dialog,
            height=30,
            width=160,
            state="disabled"
        )
        self.custom_params_button.pack(pady=(5, 0), anchor="w")
        
        # Settings section
        self.settings_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.settings_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        self.settings_title = ctk.CTkLabel(
            self.settings_frame, 
            text="Settings", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.settings_title.pack(pady=(0, 10))
        
        # Theme selection
        self.theme_label = ctk.CTkLabel(self.settings_frame, text="Theme:")
        self.theme_label.pack(anchor="w")
        
        self.theme_menu = ctk.CTkOptionMenu(
            self.settings_frame, 
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode
        )
        self.theme_menu.pack(pady=(5, 15), fill="x")
        self.theme_menu.set("Dark")
        
        # Auto-open result checkbox
        self.auto_open_var = ctk.BooleanVar(value=True)
        self.auto_open_checkbox = ctk.CTkCheckBox(
            self.settings_frame,
            text="Auto-open result",
            variable=self.auto_open_var
        )
        self.auto_open_checkbox.pack(anchor="w", pady=5)
        
        # Buttons section
        self.buttons_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.buttons_frame.grid(row=8, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # Help button
        self.help_button = ctk.CTkButton(
            self.buttons_frame,
            text="📖 Help",
            command=self.show_help,
            width=160
        )
        self.help_button.pack(pady=5, fill="x")
        
        # About button
        self.about_button = ctk.CTkButton(
            self.buttons_frame,
            text="ℹ️ About",
            command=self.show_about,
            width=160
        )
        self.about_button.pack(pady=5, fill="x")
        
        # GitHub button
        self.github_button = ctk.CTkButton(
            self.buttons_frame,
            text="🔗 GitHub",
            command=self.open_github,
            width=160,
            fg_color="gray",
            hover_color="gray30"
        )
        self.github_button.pack(pady=5, fill="x")
    
    def create_main_content(self):
        # Main content frame
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.grid(row=0, column=1, padx=20, pady=(20, 0), sticky="nsew")
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="COSMED XML to Excel Converter",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=3, pady=(20, 30))
        
        # Input section
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.grid(row=1, column=0, columnspan=3, padx=20, pady=(0, 15), sticky="ew")
        self.input_frame.grid_columnconfigure(1, weight=1)
        
        self.input_title = ctk.CTkLabel(
            self.input_frame, 
            text="📁 Input Folder", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.input_title.grid(row=0, column=0, columnspan=3, padx=20, pady=(15, 10), sticky="w")
        
        self.input_entry = ctk.CTkEntry(
            self.input_frame, 
            textvariable=self.input_folder,
            placeholder_text="Select folder containing XML files...",
            height=35
        )
        self.input_entry.grid(row=1, column=0, columnspan=2, padx=(20, 10), pady=(0, 15), sticky="ew")
        
        self.browse_input_button = ctk.CTkButton(
            self.input_frame,
            text="Browse",
            width=100,
            height=35,
            command=self.browse_input_folder
        )
        self.browse_input_button.grid(row=1, column=2, padx=(0, 20), pady=(0, 15))
        
        # Output section
        self.output_frame = ctk.CTkFrame(self.main_frame)
        self.output_frame.grid(row=2, column=0, columnspan=3, padx=20, pady=(0, 15), sticky="ew")
        self.output_frame.grid_columnconfigure(1, weight=1)
        
        self.output_title = ctk.CTkLabel(
            self.output_frame, 
            text="💾 Output File", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.output_title.grid(row=0, column=0, columnspan=3, padx=20, pady=(15, 10), sticky="w")
        
        self.output_entry = ctk.CTkEntry(
            self.output_frame, 
            textvariable=self.output_file,
            placeholder_text="Choose output Excel file location...",
            height=35
        )
        self.output_entry.grid(row=1, column=0, columnspan=2, padx=(20, 10), pady=(0, 15), sticky="ew")
        
        self.browse_output_button = ctk.CTkButton(
            self.output_frame,
            text="Browse",
            width=100,
            height=35,
            command=self.browse_output_file
        )
        self.browse_output_button.grid(row=1, column=2, padx=(0, 20), pady=(0, 15))
        
        # Description frame
        self.desc_frame = ctk.CTkFrame(self.main_frame)
        self.desc_frame.grid(row=3, column=0, columnspan=3, padx=20, pady=(0, 15), sticky="ew")
        
        self.description_label = ctk.CTkLabel(
            self.desc_frame,
            text=self.get_export_description("selected"),
            wraplength=600,
            justify="left",
            font=ctk.CTkFont(size=13)
        )
        self.description_label.pack(padx=20, pady=15)
        
        # File list section
        self.file_section = ctk.CTkFrame(self.main_frame)
        self.file_section.grid(row=4, column=0, columnspan=3, padx=20, pady=(0, 20), sticky="nsew")
        self.file_section.grid_columnconfigure(0, weight=1)
        self.file_section.grid_rowconfigure(2, weight=1)
        
        self.file_title = ctk.CTkLabel(
            self.file_section, 
            text="📄 XML Files Found", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.file_title.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.file_count_label = ctk.CTkLabel(
            self.file_section, 
            text="No files scanned yet",
            font=ctk.CTkFont(size=12)
        )
        self.file_count_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # File list with scrollbar
        self.file_text_frame = ctk.CTkFrame(self.file_section)
        self.file_text_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.file_text_frame.grid_columnconfigure(0, weight=1)
        self.file_text_frame.grid_rowconfigure(0, weight=1)
        
        self.file_list_text = ctk.CTkTextbox(self.file_text_frame, height=200, font=ctk.CTkFont(family="Consolas", size=11))
        self.file_list_text.grid(row=0, column=0, sticky="nsew")
    
    def create_bottom_panel(self):
        # Control buttons frame
        self.control_frame = ctk.CTkFrame(self.window)
        self.control_frame.grid(row=1, column=1, padx=20, pady=(10, 0), sticky="ew")
        self.control_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Scan button
        self.scan_button = ctk.CTkButton(
            self.control_frame,
            text="🔍 Scan Folder",
            command=self.scan_folder,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.scan_button.grid(row=0, column=0, padx=10, pady=15, sticky="ew")
        
        # Process button
        self.process_button = ctk.CTkButton(
            self.control_frame,
            text="⚡ Convert to Excel",
            command=self.process_files,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("gray70", "gray30"),
            state="disabled"
        )
        self.process_button.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        
        # Clear button
        self.clear_button = ctk.CTkButton(
            self.control_frame,
            text="🗑️ Clear All",
            command=self.clear_all,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.clear_button.grid(row=0, column=2, padx=10, pady=15, sticky="ew")
        
        # Progress and status frame
        self.status_frame = ctk.CTkFrame(self.window)
        self.status_frame.grid(row=2, column=1, padx=20, pady=(10, 20), sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.status_frame, variable=self.progress_var, height=20)
        self.progress_bar.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.progress_bar.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            textvariable=self.status_var,
            font=ctk.CTkFont(size=13)
        )
        self.status_label.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")
    
    def get_export_description(self, export_type):
        descriptions = {
            "selected": "📊 Selected Parameters: Exports 15 key cardiopulmonary parameters including VO2/kg at MFO, AT, RC, and Max phases. Perfect for focused clinical analysis and research.",
            "max": "📈 Max Values Only: Exports maximum values for all parameters. Simplified dataset ideal for peak performance analysis and quick assessments.",
            "complete": "📋 Complete Dataset: Exports all measurement phases (Rest, Warmup, MFO, AT, RC, Max, Predicted, etc.). Comprehensive data for detailed research and analysis.",
            "custom": "⚙️ Custom Parameters: Choose specific parameters and phases to export. Tailored datasets for specialized analysis and research requirements."
        }
        return descriptions.get(export_type, "")
    
    def on_export_type_change(self):
        export_type = self.export_type.get()
        self.description_label.configure(text=self.get_export_description(export_type))
        
        # Enable/disable custom parameters button
        if export_type == "custom":
            self.custom_params_button.configure(state="normal")
        else:
            self.custom_params_button.configure(state="disabled")
        
        # Update default filename if output is not set
        if not self.output_file.get() and self.input_folder.get():
            folder_name = os.path.basename(self.input_folder.get()) or "cosmed_data"
            default_names = {
                "selected": f"{folder_name}_selected_parameters.xlsx",
                "max": f"{folder_name}_max_values.xlsx",
                "complete": f"{folder_name}_complete_dataset.xlsx",
                "custom": f"{folder_name}_custom_parameters.xlsx"
            }
            default_path = os.path.join(
                os.path.dirname(self.input_folder.get()) or os.getcwd(),
                default_names[export_type]
            )
            self.output_file.set(default_path)
    
    def browse_input_folder(self):
        folder = filedialog.askdirectory(
            title="Select folder containing COSMED XML files",
            initialdir=os.getcwd()
        )
        if folder:
            self.input_folder.set(folder)
            self.file_list_text.delete("0.0", "end")
            self.xml_files = []
            self.update_ui_state()
            # Auto-suggest output filename
            self.on_export_type_change()
    
    def browse_output_file(self):
        initial_name = ""
        if self.input_folder.get():
            folder_name = os.path.basename(self.input_folder.get()) or "cosmed_data"
            export_type = self.export_type.get()
            initial_name = f"{folder_name}_{export_type}_export.xlsx"
        
        file = filedialog.asksaveasfilename(
            title="Save Excel file as",
            defaultextension=".xlsx",
            initialname=initial_name,
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file:
            self.output_file.set(file)
            self.update_ui_state()
    
    def scan_folder(self):
        folder = self.input_folder.get()
        if not folder or not os.path.exists(folder):
            messagebox.showerror("Error", "Please select a valid input folder.")
            return
        
        self.status_var.set("🔍 Scanning for XML files...")
        self.file_list_text.delete("0.0", "end")
        self.progress_bar.set(0.2)
        
        # Find XML files
        self.xml_files = []
        try:
            for root, dirs, files in os.walk(folder):
                for filename in files:
                    if filename.lower().endswith(".xml"):
                        self.xml_files.append(os.path.join(root, filename))
            
            self.progress_bar.set(0.5)
            
            if self.xml_files:
                # Quick analysis to get available parameters
                try:
                    reader = XmlDataReader(folder)
                    sample_data = reader.extract_id_and_parameters()
                    if sample_data:
                        # Extract unique parameters from sample data
                        params = set()
                        for file_data in sample_data[:3]:  # Sample first few files
                            for param in file_data.get('parameters', []):
                                params.add(param['Name'])
                        self.available_parameters = sorted(list(params))
                    else:
                        self.available_parameters = []
                except:
                    self.available_parameters = []
                
                # Display files
                self.file_list_text.insert("0.0", f"📁 Scanning Results\n{'='*50}\n")
                self.file_list_text.insert("end", f"Found {len(self.xml_files)} XML files:\n\n")
                
                for i, file_path in enumerate(self.xml_files, 1):
                    filename = os.path.basename(file_path)
                    rel_path = os.path.relpath(file_path, folder)
                    self.file_list_text.insert("end", f"{i:3d}. {filename}\n")
                    if rel_path != filename:  # Show subfolder if different
                        self.file_list_text.insert("end", f"     📂 {os.path.dirname(rel_path)}\n")
                
                if self.available_parameters:
                    self.file_list_text.insert("end", f"\n📊 Available Parameters ({len(self.available_parameters)}):\n")
                    for param in self.available_parameters[:10]:  # Show first 10
                        self.file_list_text.insert("end", f"• {param}\n")
                    if len(self.available_parameters) > 10:
                        self.file_list_text.insert("end", f"• ... and {len(self.available_parameters) - 10} more\n")
                
                self.file_count_label.configure(
                    text=f"✅ {len(self.xml_files)} XML files ready for processing"
                )
                self.status_var.set(f"✅ Found {len(self.xml_files)} XML files ready for processing")
            else:
                self.file_list_text.insert("0.0", "❌ No XML Files Found\n")
                self.file_list_text.insert("end", "="*30 + "\n\n")
                self.file_list_text.insert("end", "No XML files found in the selected folder.\n\n")
                self.file_list_text.insert("end", "Please check:\n")
                self.file_list_text.insert("end", "• Folder contains .xml files\n")
                self.file_list_text.insert("end", "• Files have correct extension\n")
                self.file_list_text.insert("end", "• You have read permissions\n")
                
                self.file_count_label.configure(text="❌ No XML files found")
                self.status_var.set("❌ No XML files found in selected folder")
                
        except Exception as e:
            self.file_list_text.insert("0.0", f"❌ Error scanning folder:\n{str(e)}")
            self.status_var.set("❌ Error scanning folder")
        
        self.progress_bar.set(1.0)
        self.window.after(1000, lambda: self.progress_bar.set(0))
        self.update_ui_state()
    
    def process_files(self):
        if self.processing:
            return
        
        # Validate inputs
        if not self.input_folder.get() or not os.path.exists(self.input_folder.get()):
            messagebox.showerror("Error", "Please select a valid input folder.")
            return
        
        if not self.output_file.get():
            messagebox.showerror("Error", "Please specify an output file.")
            return
        
        if not self.xml_files:
            messagebox.showerror("Error", "Please scan the folder first to find XML files.")
            return
        
        # Confirm processing
        result = messagebox.askyesno(
            "Confirm Processing",
            f"Ready to process {len(self.xml_files)} XML files.\n\n"
            f"Export type: {self.export_type.get().title()}\n"
            f"Output file: {os.path.basename(self.output_file.get())}\n\n"
            "Continue with processing?"
        )
        
        if not result:
            return
        
        # Start processing
        self.processing = True
        self.process_button.configure(text="⏳ Processing...", state="disabled")
        self.scan_button.configure(state="disabled")
        
        thread = threading.Thread(target=self._process_files_thread)
        thread.daemon = True
        thread.start()
    
    def show_custom_params_dialog(self):
        """Show dialog for selecting custom parameters and phases"""
        if not self.available_parameters:
            messagebox.showwarning(
                "No Parameters Available",
                "Please scan the input folder first to detect available parameters."
            )
            return
        
        # Create custom parameters selection window
        custom_window = ctk.CTkToplevel(self.window)
        custom_window.title("Custom Parameters Selection")
        custom_window.geometry("800x600")
        custom_window.transient(self.window)
        custom_window.grab_set()
        
        # Main frame with scrollable area
        main_frame = ctk.CTkFrame(custom_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Select Parameters and Phases to Export",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = ctk.CTkLabel(
            main_frame,
            text="Choose which parameters to export and select the measurement phases for each parameter.",
            font=ctk.CTkFont(size=12),
            wraplength=700
        )
        instructions.pack(pady=(0, 15))
        
        # Scrollable frame for parameters
        scroll_frame = ctk.CTkScrollableFrame(main_frame, height=400)
        scroll_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Store checkboxes and phase selections
        param_vars = {}
        phase_vars = {}
        
        for param_name in self.available_parameters:
            # Parameter frame
            param_frame = ctk.CTkFrame(scroll_frame)
            param_frame.pack(fill="x", padx=5, pady=5)
            
            # Parameter checkbox
            param_vars[param_name] = ctk.BooleanVar()
            if param_name in self.custom_parameters:
                param_vars[param_name].set(True)
            
            param_checkbox = ctk.CTkCheckBox(
                param_frame,
                text=param_name,
                variable=param_vars[param_name],
                font=ctk.CTkFont(size=14, weight="bold")
            )
            param_checkbox.pack(anchor="w", padx=10, pady=(10, 5))
            
            # Phases frame
            phases_frame = ctk.CTkFrame(param_frame)
            phases_frame.pack(fill="x", padx=20, pady=(0, 10))
            
            phases_label = ctk.CTkLabel(phases_frame, text="Phases to export:")
            phases_label.pack(anchor="w", padx=10, pady=(10, 5))
            
            # Phase checkboxes in a grid
            phase_vars[param_name] = {}
            phases_container = ctk.CTkFrame(phases_frame)
            phases_container.pack(fill="x", padx=10, pady=(0, 10))
            
            for i, phase in enumerate(self.available_phases):
                phase_vars[param_name][phase] = ctk.BooleanVar()
                if param_name in self.custom_parameters and phase in self.custom_parameters[param_name]:
                    phase_vars[param_name][phase].set(True)
                elif param_name not in self.custom_parameters and phase == "Max":
                    # Default to Max phase for new parameters
                    phase_vars[param_name][phase].set(True)
                
                phase_cb = ctk.CTkCheckBox(
                    phases_container,
                    text=phase,
                    variable=phase_vars[param_name][phase],
                    width=80
                )
                phase_cb.grid(row=i//4, column=i%4, padx=5, pady=2, sticky="w")
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        # Quick selection buttons
        quick_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        quick_frame.pack(side="left")
        
        def select_all_max():
            """Select all parameters with Max phase only"""
            for param in self.available_parameters:
                param_vars[param].set(True)
                for phase in self.available_phases:
                    phase_vars[param][phase].set(phase == "Max")
        
        def select_key_params():
            """Select the standard 15 key parameters"""
            key_params = ["t", "Speed", "Pace", "VO2", "VO2/kg", "VCO2", "METS", "RQ", "VE", "Rf", "HR", "VO2/HR"]
            for param in self.available_parameters:
                if param in key_params:
                    param_vars[param].set(True)
                    for phase in self.available_phases:
                        if param == "VO2/kg":
                            phase_vars[param][phase].set(phase in ["MFO", "AT", "RC", "Max"])
                        else:
                            phase_vars[param][phase].set(phase == "Max")
                else:
                    param_vars[param].set(False)
        
        def clear_all():
            """Clear all selections"""
            for param in self.available_parameters:
                param_vars[param].set(False)
                for phase in self.available_phases:
                    phase_vars[param][phase].set(False)
        
        quick_all_button = ctk.CTkButton(quick_frame, text="All (Max)", command=select_all_max, width=100)
        quick_all_button.pack(side="left", padx=(0, 5))
        
        quick_key_button = ctk.CTkButton(quick_frame, text="Key 15", command=select_key_params, width=100)
        quick_key_button.pack(side="left", padx=5)
        
        quick_clear_button = ctk.CTkButton(quick_frame, text="Clear All", command=clear_all, width=100)
        quick_clear_button.pack(side="left", padx=5)
        
        # Action buttons
        action_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        action_frame.pack(side="right")
        
        def save_selection():
            # Save the custom parameters selection
            self.custom_parameters = {}
            selected_count = 0
            
            for param_name in self.available_parameters:
                if param_vars[param_name].get():
                    selected_phases = []
                    for phase in self.available_phases:
                        if phase_vars[param_name][phase].get():
                            selected_phases.append(phase)
                    
                    if selected_phases:  # Only add if phases are selected
                        self.custom_parameters[param_name] = selected_phases
                        selected_count += 1
            
            if not self.custom_parameters:
                messagebox.showwarning(
                    "No Selection",
                    "Please select at least one parameter with at least one phase."
                )
                return
            
            custom_window.destroy()
            
            # Update description
            param_count = len(self.custom_parameters)
            phase_count = sum(len(phases) for phases in self.custom_parameters.values())
            description = f"⚙️ Custom Parameters: {param_count} parameters with {phase_count} total phases selected. Tailored dataset for specialized analysis."
            self.description_label.configure(text=description)
        
        def cancel_selection():
            custom_window.destroy()
        
        save_button = ctk.CTkButton(action_frame, text="✅ Save Selection", command=save_selection, width=120)
        save_button.pack(side="right", padx=(5, 0))
        
        cancel_button = ctk.CTkButton(action_frame, text="❌ Cancel", command=cancel_selection, width=100)
        cancel_button.pack(side="right")
    
    def _process_files_thread(self):
        try:
            # Initialize
            self.window.after(0, lambda: self.status_var.set("🔧 Initializing processing..."))
            self.window.after(0, lambda: self.progress_bar.set(0.1))
            
            # Get export type and create output filename
            export_type = self.export_type.get()
            output_filename = "converted_data"
            
            if export_type == "selected":
                output_filename += "_selected_parameters"
            elif export_type == "max":
                output_filename += "_max_only"
            elif export_type == "complete":
                output_filename += "_complete"
            elif export_type == "custom":
                output_filename += "_custom_parameters"
            
            output_filename += ".xlsx"
            output_path = os.path.join(os.path.dirname(self.output_file.get()), output_filename)
            
            # Initialize components
            self.window.after(0, lambda: self.status_var.set("📖 Extracting data from XML files..."))
            self.window.after(0, lambda: self.progress_bar.set(0.3))
            
            reader = XmlDataReader(self.input_folder.get())
            extracted_data = reader.extract_id_and_parameters()
            
            if not extracted_data:
                self.window.after(0, lambda: messagebox.showerror(
                    "Error", 
                    "No data could be extracted from XML files.\n\n"
                    "Please check that the XML files contain valid COSMED data."
                ))
                return
            
            # Create exporter and export data
            self.window.after(0, lambda: self.status_var.set("📊 Creating Excel file..."))
            self.window.after(0, lambda: self.progress_bar.set(0.6))
            
            exporter = ExcelExporter(output_path)
            
            # Handle different export types
            if export_type == "custom":
                if not self.custom_parameters:
                    self.window.after(0, messagebox.showerror(
                        "Error",
                        "No custom parameters selected.\n\n"
                        "Please configure custom parameters first by clicking the 'Select Parameters' button."
                    ))
                    return
                
                # Export with custom parameters
                self.window.after(0, self.status_var.set("💾 Exporting custom parameters to Excel..."))
                self.window.after(0, self.progress_bar.set(0.8))

                success = exporter.export_custom_parameters(extracted_data, self.custom_parameters)
                
                if not success:
                    self.window.after(0, messagebox.showerror(
                        "Error",
                        "Failed to export custom parameters.\n\n"
                        "Please check the error logs for details."
                    ))
                    return      
            else:
                # Standard export
                self.window.after(0, self.status_var.set(f"💾 Exporting {export_type} data to Excel..."))
                self.window.after(0, self.progress_bar.set(0.8))
                
                if export_type == "selected":
                    exporter.export_selected_parameters(extracted_data)
                elif export_type == "max":
                    exporter.export_max_values_only(extracted_data)
                elif export_type == "complete":
                    exporter.export_extracted_xml_data(extracted_data)
            
            # Complete
            self.window.after(0, self.progress_bar.set(1.0))
            self.window.after(0, self.status_var.set(f"✅ Successfully exported {len(extracted_data)} subjects to Excel"))
            
            # Success message
            export_description = export_type.title()
            if export_type == "custom":
                param_count = len(self.custom_parameters)
                phase_count = sum(len(phases) for phases in self.custom_parameters.values())
                export_description = f"Custom ({param_count} parameters, {phase_count} phases)"
            
            success_msg = (
                f"🎉 Conversion Completed Successfully!\n\n"
                f"📊 Processed: {len(extracted_data)} XML files\n"
                f"📁 Export type: {export_description}\n"
                f"💾 Output file: {os.path.basename(output_path)}\n"
                f"📍 Location: {os.path.dirname(output_path)}"
            )
            
            self.window.after(0, messagebox.showinfo("Success", success_msg))
            
            # Auto-open file if enabled
            if self.auto_open_var.get():
                try:
                    os.startfile(output_path)
                except:
                    pass  # Ignore if can't open
            
        except Exception as e:
            error_msg = f"❌ Processing Error\n\nAn error occurred during processing:\n\n{str(e)}"
            self.window.after(0, messagebox.showerror("Error", error_msg))
            self.window.after(0, self.status_var.set("❌ Processing failed"))
            
        finally:
            # Reset UI
            self.processing = False
            self.window.after(0, lambda: self.process_button.configure(text="⚡ Convert to Excel", state="normal"))
            self.window.after(0, lambda: self.scan_button.configure(state="normal"))
            self.window.after(0, self.update_ui_state)
    
    def clear_all(self):
        self.input_folder.set("")
        self.output_file.set("")
        self.file_list_text.delete("0.0", "end")
        self.xml_files = []
        self.progress_bar.set(0)
        self.status_var.set("Ready to process XML files")
        self.file_count_label.configure(text="No files scanned yet")
        self.update_ui_state()
    
    def update_ui_state(self):
        has_input = bool(self.input_folder.get() and os.path.exists(self.input_folder.get()))
        has_output = bool(self.output_file.get())
        has_files = bool(self.xml_files)
        
        if has_input and has_output and has_files and not self.processing:
            self.process_button.configure(state="normal", fg_color=["#3B8ED0", "#1F6AA5"])
        else:
            self.process_button.configure(state="disabled", fg_color=("gray70", "gray30"))
    
    def change_appearance_mode(self, new_mode):
        ctk.set_appearance_mode(new_mode)
    
    def show_help(self):
        help_window = ctk.CTkToplevel(self.window)
        help_window.title("Help - COSMED Converter")
        help_window.geometry("700x500")
        help_window.transient(self.window)
        
        help_text = ctk.CTkTextbox(help_window, font=ctk.CTkFont(size=12))
        help_text.pack(fill="both", expand=True, padx=20, pady=20)
        
        help_content = """
📖 COSMED XML Data Converter - Help Guide

🚀 GETTING STARTED:
1. Select input folder containing COSMED XML files
2. Choose export type (Selected, Max, or Complete)
3. Specify output Excel file location
4. Click "Scan Folder" to find XML files
5. Click "Convert to Excel" to process

📊 EXPORT TYPES:

Selected Parameters:
• 15 key cardiopulmonary parameters
• Includes VO2/kg at MFO, AT, RC, and Max phases
• Perfect for focused clinical analysis

Max Values Only:
• Maximum values for all parameters
• Simplified dataset for peak performance analysis
• Quick overview of subject capabilities

Complete Dataset:
• All measurement phases (Rest, Warmup, MFO, AT, RC, Max, etc.)
• Comprehensive data for detailed research
• Includes predicted values and classifications

🔧 FEATURES:
• Batch processing of multiple XML files
• Automatic file scanning and validation
• Progress tracking and status updates
• Auto-open result file option
• Dark/Light theme support
• Error handling and validation

💡 TIPS:
• Use absolute paths for best results
• Ensure XML files contain valid COSMED data
• Close Excel files before overwriting
• Use "Scan Folder" to verify file detection
• Check the file list for processing confirmation

❗ TROUBLESHOOTING:
• If no files found, check file extensions (.xml)
• Ensure you have read permissions on folders
• Verify COSMED XML file format compatibility
• Check output folder write permissions

🏥 PERFECT FOR:
• Clinical researchers
• Exercise physiologists
• Sports scientists
• COSMED equipment users

For more information, visit the GitHub repository or contact support.
"""
        
        help_text.insert("0.0", help_content)
        help_text.configure(state="disabled")
    
    def show_about(self):
        messagebox.showinfo(
            "About COSMED Converter",
            "🫁 COSMED XML Data Converter v2.0\n\n"
            "A modern GUI application for converting COSMED cardiopulmonary exercise test (CPET) data from XML files to Excel spreadsheets.\n\n"
            "✨ Features:\n"
            "• Three export formats (Selected, Max, Complete)\n"
            "• Modern dark/light theme interface\n"
            "• Batch processing of multiple XML files\n"
            "• Automatic data extraction and formatting\n"
            "• Professional Excel output with proper headers\n"
            "• Progress tracking and error handling\n\n"
            "🏥 Perfect for clinical researchers, exercise physiologists, and sports scientists working with COSMED CPET equipment.\n\n"
            "Built with ❤️ from 🇩🇪\n"
            "© 2025"
        )
    
    def open_github(self):
        url: str = "https://github.com/Ganzosupremo/OmniaCosmedDataCoverter"
        webbrowser.open(url)

    def run(self):
        self.window.mainloop()

def main():
    app = AdvancedCosmedGUI()
    app.run()

if __name__ == "__main__":
    main()
