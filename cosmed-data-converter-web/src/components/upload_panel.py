import streamlit as st
from src.utils import state, params, validators
from web_modules import XmlDataReader, ExcelExporter
import tempfile
import os

def render_upload_panel():
    """Render the file upload panel with parameter scanning and conversion"""
    st.subheader("📁 Upload COSMED XML Files")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose XML files",
        type=['xml'],
        accept_multiple_files=True,
        help="Select one or more COSMED XML export files"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully")
        
        # Parameter scanning section
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🔍 Scan Parameters", help="Analyze files to detect available parameters", key="scan_parameters_button"):
                with st.spinner("Scanning parameters..."):
                    if params.scan_parameters_from_files(uploaded_files):
                        st.success("✅ Parameters scanned successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Could not scan parameters")
        
        with col2:
            if state.get_available_parameters():
                st.info(f"📊 Found {len(state.get_available_parameters())} parameters")
        
        # Show available parameters if scanned
        if state.get_available_parameters():
            with st.expander("🔍 Available Parameters", expanded=False):
                params_df = st.dataframe(
                    {"Available Parameters": state.get_available_parameters()},
                    use_container_width=True,
                    height=200
                )
        
        # Conversion button
        st.markdown("---")
        if st.button("🔄 Convert to Excel", type="primary", use_container_width=True, key="convert_to_excel_button"):
            if _validate_files(uploaded_files):
                with st.spinner("Processing files..."):
                    success, result = _process_files(uploaded_files)
                    if success:
                        state.set('processed_data', result)
                        state.set('file_count', len(uploaded_files))
                        st.success("✅ Files processed successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Processing failed: {result}")

def _validate_files(uploaded_files):
    """Validate uploaded files"""
    try:
        valid_files = []
        invalid_files = []
        
        for file in uploaded_files:
            if file.name.lower().endswith('.xml'):
                # Basic XML validation by trying to read content
                content = file.read()
                file.seek(0)  # Reset file pointer
                
                if b'<?xml' in content[:100] or b'<' in content[:100]:
                    valid_files.append(file.name)
                else:
                    invalid_files.append(file.name)
            else:
                invalid_files.append(file.name)
        
        if invalid_files:
            st.error(f"❌ Invalid files detected: {', '.join(invalid_files)}")
            return False
        
        if not valid_files:
            st.error("❌ No valid XML files found")
            return False
        
        return True
        
    except Exception as e:
        st.error(f"❌ Validation error: {str(e)}")
        return False

def _process_files(uploaded_files):
    """Process uploaded files based on selected export type"""
    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded files
            for file in uploaded_files:
                file_path = os.path.join(temp_dir, file.name)
                with open(file_path, "wb") as f:
                    f.write(file.read())
                file.seek(0)  # Reset file pointer
            
            # Initialize data reader
            reader = XmlDataReader(temp_dir)
            
            # Get export type from session state
            export_type = state.get('export_type', 'selected')
            custom_parameters = state.get_custom_parameters()
            
            # Process based on export type
            if export_type == "custom" and custom_parameters:
                processed_data = reader.extract_data_with_custom_parameters(custom_parameters)
            elif export_type == "max":
                processed_data = reader.extract_max_values()
            elif export_type == "complete":
                processed_data = reader.extract_complete_data()
            else:  # selected
                processed_data = reader.extract_selected_data()
            
            if not processed_data:
                return False, "No data could be extracted from the files"
            
            # Create Excel exporter
            exporter = ExcelExporter(processed_data)
            
            # Generate Excel file in memory
            excel_buffer = exporter.create_excel_buffer()
            
            return True, {
                'data': processed_data,
                'excel_buffer': excel_buffer,
                'export_type': export_type,
                'file_count': len(uploaded_files)
            }
            
    except Exception as e:
        return False, str(e)
