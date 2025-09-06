import streamlit as st
import os
import tempfile
import pandas as pd
from typing import Optional, List

from web_modules import XmlDataReader, ExcelExporter, CSSLoader, PhaseAnalyzer

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

    # Create tabs for different functionalities
    tab1, tab2 = st.tabs(["🔄 XML Converter", "📊 Phase Statistics"])
    
    with tab1:
        # Sidebar configuration for XML converter
        create_sidebar()
        
        # Main content for XML conversion
        create_main_content()
    
    with tab2:
        # Phase statistics analyzer
        create_phase_analyzer_content()
    
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
    
    **Version**: 2.2 (Streamlit Web Edition with Custom Parameters & Batch Analysis)
    
    **Purpose**: Convert COSMED cardiopulmonary exercise test data from XML format to Excel spreadsheets for easier analysis and reporting.
    
    **New Features**:
    - 🎯 **Custom Parameter Selection**: Choose exactly which parameters and phases to export
    - 🔍 **Smart Parameter Scanning**: Automatically detect available parameters from your files
    - 📊 **Data Preview**: See your data before downloading
    - ⚡ **Quick Presets**: "Key 15" selection for standard clinical parameters
    - 🧠 **Intelligent Phases**: VO2/kg automatically includes MFO, AT, RC, and Max phases
    - 📚 **Batch Phase Analysis**: Upload and analyze multiple data files simultaneously
    - 🔗 **Combined Analysis**: Merge multiple datasets for comprehensive statistics
    
    **Core Features**:
    - 🌐 **Web-based interface** (no installation required)
    - 📁 **Multiple export formats** (Selected, Max, Complete, Custom)
    - 🔄 **Batch processing** of multiple files
    - ✅ **Automatic data validation**
    - 🖥️ **Cross-platform compatibility**
    - 🔒 **Privacy-focused** (all processing happens locally)
    - 📈 **Phase Statistics Analysis** (single file or batch processing)
    
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

def create_phase_analyzer_content():
    """Create content for phase statistics analyzer"""
    st.markdown("""
        <div class="custom-card">
            <h2>📊 Phase Statistics Analyzer</h2>
            <p>Analyze exercise phase data and calculate comprehensive statistics (mean, standard deviation, max) for each phase occurrence.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for phase analyzer
    if 'phase_analysis_results' not in st.session_state:
        st.session_state.phase_analysis_results = None
    if 'batch_analysis_results' not in st.session_state:
        st.session_state.batch_analysis_results = None
    
    # Upload mode selection
    st.subheader("📁 Upload Mode")
    
    upload_mode = st.radio(
        "Choose upload mode:",
        ["single", "batch"],
        format_func=lambda x: {
            "single": "📄 Single File Analysis",
            "batch": "📚 Batch File Analysis"
        }[x],
        help="Single file: Analyze one file at a time. Batch: Upload and analyze multiple files together.",
        horizontal=True
    )
    
    if upload_mode == "single":
        create_single_file_analyzer()
    else:
        create_batch_file_analyzer()

def create_single_file_analyzer():
    """Create single file analyzer interface"""
    # File upload section
    st.subheader("📁 Upload Data File")
    
    uploaded_file = st.file_uploader(
        "Choose a data file (Excel or CSV)",
        type=['xlsx', 'xls', 'csv'],
        help="Upload an Excel or CSV file with a 'Phase' column and numeric data columns",
        key="phase_analyzer_upload"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.success(f"✅ File uploaded: **{uploaded_file.name}**")
        
        # Preview the data
        try:
            if uploaded_file.name.endswith('.csv'):
                preview_df = pd.read_csv(uploaded_file, nrows=5)
            else:
                preview_df = pd.read_excel(uploaded_file, nrows=5)
            
            with st.expander("👁️ Data Preview (First 5 rows)", expanded=False):
                st.dataframe(preview_df, use_container_width=True)
                st.info(f"📊 Columns detected: {list(preview_df.columns)}")
                
                # Check for Phase column
                if 'Phase' in preview_df.columns:
                    st.success("✅ 'Phase' column detected")
                    unique_phases = preview_df['Phase'].dropna().unique()
                    if len(unique_phases) > 0:
                        st.info(f"🔍 Sample phases found: {', '.join(map(str, unique_phases[:5]))}")
                else:
                    st.warning("⚠️ No 'Phase' column found. Please ensure your data has a column named 'Phase'.")
            
        except Exception as e:
            st.error(f"❌ Error previewing file: {str(e)}")
        
        # Analysis settings
        st.subheader("⚙️ Analysis Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            include_warnings = st.checkbox(
                "Show warnings", 
                value=True,
                help="Display warnings about data processing issues"
            )
        
        with col2:
            show_phase_details = st.checkbox(
                "Show phase details", 
                value=True,
                help="Display detailed information about detected phases"
            )
        
        # Process button
        if st.button("🔬 Analyze Phase Statistics", type="primary", use_container_width=True):
            analyze_phase_data(uploaded_file, include_warnings, show_phase_details)
    
    # Results section
    if st.session_state.phase_analysis_results is not None:
        display_phase_analysis_results()

def create_batch_file_analyzer():
    """Create batch file analyzer interface"""
    # File upload section
    st.subheader("📚 Upload Multiple Data Files")
    
    uploaded_files = st.file_uploader(
        "Choose data files (Excel or CSV)",
        type=['xlsx', 'xls', 'csv'],
        accept_multiple_files=True,
        help="Upload multiple Excel or CSV files with 'Phase' columns and numeric data columns",
        key="batch_phase_analyzer_upload"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} files uploaded")
        
        # Display uploaded files
        with st.expander(f"📄 Uploaded Files ({len(uploaded_files)})", expanded=False):
            for i, file in enumerate(uploaded_files, 1):
                file_size = len(file.read()) / 1024  # KB
                file.seek(0)  # Reset file pointer
                st.write(f"{i}. **{file.name}** ({file_size:.1f} KB)")
        
        # Batch preview
        st.subheader("👁️ Batch Preview")
        
        # Show preview of first few files
        preview_files = uploaded_files[:3]  # Preview first 3 files
        
        for i, file in enumerate(preview_files):
            try:
                file.seek(0)
                
                if file.name.endswith('.csv'):
                    preview_df = pd.read_csv(file, nrows=3)
                else:
                    preview_df = pd.read_excel(file, nrows=3)
                
                file.seek(0)  # Reset for later processing
                
                with st.expander(f"📊 Preview: {file.name}", expanded=False):
                    st.dataframe(preview_df, use_container_width=True)
                    
                    # Check for Phase column
                    if 'Phase' in preview_df.columns:
                        st.success("✅ 'Phase' column detected")
                        unique_phases = preview_df['Phase'].dropna().unique()
                        if len(unique_phases) > 0:
                            st.info(f"🔍 Sample phases: {', '.join(map(str, unique_phases))}")
                    else:
                        st.warning("⚠️ No 'Phase' column found in this file")
                        
            except Exception as e:
                st.error(f"❌ Error previewing {file.name}: {str(e)}")
        
        if len(uploaded_files) > 3:
            st.info(f"📋 Showing preview for first 3 files. {len(uploaded_files) - 3} additional files will be processed.")
        
        # Batch analysis settings
        st.subheader("⚙️ Batch Analysis Settings")
        
        # Parameter selection section
        st.write("**Parameter Selection:**")
        
        # First scan files to get available parameters
        available_params = scan_parameters_from_files(uploaded_files)
        
        if available_params:
            # Parameter selection method
            param_selection_method = st.radio(
                "Choose parameter selection method:",
                ["all", "custom"],
                format_func=lambda x: {
                    "all": "📊 All Available Parameters",
                    "custom": "🎯 Custom Parameter Selection"
                }[x],
                help="Select whether to use all parameters or choose specific ones",
                horizontal=True,
                key="batch_param_method"
            )
            
            selected_parameters = None
            if param_selection_method == "custom":
                selected_parameters = st.multiselect(
                    "Select parameters for analysis:",
                    options=available_params,
                    default=available_params[:10] if len(available_params) > 10 else available_params,
                    help="Choose specific parameters to include in batch analysis",
                    key="batch_param_selection"
                )
                
                if not selected_parameters:
                    st.warning("⚠️ No parameters selected. All available parameters will be used.")
                    selected_parameters = None
        else:
            st.warning("⚠️ Could not detect parameters from uploaded files. All detected parameters will be used during processing.")
            selected_parameters = None
        
        # Additional settings
        col1, col2 = st.columns(2)
        
        with col1:
            include_warnings = st.checkbox(
                "Show processing warnings", 
                value=True,
                help="Display warnings about data processing issues",
                key="batch_warnings"
            )
        
        with col2:
            show_individual_results = st.checkbox(
                "Show individual file results", 
                value=False,
                help="Display detailed results for each file processed",
                key="batch_individual"
            )
        
        # Process button
        if st.button("🔬 Analyze Batch Phase Statistics", type="primary", use_container_width=True):
            analyze_batch_phase_data(uploaded_files, include_warnings, show_individual_results, selected_parameters)
    
    # Batch results section
    if st.session_state.batch_analysis_results is not None:
        display_batch_analysis_results()

def analyze_batch_phase_data(uploaded_files, include_warnings: bool, show_individual_results: bool, selected_parameters: Optional[List[str]]):
    """NEW SPEC: Analyze multiple uploaded files for batch phase statistics"""
    
    try:
        with st.spinner("🔄 Analyzing batch phase statistics..."):
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Prepare file list
            file_names = [f.name for f in uploaded_files]
            
            # Reset file pointers
            for file in uploaded_files:
                file.seek(0)
            
            status_text.text(f"🔍 Processing {len(uploaded_files)} files as individual subjects...")
            progress_bar.progress(0.1)
            
            # Create phase analyzer instance
            analyzer = PhaseAnalyzer()
            
            # NEW SPEC: Analyze batch with subject-based processing
            batch_results = analyzer.analyze_batch_files(uploaded_files, file_names, selected_parameters)
            
            progress_bar.progress(0.9)
            status_text.text("✅ Batch analysis completed!")
            
            # Store results in session state
            st.session_state.batch_analysis_results = batch_results
            
            # Clear progress indicators
            progress_bar.progress(1.0)
            progress_bar.empty()
            status_text.empty()
            
            # Show summary
            if batch_results['success']:
                if batch_results.get('batch_statistics') and batch_results['batch_statistics']['success']:
                    subjects_count = batch_results['batch_statistics']['subjects']
                    st.success(f"🎉 Successfully processed {batch_results['files_processed']} subjects with {subjects_count} subjects in final dataset!")
                else:
                    st.success(f"🎉 Successfully processed {batch_results['files_processed']} out of {batch_results['total_files']} files!")
            else:
                st.error("❌ Batch analysis failed")
                
            # Show warnings if requested
            if include_warnings and batch_results['warnings']:
                st.warning("⚠️ **Processing Warnings:**")
                for warning in batch_results['warnings']:
                    st.warning(f"• {warning}")
            
            st.rerun()  # Refresh to show results
            
    except Exception as e:
        st.error(f"❌ Error during batch analysis: {str(e)}")
        st.exception(e)  # For debugging

def display_batch_analysis_results():
    """NEW SPEC: Display batch phase analysis results with subject-based format"""
    batch_results = st.session_state.batch_analysis_results
    
    st.markdown("---")
    st.subheader("📊 Batch Analysis Results")
    
    # Results summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Files Processed",
            value=f"{batch_results['files_processed']}/{batch_results['total_files']}",
            delta="subjects"
        )
    
    with col2:
        batch_available = batch_results.get('batch_statistics') and batch_results['batch_statistics']['success']
        st.metric(
            label="Batch Dataset",
            value="✅ Available" if batch_available else "❌ Not Available",
            delta="flattened"
        )
    
    with col3:
        successful_count = len([r for r in batch_results['file_results'].values() if r['success']])
        st.metric(
            label="Successful Subjects",
            value=successful_count,
            delta="analyzed"
        )
    
    with col4:
        st.metric(
            label="Export Ready",
            value="✅ Ready",
            delta="3 sheets"
        )
    
    # File processing summary
    st.subheader("📋 Subject Processing Summary")
    
    # Create summary table
    summary_data = []
    for filename, result in batch_results['file_results'].items():
        subject_name = filename.split('.')[0] if '.' in filename else filename
        if result['success']:
            summary_data.append({
                'Subject': subject_name,
                'File': filename,
                'Status': '✅ Success',
                'Rows Processed': f"{result.get('processed_rows', 0):,}",
                'Phase Groups': result.get('phase_groups', 0),
                'Numeric Columns': result.get('numeric_columns', 0)
            })
        else:
            summary_data.append({
                'Subject': subject_name,
                'File': filename,
                'Status': '❌ Failed',
                'Rows Processed': '0',
                'Phase Groups': '0',
                'Numeric Columns': '0'
            })
    
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    # NEW SPEC: Batch statistics preview (subjects as rows, Phase_Parameter as columns)
    if batch_results.get('batch_statistics') and batch_results['batch_statistics']['success']:
        st.subheader("📈 Batch Dataset Statistics (Subject-Based)")
        
        batch_stats = batch_results['batch_statistics']
        
        # Batch metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Subjects",
                value=batch_stats['subjects'],
                delta=f"{len(batch_stats['phases'])} phases"
            )
        
        with col2:
            st.metric(
                label="Parameters Analyzed",
                value=len(batch_stats['parameters']),
                delta="numeric columns"
            )
        
        with col3:
            phase_param_combinations = len(batch_stats['phases']) * len(batch_stats['parameters'])
            st.metric(
                label="Phase×Parameter Combinations",
                value=phase_param_combinations,
                delta="data columns"
            )
        
        # NEW SPEC: Preview the 3 main sheets with subjects as rows
        stat_tab1, stat_tab2, stat_tab3 = st.tabs(["📊 Average Sheet", "📏 StdDev Sheet", "📈 Max Sheet"])
        
        with stat_tab1:
            st.write("**Average Values (Rows = Subjects, Columns = Phase_Parameter):**")
            avg_df = batch_stats['average']
            st.dataframe(avg_df, use_container_width=True)
        
        with stat_tab2:
            st.write("**Standard Deviation Values (Rows = Subjects, Columns = Phase_Parameter):**")
            std_df = batch_stats['stddev']
            st.dataframe(std_df, use_container_width=True)
        
        with stat_tab3:
            st.write("**Maximum Values (Rows = Subjects, Columns = Phase_Parameter):**")
            max_df = batch_stats['max']
            st.dataframe(max_df, use_container_width=True)
    
    # Individual file results (if requested)
    if st.checkbox("Show Individual Subject Results", value=False, help="Display detailed statistics for each successfully processed subject"):
        st.subheader("� Individual Subject Results")
        
        for filename, result in batch_results['file_results'].items():
            if result['success']:
                subject_name = filename.split('.')[0] if '.' in filename else filename
                with st.expander(f"📊 Subject: {subject_name} ({filename})", expanded=False):
                    # Individual subject metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Phase Groups", result['phase_groups'])
                    
                    with col2:
                        st.metric("Rows Processed", f"{result.get('processed_rows', 0):,}")
                    
                    with col3:
                        st.metric("Numeric Columns", result['numeric_columns'])
                    
                    # Individual subject statistics tabs
                    sub_tab1, sub_tab2, sub_tab3 = st.tabs([f"📊 {subject_name} Avg", f"📏 {subject_name} Std", f"📈 {subject_name} Max"])
                    
                    with sub_tab1:
                        if 'statistics' in result:
                            st.dataframe(result['statistics']['average'], use_container_width=True)
                        else:
                            st.warning("No statistics available for this subject")
                    
                    with sub_tab2:
                        if 'statistics' in result:
                            st.dataframe(result['statistics']['stddev'], use_container_width=True)
                        else:
                            st.warning("No statistics available for this subject")
                    
                    with sub_tab3:
                        if 'statistics' in result:
                            st.dataframe(result['statistics']['max'], use_container_width=True)
                        else:
                            st.warning("No statistics available for this subject")
    
    # Export section
    st.subheader("📥 Export Batch Results")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **NEW FORMAT: Subject-Based Analysis**
        - **Rows**: Each subject (one per file)
        - **Columns**: Phase_Parameter combinations
        - **Sheets**: Average, StdDev, Max values
        - **Schema**: Consistent across all subjects (missing phases = NaN)
        """)
    
    with col2:
        # Generate filename with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_batch_results.xlsx"
        
        if st.button("📊 Download Batch Results", type="primary", use_container_width=True):
            try:
                # Create phase analyzer for export
                analyzer = PhaseAnalyzer()
                excel_bytes = analyzer.export_batch_statistics_to_bytes(batch_results)
                
                st.download_button(
                    label=f"💾 Save {filename}",
                    data=excel_bytes,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
                st.success("✅ Export ready! Click the download button above.")
                
            except Exception as e:
                st.error(f"❌ Error creating Excel file: {str(e)}")
    
    # Additional information about NEW SPEC batch analysis
    with st.expander("ℹ️ About NEW Batch Analysis Format", expanded=False):
        st.markdown("""
        ### 📊 Batch Processing - Subject-Based Format
        
        **Key Changes:**
        - Each uploaded file represents **one test subject**
        - Subject name = filename (without extension)
        - Final output has **subjects as rows**, **Phase_Parameter as columns**
        
        **Output Structure:**
        - **3 Sheets**: Average, StdDev, Max
        - **Consistent Schema**: All subjects have the same column structure
        - **Missing Data**: If a subject lacks a phase, values = NaN
        
        **Example Column Names:**
        - `EXERCISE 1_HR`, `EXERCISE 1_VO2`
        - `RECOVERY 2_HR`, `RECOVERY 2_VO2`
        - `WARMUP_Speed`, `WARMUP_Pace`
        
        **Use Cases:**
        - **Multi-subject studies**: Compare statistics across participants
        - **Research datasets**: Easy import into statistical software
        - **Clinical analysis**: Side-by-side subject comparison
        """)
    
    # Clear results button
    if st.button("🗑️ Clear Batch Results", help="Clear current results to start a new analysis"):
        st.session_state.batch_analysis_results = None
        st.rerun()

def analyze_phase_data(uploaded_file, include_warnings: bool, show_phase_details: bool):
    """Analyze the uploaded file for phase statistics"""
    
    try:
        with st.spinner("🔄 Analyzing phase statistics..."):
            # Reset file pointer
            uploaded_file.seek(0)
            
            # Read the file into DataFrame
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Create phase analyzer instance
            analyzer = PhaseAnalyzer()
            
            # Analyze the DataFrame
            results = analyzer.analyze_dataframe(df)
            
            if results['success']:
                # Store results in session state
                st.session_state.phase_analysis_results = results
                
            # Show success message
            st.success("✅ Phase analysis completed successfully!")
            
            # Show processing info if applicable
            if results.get('processed_rows') and results['processed_rows'] != results['input_rows']:
                st.info(f"📋 **Processing Summary:**\n"
                       f"- Original file rows: {results['input_rows']:,}\n"
                       f"- Data rows processed: {results['processed_rows']:,}\n"
                       f"- Structured format detected and handled")
            
            # Show warnings if requested
            if include_warnings and results['warnings']:
                st.warning("⚠️ **Processing Notes:**")
                for warning in results['warnings']:
                    st.warning(f"• {warning}")
            
            # Show phase details if requested
            if show_phase_details:
                st.info(f"""
                📊 **Analysis Summary:**
                - Input rows: {results['input_rows']:,}
                - Data rows analyzed: {results.get('processed_rows', results['input_rows']):,}
                - Numeric columns: {results['numeric_columns']}
                - Phase groups identified: {results['phase_groups']}
                """)
                
                if results['phases']:
                    with st.expander("🔍 Detected Phase Groups", expanded=False):
                        # Group phases by base name for better display
                        phase_groups = {}
                        for phase in results['phases']:
                            if ' Set ' in phase:
                                base = phase.split(' Set ')[0]
                                if base not in phase_groups:
                                    phase_groups[base] = []
                                phase_groups[base].append(phase)
                            else:
                                if 'Other' not in phase_groups:
                                    phase_groups['Other'] = []
                                phase_groups['Other'].append(phase)
                        
                        for base_phase, phase_list in phase_groups.items():
                            st.write(f"**{base_phase}**: {len(phase_list)} occurrences")
                            if len(phase_list) <= 10:
                                for phase in phase_list:
                                    st.write(f"  • {phase}")
                            else:
                                for phase in phase_list[:5]:
                                    st.write(f"  • {phase}")
                                st.write(f"  ... and {len(phase_list)-5} more")
                
            else:
                st.error(f"❌ Analysis failed: {results['error']}")
                
                if results['warnings']:
                    st.warning("⚠️ **Warnings:**")
                    for warning in results['warnings']:
                        st.warning(f"• {warning}")
                        
    except Exception as e:
        st.error(f"❌ Error during analysis: {str(e)}")

def display_phase_analysis_results():
    """Display the phase analysis results"""
    results = st.session_state.phase_analysis_results
    
    st.markdown("---")
    st.subheader("📊 Analysis Results")
    
    # Results summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Phase Groups",
            value=results['phase_groups'],
            delta=f"{results['input_rows']:,} total rows"
        )
    
    with col2:
        st.metric(
            label="Parameters Analyzed", 
            value=results['numeric_columns'],
            delta="numeric columns"
        )
    
    with col3:
        file_size = "Ready for download"
        st.metric(
            label="Export Status",
            value="✅ Ready",
            delta=file_size
        )
    
    # Statistics preview
    st.subheader("📈 Statistics Preview")
    
    # Create tabs for different statistics
    stat_tab1, stat_tab2, stat_tab3 = st.tabs(["📊 Average", "📏 Std Deviation", "📈 Maximum"])
    
    with stat_tab1:
        st.write("**Average Values by Phase:**")
        avg_df = results['statistics']['average']
        st.dataframe(avg_df, use_container_width=True)
    
    with stat_tab2:
        st.write("**Standard Deviation by Phase:**")
        std_df = results['statistics']['stddev']
        st.dataframe(std_df, use_container_width=True)
    
    with stat_tab3:
        st.write("**Maximum Values by Phase:**")
        max_df = results['statistics']['max']
        st.dataframe(max_df, use_container_width=True)
    
    # Export section
    st.subheader("📥 Export Results")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Generate Excel file for download
        try:
            analyzer = PhaseAnalyzer()
            excel_bytes = analyzer.export_statistics_to_bytes(
                results['statistics']['average'],
                results['statistics']['stddev'],
                results['statistics']['max']
            )
            
            filename = "phase_statistics_analysis.xlsx"
            
            st.download_button(
                label="📥 Download Excel Report",
                data=excel_bytes,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                help="Download complete phase statistics in Excel format with separate sheets for Average, StdDev, and Max"
            )
            
        except Exception as e:
            st.error(f"❌ Error preparing download: {str(e)}")
    
    with col2:
        if st.button("🔄 New Analysis", use_container_width=True):
            st.session_state.phase_analysis_results = None
            st.rerun()
    
    # Additional information
    with st.expander("ℹ️ About Phase Statistics", expanded=False):
        st.markdown("""
        ### 📊 What This Analysis Provides:
        
        **Three Statistical Measures:**
        - **Average**: Arithmetic mean of each parameter for each phase occurrence
        - **Standard Deviation**: Sample standard deviation (using ddof=1) showing data spread
        - **Maximum**: Peak values reached in each parameter for each phase occurrence
        
        **Phase Grouping Logic:**
        - Phases are grouped by their base name (removing trailing "Set" and numbers)
        - Each occurrence gets a "Set N" suffix (e.g., "Exercise Set 1", "Exercise Set 2")
        - Preserves the original casing from your data
        
        **File Format Support:**
        - **Simple Format**: Files with Phase column and numeric data
        - **Structured Format**: Files with metadata columns before 't' column
          - Automatically drops columns before 't' (preserving Phase if found)
          - Skips units row and empty row
          - Starts analysis from actual time-series data
        
        **Input Requirements:**
        - Must contain a 'Phase' column (anywhere in the file)
        - Numeric columns for statistical analysis
        - Supports Excel (.xlsx, .xls) and CSV formats
        
        **Output Format:**
        - Excel file with three sheets: `Average`, `StdDev`, `Max`
        - Rows represent phase groups (with Set suffixes)
        - Columns represent the numeric parameters from your data
        - Missing or non-numeric values are handled as NaN
        
        **Use Cases:**
        - Exercise physiology research (HIIT analysis, recovery studies)
        - Clinical assessment of repeated exercise phases
        - Performance analysis across multiple test sets
        - Statistical comparison between different phase occurrences
        - COSMED data analysis with structured export format
        """)

    # Format detection info
    with st.expander("🔍 Supported File Formats", expanded=False):
        st.markdown("""
        ### 📁 File Format Detection:
        
        **Simple Format:**
        ```
        Phase,VO2,HR,VE,Speed
        Exercise,25.5,120,45.2,8.0
        Exercise,26.1,125,47.1,8.2
        Rest,10.2,70,20.1,0.0
        ```
        
        **Structured Format (COSMED exports):**
        ```
        Metadata1,Metadata2,...,t,Rf,VT,VE,...,Phase
        units_row,units,...,s,1/min,L(btps),L/min,...,---
        empty_row,empty,...,NaN,NaN,NaN,NaN,...,NaN
        00:00:01,data,...,20.6,0.582,12,...,REST
        00:00:04,data,...,17.4,0.859,14.9,...,REST
        ```
        
        **Batch Processing:**
        - Upload multiple files simultaneously for comprehensive analysis
        - Combines compatible files into unified dataset
        - Maintains individual file statistics alongside combined results
        - Handles mixed file formats automatically
        
        **Automatic Processing:**
        - Detects column 't' as start of time-series data  
        - Preserves Phase column even if before 't'
        - Skips metadata, units, and empty rows
        - Focuses analysis on actual measurement data
        - Processes each batch file independently before combining
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