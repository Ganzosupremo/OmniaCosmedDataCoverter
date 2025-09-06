import streamlit as st

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