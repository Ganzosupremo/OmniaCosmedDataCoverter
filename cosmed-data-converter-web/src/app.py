import streamlit as st
import os
import tempfile
import zipfile
from io import BytesIO
import pandas as pd
from xml_data_reader import XmlDataReader
from excel_exporter import ExcelExporter

# Page configuration
st.set_page_config(
    page_title="COSMED XML Converter",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #1f77b4, #17becf);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .upload-box {
        border: 2px dashed #cccccc;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'file_count' not in st.session_state:
    st.session_state.file_count = 0

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🫁 COSMED XML Data Converter</h1>
        <p>Convert COSMED cardiopulmonary exercise test data from XML to Excel</p>
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
            st.info("Custom parameter selection will be available after scanning files.")
        
        # Help section
        st.header("📖 Help & Info")
        
        if st.button("❓ How to Use", use_container_width=True):
            show_help_dialog()
        
        if st.button("ℹ️ About", use_container_width=True):
            show_about_dialog()

def create_main_content():
    """Create main content area"""
    
    # File upload section
    st.header("📁 Upload XML Files")
    
    uploaded_files = st.file_uploader(
        "Choose COSMED XML files",
        type=['xml'],
        accept_multiple_files=True,
        help="Select one or more XML files exported from COSMED software"
    )
    
    if uploaded_files:
        st.session_state.file_count = len(uploaded_files)
        
        # Display uploaded files
        with st.expander(f"📄 Uploaded Files ({len(uploaded_files)})", expanded=False):
            for i, file in enumerate(uploaded_files, 1):
                file_size = len(file.read()) / 1024  # KB
                file.seek(0)  # Reset file pointer
                st.write(f"{i}. **{file.name}** ({file_size:.1f} KB)")
        
        # File validation
        valid_files = validate_files(uploaded_files)
        
        if valid_files:
            st.success(f"✅ {len(valid_files)} valid XML files ready for processing")
            
            # Process button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    "⚡ Convert to Excel", 
                    type="primary", 
                    use_container_width=True,
                    disabled=len(valid_files) == 0
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
                
                status_text.text("🔍 Reading XML data...")
                progress_bar.progress(0.4)
                
                # Process files using existing classes
                reader = XmlDataReader(temp_dir)
                extracted_data = reader.extract_id_and_parameters()
                
                if extracted_data:
                    progress_bar.progress(0.7)
                    status_text.text(f"📊 Processing {len(extracted_data)} records...")
                    
                    # Create Excel file
                    output_path = os.path.join(temp_dir, "cosmed_converted_data.xlsx")
                    exporter = ExcelExporter(output_path)
                    
                    export_type = st.session_state.export_type
                    
                    if export_type == "selected":
                        exporter.export_selected_parameters(extracted_data)
                    elif export_type == "max":
                        exporter.export_max_values_only(extracted_data)
                    elif export_type == "complete":
                        exporter.export_extracted_xml_data(extracted_data)
                    else:  # custom
                        # For now, default to selected
                        exporter.export_selected_parameters(extracted_data)
                    
                    progress_bar.progress(0.9)
                    status_text.text("📝 Preparing download...")
                    
                    # Read the created Excel file
                    with open(output_path, "rb") as excel_file:
                        excel_data = excel_file.read()
                    
                    # Store results in session state
                    st.session_state.processed_data = {
                        'excel_data': excel_data,
                        'file_count': len(extracted_data),
                        'export_type': export_type,
                        'filename': f"cosmed_data_{export_type}.xlsx"
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
    
    st.header("📊 Processing Results")
    
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
        st.metric(
            label="Export Type",
            value=data['export_type'].title(),
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
            st.rerun()

def show_help_dialog():
    """Show help information"""
    st.info("""
    ## 📖 How to Use COSMED XML Converter
    
    ### Step 1: Upload Files
    - Click "Browse files" or drag & drop XML files
    - Select one or more COSMED XML export files
    - Supported format: XML files from COSMED software
    
    ### Step 2: Choose Export Type
    - **Selected Parameters**: 15 key clinical parameters
    - **Max Values Only**: Peak performance values
    - **Complete Dataset**: All measurement phases
    - **Custom Parameters**: Choose specific data (coming soon)
    
    ### Step 3: Process & Download
    - Click "Convert to Excel" to process files
    - Download the generated Excel file
    - Open in Excel, LibreOffice, or similar software
    
    ### Supported Data
    - VO2, VCO2, respiratory parameters
    - Heart rate and metabolic data
    - Multiple test phases (Rest, AT, Max, etc.)
    - Patient demographics and test info
    """)

def show_about_dialog():
    """Show about information"""
    st.info("""
    ## ℹ️ About COSMED XML Converter
    
    **Version**: 2.0 (Streamlit Web Edition)
    
    **Purpose**: Convert COSMED cardiopulmonary exercise test data from XML format to Excel spreadsheets for easier analysis and reporting.
    
    **Features**:
    - Web-based interface (no installation required)
    - Multiple export formats
    - Batch processing of multiple files
    - Automatic data validation
    - Cross-platform compatibility
    
    **Supported COSMED Systems**:
    - Quark CPET
    - K5 series
    - Fitmate Pro
    - And other COSMED systems that export XML data
    
    **Developer**: Built for healthcare professionals and researchers working with cardiopulmonary exercise testing data.
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