import streamlit as st
from src.utils import state
from web_modules import PhaseAnalyzer
import pandas as pd

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
        if st.button("🔬 Analyze Phase Statistics", type="primary", use_container_width=True, key="analyze_single_file_button"):
            analyze_phase_data(uploaded_file, include_warnings, show_phase_details)
    
    # Results section
    if state.get_phase_analysis_results() is not None:
        display_phase_analysis_results()

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
                state.set_phase_analysis_results(results)

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
                key="download_single_file_analysis"
            )
            
        except Exception as e:
            st.error(f"❌ Error preparing download: {str(e)}")
    
    with col2:
        if st.button("🔄 New Analysis", use_container_width=True, key="new_analysis_single_file"):
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