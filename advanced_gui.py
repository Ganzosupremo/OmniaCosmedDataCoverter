import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
from xml_data_reader import XmlDataReader
from excel_exporter import ExcelExporter
import webbrowser

class AdvancedCosmedGUI:
    def __init__(self):
        # Set the appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.window = ctk.CTk()
        self.window.title("COSMED XML Data Converter")
        self.window.geometry("1000x800")
        self.window.minsize(900, 700)
        
        # Configure grid weights
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        # Variables
        self.input_folder = ctk.StringVar()
        self.output_file = ctk.StringVar()
        self.export_type = ctk.StringVar(value="selected")
        self.progress_var = ctk.DoubleVar()
        self.status_var = ctk.StringVar(value="Ready to process XML files")
        self.xml_files = []
        self.processing = False
        
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
            "complete": "📋 Complete Dataset: Exports all measurement phases (Rest, Warmup, MFO, AT, RC, Max, Predicted, etc.). Comprehensive data for detailed research and analysis."
        }
        return descriptions.get(export_type, "")
    
    def on_export_type_change(self):
        export_type = self.export_type.get()
        self.description_label.configure(text=self.get_export_description(export_type))
        
        # Update default filename if output is not set
        if not self.output_file.get() and self.input_folder.get():
            folder_name = os.path.basename(self.input_folder.get()) or "cosmed_data"
            default_names = {
                "selected": f"{folder_name}_selected_parameters.xlsx",
                "max": f"{folder_name}_max_values.xlsx",
                "complete": f"{folder_name}_complete_dataset.xlsx"
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
                # Display files
                self.file_list_text.insert("0.0", f"📁 Scanning Results\n{'='*50}\n")
                self.file_list_text.insert("end", f"Found {len(self.xml_files)} XML files:\n\n")
                
                for i, file_path in enumerate(self.xml_files, 1):
                    filename = os.path.basename(file_path)
                    rel_path = os.path.relpath(file_path, folder)
                    self.file_list_text.insert("end", f"{i:3d}. {filename}\n")
                    if rel_path != filename:  # Show subfolder if different
                        self.file_list_text.insert("end", f"     📂 {os.path.dirname(rel_path)}\n")
                
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
    
    def _process_files_thread(self):
        try:
            # Initialize
            self.window.after(0, lambda: self.status_var.set("🔧 Initializing XML reader..."))
            self.window.after(0, lambda: self.progress_bar.set(0.1))
            
            reader = XmlDataReader(self.input_folder.get())
            
            # Extract data
            self.window.after(0, lambda: self.status_var.set("📖 Extracting data from XML files..."))
            self.window.after(0, lambda: self.progress_bar.set(0.3))
            
            extracted_data = reader.extract_id_and_parameters()
            
            if not extracted_data:
                self.window.after(0, lambda: messagebox.showerror(
                    "Error", 
                    "No data could be extracted from XML files.\n\n"
                    "Please check that the XML files contain valid COSMED data."
                ))
                return
            
            # Create exporter
            self.window.after(0, lambda: self.status_var.set("📊 Creating Excel file..."))
            self.window.after(0, lambda: self.progress_bar.set(0.6))
            
            exporter = ExcelExporter(self.output_file.get())
            
            # Export data
            export_type = self.export_type.get()
            self.window.after(0, lambda: self.status_var.set(f"💾 Exporting {export_type} data to Excel..."))
            self.window.after(0, lambda: self.progress_bar.set(0.8))
            
            if export_type == "selected":
                exporter.export_selected_parameters(extracted_data)
            elif export_type == "max":
                exporter.export_max_values_only(extracted_data)
            elif export_type == "complete":
                exporter.export_extracted_xml_data(extracted_data)
            
            # Complete
            self.window.after(0, lambda: self.progress_bar.set(1.0))
            self.window.after(0, lambda: self.status_var.set(f"✅ Successfully exported {len(extracted_data)} subjects to Excel"))
            
            # Success message
            success_msg = (
                f"🎉 Conversion Completed Successfully!\n\n"
                f"📊 Processed: {len(extracted_data)} XML files\n"
                f"📁 Export type: {export_type.title()}\n"
                f"💾 Output file: {os.path.basename(self.output_file.get())}\n"
                f"📍 Location: {os.path.dirname(self.output_file.get())}"
            )
            
            self.window.after(0, lambda: messagebox.showinfo("Success", success_msg))
            
            # Auto-open file if enabled
            if self.auto_open_var.get():
                try:
                    os.startfile(self.output_file.get())
                except:
                    pass  # Ignore if can't open
            
        except Exception as e:
            error_msg = f"❌ Processing Error\n\nAn error occurred during processing:\n\n{str(e)}"
            self.window.after(0, lambda: messagebox.showerror("Error", error_msg))
            self.window.after(0, lambda: self.status_var.set("❌ Processing failed"))
            
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
