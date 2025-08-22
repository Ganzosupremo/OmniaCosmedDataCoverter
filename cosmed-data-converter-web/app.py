import streamlit as st
import os
import tempfile
import pandas as pd

from modules import XmlDataReader, ExcelExporter, CSSLoader

# CSS Loading function (embedded for simplicity)
def load_css():
    """Load external CSS file"""
    try:
        css_path = os.path.join(os.path.dirname(__file__), 'assets', 'styles.css')
        CSSLoader.load_css(css_path)
    except Exception as e:
        st.error(f"Could not load CSS: {e}")


def select_key_parameters():
    """Select the standard 15 key parameters with appropriate phases"""
    key_params = [
        't', 'Speed', 'Pace', 'VO2', 'VO2/kg', 'VCO2', 
        'METS', 'RQ', 'VE', 'Rf', 'HR', 'VO2/HR', 
        'P Syst', 'P Diast', 'HRR'
    ]
    
    st.session_state.custom_parameters = {}
    
    for param in key_params:
        if param in st.session_state.available_parameters:
            # Use smart defaults based on parameter type
            if param == 'VO2/kg':
                st.session_state.custom_parameters[param] = ['MFO', 'AT', 'RC', 'Max']
            elif param in ['HRR', 'P Syst', 'P Diast']:
                # These parameters typically have their primary data in the 'Value' field
                st.session_state.custom_parameters[param] = ['Value']
            else:
                # Most other parameters use Max phase
                st.session_state.custom_parameters[param] = ['Max']

def scan_parameters_from_files(uploaded_files):
    """Scan uploaded files to detect available parameters"""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save files temporarily
            for file in uploaded_files:
                file_path = os.path.join(temp_dir, file.name)
                with open(file_path, "wb") as f:
                    f.write(file.read())
                file.seek(0)  # Reset file pointer
            
            # Extract parameters from sample files
            reader = XmlDataReader(temp_dir)
            sample_data = reader.extract_id_and_parameters()
            
            if sample_data:
                params = set()
                for file_data in sample_data[:3]:  # Sample first few files
                    for param in file_data.get('parameters', []):
                        if param.get('Name'):
                            params.add(param['Name'])
                
                st.session_state.available_parameters = sorted(list(params))
                return True
            else:
                st.session_state.available_parameters = []
                return False
                
    except Exception as e:
        st.error(f"Error scanning parameters: {str(e)}")
        st.session_state.available_parameters = []
        return False

# Page configuration
st.set_page_config(
    page_title="COSMED XML Converter",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS styles
load_css()

# Initialize session state
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'file_count' not in st.session_state:
    st.session_state.file_count = 0
if 'available_parameters' not in st.session_state:
    st.session_state.available_parameters = []
if 'custom_parameters' not in st.session_state:
    st.session_state.custom_parameters = {}
if 'uploaded_files_data' not in st.session_state:
    st.session_state.uploaded_files_data = None

def main():
    # Header
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem;">🫁 COSMED XML Converter</h1>
            <p style="font-size: 1.2rem; color: var(--text-secondary); margin-bottom: 2rem;">
                Professional cardiopulmonary exercise test data conversion tool
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar configuration
    create_sidebar()
    
    # Main content
    create_main_content()
    
    # Footer
    create_footer()

def create_sidebar():
    """Create sidebar with settings and options"""
    with st.sidebar:
        st.header("⚙️ Export Settings")
        
        # Export type selection
        export_type = st.radio(
            "Choose Export Type:",
            ["selected", "max", "complete", "custom"],
            format_func=lambda x: {
                "selected": "📊 Selected Parameters",
                "max": "📈 Max Values Only", 
                "complete": "📋 Complete Dataset",
                "custom": "⚙️ Custom Parameters"
            }[x],
            help="Select what data to export from the XML files"
        )
        
        # Store in session state
        st.session_state.export_type = export_type
        
        # Show description based on export type
        descriptions = {
            "selected": "Exports 15 key cardiopulmonary parameters including VO2/kg at MFO, AT, RC, and Max phases.",
            "max": "Exports maximum values for all parameters. Simplified dataset for peak performance analysis.",
            "complete": "Exports all measurement phases. Comprehensive data for detailed research.",
            "custom": "Choose specific parameters and phases to export."
        }
        
        st.info(descriptions[export_type])
        
        # Additional settings
        st.header("🔧 Additional Settings")
        
        auto_download = st.checkbox(
            "Auto-download result", 
            value=True,
            help="Automatically download the Excel file after processing"
        )
        st.session_state.auto_download = auto_download
        
        include_metadata = st.checkbox(
            "Include metadata sheet", 
            value=True,
            help="Add a sheet with processing information and file details"
        )
        st.session_state.include_metadata = include_metadata
        
        # Custom parameters (if selected)
        if export_type == "custom":
            st.header("📋 Custom Parameters")
            
            if st.session_state.available_parameters:
                st.success(f"✅ Found {len(st.session_state.available_parameters)} parameters")
                
                # Quick selection buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Select Key 15", use_container_width=True, help="Select the standard 15 clinical parameters"):
                        select_key_parameters()
                        st.rerun()
                
                with col2:
                    if st.button("Clear All", use_container_width=True, help="Clear all parameter selections"):
                        st.session_state.custom_parameters = {}
                        st.rerun()
                
                # Parameter selection
                st.subheader("Select Parameters:")
                
                # Phase explanation
                with st.expander("ℹ️ Understanding Measurement Phases", expanded=False):
                    st.markdown("""
                    **Common Measurement Phases:**
                    - **Value**: Primary measurement value (used for parameters like HRR, blood pressure)
                    - **Rest**: Baseline measurements before exercise
                    - **Warmup**: Initial low-intensity exercise phase
                    - **MFO**: Maximum Fat Oxidation point
                    - **AT**: Anaerobic Threshold (VT1)
                    - **RC**: Respiratory Compensation Point (VT2)
                    - **Max**: Peak exercise values
                    - **Pred**: Predicted values based on demographics
                    - **PercPred**: Percentage of predicted values
                    - **Normal**: Normal reference ranges
                    - **Class**: Classification categories
                    """)
                
                # Available phases (including Value which some parameters use as primary data)
                available_phases = ['Value', 'Rest', 'Warmup', 'MFO', 'AT', 'RC', 'Max', 'Pred', 'PercPred', 'Normal', 'Class']
                
                # Create parameter selection interface
                for param in st.session_state.available_parameters[:15]:  # Limit to first 15 for UI
                    with st.expander(f"📊 {param}", expanded=param in st.session_state.custom_parameters):
                        
                        # Parameter checkbox
                        param_selected = st.checkbox(
                            f"Include {param}",
                            value=param in st.session_state.custom_parameters,
                            key=f"param_{param}"
                        )
                        
                        if param_selected:
                            # Phase selection
                            st.write("Select measurement phases:")
                            
                            # Smart default phases based on parameter type
                            default_phases = ['Max']  # Default fallback
                            
                            # Parameters that typically use 'Value' field
                            if param in ['HRR', 'P Syst', 'P Diast']:
                                default_phases = ['Value']
                            # VO2/kg gets multiple phases for comprehensive analysis
                            elif param == 'VO2/kg':
                                default_phases = ['MFO', 'AT', 'RC', 'Max']
                            # Metabolic and respiratory parameters often have meaningful data across phases
                            elif param in ['VO2', 'VCO2', 'METS', 'RQ', 'VE', 'Rf']:
                                default_phases = ['Max']  # Can be expanded to ['MFO', 'AT', 'RC', 'Max'] if desired
                            # Time and performance parameters
                            elif param in ['t', 'Speed', 'Pace']:
                                default_phases = ['Max']
                            # HR typically measured at multiple phases
                            elif param == 'HR':
                                default_phases = ['Max']  # Can be expanded to ['AT', 'RC', 'Max'] if desired
                            
                            current_phases = st.session_state.custom_parameters.get(param, default_phases)
                            
                            selected_phases = []
                            
                            # Group phases for better layout
                            primary_phases = ['Value', 'Rest', 'Warmup', 'MFO', 'AT', 'RC', 'Max']
                            secondary_phases = ['Pred', 'PercPred', 'Normal', 'Class']
                            
                            # Primary phases (more commonly used)
                            st.write("**Primary Phases:**")
                            phase_cols = st.columns(4)
                            for i, phase in enumerate(primary_phases):
                                with phase_cols[i % 4]:
                                    if st.checkbox(
                                        phase,
                                        value=phase in current_phases,
                                        key=f"phase_{param}_{phase}",
                                        help=f"Include {phase} phase data for {param}"
                                    ):
                                        selected_phases.append(phase)
                            
                            # Secondary phases (less commonly used)
                            with st.expander("📊 Additional Phases", expanded=False):
                                phase_cols2 = st.columns(4)
                                for i, phase in enumerate(secondary_phases):
                                    with phase_cols2[i % 4]:
                                        if st.checkbox(
                                            phase,
                                            value=phase in current_phases,
                                            key=f"phase_{param}_{phase}",
                                            help=f"Include {phase} data for {param}"
                                        ):
                                            selected_phases.append(phase)
                            
                            if selected_phases:
                                st.session_state.custom_parameters[param] = selected_phases
                            elif param in st.session_state.custom_parameters:
                                del st.session_state.custom_parameters[param]
                        
                        elif param in st.session_state.custom_parameters:
                            del st.session_state.custom_parameters[param]
                
                # Show selection summary
                if st.session_state.custom_parameters:
                    param_count = len(st.session_state.custom_parameters)
                    phase_count = sum(len(phases) for phases in st.session_state.custom_parameters.values())
                    st.success(f"📊 Selected: {param_count} parameters, {phase_count} total phases")
                else:
                    st.info("🔍 Select parameters above to customize your export")
            else:
                st.info("📤 Upload and scan files first to detect available parameters")
        
        # Help section
        st.header("📖 Help & Info")
        
        if st.button("❓ How to Use", use_container_width=True):
            show_help_dialog()
        
        if st.button("ℹ️ About", use_container_width=True):
            show_about_dialog()

def create_main_content():
    """Create main content area"""
    st.header("📁 File Upload & Processing")

    uploaded_files = st.file_uploader(
        "Choose COSMED XML files",
        type=['xml'],
        accept_multiple_files=True,
        help="Select one or more XML files exported from COSMED software"
    )
    
    if uploaded_files:
        st.session_state.file_count = len(uploaded_files)
        st.session_state.uploaded_files_data = uploaded_files
        
        # Display uploaded files
        with st.expander(f"📄 Uploaded Files ({len(uploaded_files)})", expanded=False):
            for i, file in enumerate(uploaded_files, 1):
                file_size = len(file.read()) / 1024  # KB
                file.seek(0)  # Reset file pointer
                st.write(f"{i}. **{file.name}** ({file_size:.1f} KB)")
        
        # Scan parameters button
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🔍 Scan Parameters", use_container_width=True, help="Scan files to detect available parameters"):
                with st.spinner("Scanning parameters..."):
                    if scan_parameters_from_files(uploaded_files):
                        st.success(f"✅ Found {len(st.session_state.available_parameters)} parameters")
                        st.rerun()
                    else:
                        st.error("❌ Could not detect parameters from files")
        
        # File validation
        valid_files = validate_files(uploaded_files)
        
        if valid_files:
            # Show available parameters if scanned
            if st.session_state.available_parameters:
                with st.expander(f"📊 Available Parameters ({len(st.session_state.available_parameters)})", expanded=False):
                    cols = st.columns(3)
                    for i, param in enumerate(st.session_state.available_parameters):
                        with cols[i % 3]:
                            st.write(f"• {param}")
            
            with col2:
                # Check if custom export is selected and parameters are configured
                export_type = st.session_state.export_type
                can_process = True
                
                if export_type == "custom":
                    if not st.session_state.custom_parameters:
                        can_process = False
                        st.error("❌ Please select custom parameters first")
                
                if st.button(
                    "⚡ Convert to Excel", 
                    type="primary", 
                    use_container_width=True,
                    disabled=not can_process,
                    help="Convert XML files to Excel format"
                ):
                    process_files(valid_files)
        else:
            st.error("❌ No valid XML files found. Please check your file selection.")
    
    # Results section
    if st.session_state.processed_data is not None:
        show_results()

def validate_files(uploaded_files):
    """Validate uploaded XML files"""
    valid_files = []
    
    for file in uploaded_files:
        try:
            content = file.read().decode('utf-8')
            file.seek(0)  # Reset file pointer
            
            # Basic XML validation
            if '<' in content and '>' in content:
                valid_files.append(file)
            else:
                st.warning(f"⚠️ {file.name} doesn't appear to be a valid XML file")
                
        except Exception as e:
            st.warning(f"⚠️ Error reading {file.name}: {str(e)}")
            file.seek(0)  # Reset file pointer
    
    return valid_files

def process_files(uploaded_files):
    """Process the uploaded XML files"""
    
    try:
        with st.spinner("🔄 Processing XML files... This may take a moment."):
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save uploaded files
                xml_paths = []
                for i, file in enumerate(uploaded_files):
                    progress_bar.progress((i + 1) / len(uploaded_files) * 0.3)
                    status_text.text(f"Saving file {i+1}/{len(uploaded_files)}: {file.name}")
                    
                    file_path = os.path.join(temp_dir, file.name)
                    with open(file_path, "wb") as f:
                        f.write(file.read())
                    xml_paths.append(file_path)
                
                status_text.markdown('<p class="loading-text">🔍 Extracting data from XML files...</p>', unsafe_allow_html=True)
                progress_bar.progress(0.4)
                
                # Process files using existing classes
                reader = XmlDataReader(temp_dir)
                extracted_data = reader.extract_id_and_parameters()
                
                if extracted_data:
                    progress_bar.progress(0.7)
                    status_text.markdown(f'<p class="loading-text">📊 Processing {len(extracted_data)} records...</p>', unsafe_allow_html=True)

                    # Create Excel file
                    export_type = st.session_state.export_type
                    
                    if export_type == "custom":
                        output_filename = "cosmed_custom_data.xlsx"
                    else:
                        output_filename = f"cosmed_{export_type}_data.xlsx"
                    
                    output_path = os.path.join(temp_dir, output_filename)
                    exporter = ExcelExporter(output_path)
                    
                    # Export based on type
                    if export_type == "selected":
                        exporter.export_selected_parameters(extracted_data)
                    elif export_type == "max":
                        exporter.export_max_values_only(extracted_data)
                    elif export_type == "complete":
                        exporter.export_extracted_xml_data(extracted_data)
                    elif export_type == "custom":
                        if st.session_state.custom_parameters:
                            success = exporter.export_custom_parameters(extracted_data, st.session_state.custom_parameters)
                            if not success:
                                st.error("❌ Failed to export custom parameters")
                                return
                        else:
                            st.error("❌ No custom parameters selected")
                            return
                    
                    progress_bar.progress(0.9)
                    status_text.markdown('<p class="loading-text">📦 Finalizing export...</p>', unsafe_allow_html=True)
                    
                    # Read the created Excel file
                    with open(output_path, "rb") as excel_file:
                        excel_data = excel_file.read()
                    
                    # Store results in session state
                    custom_summary = None
                    if export_type == "custom" and st.session_state.custom_parameters:
                        param_count = len(st.session_state.custom_parameters)
                        phase_count = sum(len(phases) for phases in st.session_state.custom_parameters.values())
                        custom_summary = f"{param_count} parameters, {phase_count} phases"
                    
                    st.session_state.processed_data = {
                        'excel_data': excel_data,
                        'file_count': len(extracted_data),
                        'export_type': export_type,
                        'filename': output_filename,
                        'custom_summary': custom_summary
                    }
                    
                    progress_bar.progress(1.0)
                    status_text.text("✅ Processing complete!")
                    
                    # Clear the progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.success(f"🎉 Successfully processed {len(extracted_data)} XML files!")
                    st.rerun()  # Refresh to show results
                    
                else:
                    st.error("❌ No valid COSMED data found in the uploaded XML files.")
                    
    except Exception as e:
        st.error(f"❌ Error processing files: {str(e)}")
        st.error("Please check that your XML files are valid COSMED exports.")

def show_results():
    """Display processing results and download options"""
    st.markdown("""
        <div class="custom-card">
            <h2 style="margin-top: 0;">📊 Processing Results</h2>
        </div>
    """, unsafe_allow_html=True)
    
    data = st.session_state.processed_data
    
    # Results summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Files Processed",
            value=data['file_count'],
            delta=f"{data['file_count']} records"
        )
    
    with col2:
        export_display = data['export_type'].title()
        if data['export_type'] == 'custom' and data.get('custom_summary'):
            export_display = f"Custom ({data['custom_summary']})"
        
        st.metric(
            label="Export Type",
            value=export_display,
            delta="✅ Ready"
        )
    
    with col3:
        file_size = len(data['excel_data']) / 1024  # KB
        st.metric(
            label="File Size",
            value=f"{file_size:.1f} KB",
            delta="Excel format"
        )
    
    # Download section
    st.subheader("📥 Download Your Data")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.download_button(
            label="📥 Download Excel File",
            data=data['excel_data'],
            file_name=data['filename'],
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        if st.button("🔄 Process New Files", use_container_width=True):
            # Clear session state and rerun
            st.session_state.processed_data = None
            st.session_state.file_count = 0
            st.session_state.available_parameters = []
            st.session_state.custom_parameters = {}
            st.session_state.uploaded_files_data = None
            st.rerun()
    
    # Show custom parameters summary if applicable
    if data['export_type'] == 'custom' and st.session_state.custom_parameters:
        st.subheader("⚙️ Custom Parameters Used")
        
        with st.expander("View Selected Parameters", expanded=False):
            for param_name, phases in st.session_state.custom_parameters.items():
                st.write(f"**{param_name}**: {', '.join(phases)}")
    
    # Data preview section
    with st.expander("👁️ Preview Excel Data", expanded=False):
        try:
            # Create a temporary preview by reading the Excel data
            import io
            preview_df = pd.read_excel(io.BytesIO(data['excel_data']), nrows=5)
            
            st.write("**First 5 rows of your exported data:**")
            st.dataframe(preview_df, use_container_width=True)
            
            st.info(f"📊 Full dataset contains {data['file_count']} rows and {len(preview_df.columns)} columns")
            
        except Exception as e:
            st.warning(f"Could not preview data: {str(e)}")

def show_help_dialog():
    """Show help information"""
    st.info("""
    ## 📖 How to Use COSMED XML Converter
    
    ### Step 1: Upload Files
    - Click "Browse files" or drag & drop XML files
    - Select one or more COSMED XML export files
    - Supported format: XML files from COSMED software
    
    ### Step 2: Scan Parameters (Optional)
    - Click "🔍 Scan Parameters" to detect available parameters
    - This enables custom parameter selection
    - View available parameters in the expandable section
    
    ### Step 3: Choose Export Type
    - **Selected Parameters**: 15 key clinical parameters (VO2/kg, HR, etc.)
    - **Max Values Only**: Peak performance values from each parameter
    - **Complete Dataset**: All measurement phases (Rest, Warmup, MFO, AT, RC, Max, etc.)
    - **Custom Parameters**: Choose specific parameters and measurement phases
    
    ### Step 4: Configure Custom Parameters (if selected)
    - Use sidebar to select specific parameters
    - Choose measurement phases for each parameter (MFO, AT, RC, Max, etc.)
    - Use "Select Key 15" for quick selection of standard clinical parameters
    - VO2/kg automatically includes multiple phases (MFO, AT, RC, Max)
    
    ### Step 5: Process & Download
    - Click "Convert to Excel" to process files
    - Preview the results before downloading
    - Download the generated Excel file
    - Open in Excel, LibreOffice, or similar software
    
    ### Supported Data
    - VO2, VCO2, ventilatory parameters (VE, Rf)
    - Heart rate and metabolic data (HR, METS, RQ)
    - Exercise phases: Rest, Warmup, MFO, AT, RC, Max
    - Patient demographics and test information
    - Blood pressure data (systolic/diastolic)
    """)
    
    st.success("""
    💡 **Pro Tips:**
    - Custom parameters allow you to create focused datasets for specific research
    - The "Key 15" selection includes the most commonly used clinical parameters
    - Large datasets work best with "Max Values Only" for initial analysis
    - All processing happens locally in your browser - your data stays private
    """)

def show_about_dialog():
    """Show about information"""
    st.info("""
    ## ℹ️ About COSMED XML Converter
    
    **Version**: 2.1 (Streamlit Web Edition with Custom Parameters)
    
    **Purpose**: Convert COSMED cardiopulmonary exercise test data from XML format to Excel spreadsheets for easier analysis and reporting.
    
    **New Features**:
    - 🎯 **Custom Parameter Selection**: Choose exactly which parameters and phases to export
    - 🔍 **Smart Parameter Scanning**: Automatically detect available parameters from your files
    - 📊 **Data Preview**: See your data before downloading
    - ⚡ **Quick Presets**: "Key 15" selection for standard clinical parameters
    - 🧠 **Intelligent Phases**: VO2/kg automatically includes MFO, AT, RC, and Max phases
    
    **Core Features**:
    - 🌐 **Web-based interface** (no installation required)
    - 📁 **Multiple export formats** (Selected, Max, Complete, Custom)
    - 🔄 **Batch processing** of multiple files
    - ✅ **Automatic data validation**
    - 🖥️ **Cross-platform compatibility**
    - 🔒 **Privacy-focused** (all processing happens locally)
    
    **Supported COSMED Systems**:
    - Quark CPET
    - K5 series  
    - Fitmate Pro
    - Omnia
    - And other COSMED systems that export XML data
    
    **Technical Details**:
    - Built with Streamlit for the web interface
    - Uses pandas and openpyxl for Excel generation
    - Modular architecture for easy maintenance
    - Comprehensive error handling and logging
    
    **Developer**: Built for healthcare professionals, researchers, and clinicians working with cardiopulmonary exercise testing data.
    """)
    
    st.success("""
    🔬 **Perfect for Research**: Custom parameter selection makes it easy to create focused datasets for:
    - Metabolic studies (VO2, VCO2, RQ parameters)
    - Cardiovascular research (HR, blood pressure data)  
    - Exercise physiology (MFO, AT, RC, Max phases)
    - Clinical assessments (key diagnostic parameters)
    """)

def create_footer():
    """Create footer with additional information"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🔒 Privacy**: Files are processed locally and not stored on our servers.")
    
    with col2:
        st.markdown("**⚡ Performance**: Optimized for batch processing of multiple XML files.")
    
    with col3:
        st.markdown("**🌐 Compatible**: Works with all major COSMED software exports.")

if __name__ == "__main__":
    main()