import streamlit as st
from src.utils import state
from web_modules import PhaseAnalyzer

def display_phase_analysis_results():
    """Display the phase analysis results"""
    results = state.get_phase_analysis_results()
    
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
                help="Download complete phase statistics in Excel format with separate sheets for Average, StdDev, and Max",
                key="download_excel_report_phase_analysis"
            )
            
        except Exception as e:
            st.error(f"❌ Error preparing download: {str(e)}")
    
    with col2:
        if st.button("🔄 New Analysis", use_container_width=True, key="new_analysis_button_phase"):
            state.set_phase_analysis_results(None)
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
