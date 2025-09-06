import streamlit as st
from src.utils import state
from src.utils.params import scan_parameters_from_files
from web_modules import PhaseAnalyzer
import pandas as pd
from typing import Optional, List

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
        if st.button("🔬 Analyze Batch Phase Statistics", type="primary", use_container_width=True, key="analyze_batch_files_button"):
            analyze_batch_phase_data(uploaded_files, include_warnings, show_individual_results, selected_parameters)
    
    # Batch results section
    if state.get_batch_analysis_results() is not None:
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
            state.set_batch_analysis_results(batch_results)

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
    batch_results = state.get_batch_analysis_results()
    
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
        
        if st.button("📊 Download Batch Results", type="primary", use_container_width=True, key="download_batch_results_button"):
            try:
                # Create phase analyzer for export
                analyzer = PhaseAnalyzer()
                excel_bytes = analyzer.export_batch_statistics_to_bytes(batch_results)
                
                st.download_button(
                    label=f"💾 Save {filename}",
                    data=excel_bytes,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="save_batch_results_download"
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
    if st.button("🗑️ Clear Batch Results", help="Clear current results to start a new analysis", key="clear_batch_results_button"):
        state.set_batch_analysis_results(None)
        st.rerun()