import streamlit as st
from src.utils import state, layout
from src.components import (
    create_sidebar,
    render_upload_panel,
    display_phase_analysis_results,
    create_single_file_analyzer,
    create_batch_file_analyzer,
    create_footer
)

# Page configuration
st.set_page_config(
    page_title="COSMED XML Converter",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application entry point"""
    # Load CSS styles
    layout.load_css()
    
    # Initialize session state
    state.init_session_state()
    
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
        render_main_content()
    
    with tab2:
        # Phase statistics analyzer
        render_phase_analyzer_content()
    
    # Footer
    create_footer()

def render_main_content():
    """Render the main XML conversion content"""
    # Upload panel
    render_upload_panel()
    
    # Results panel (if data has been processed)
    if state.get('processed_data'):
        render_results_panel()

def render_results_panel():
    """Render the results panel with download functionality"""
    st.markdown("---")
    st.subheader("📊 Processing Results")
    
    processed_data = state.get('processed_data')
    file_count = state.get('file_count', 0)
    
    # Show summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Files Processed", file_count)
    
    with col2:
        if processed_data and 'data' in processed_data:
            record_count = len(processed_data['data'])
            st.metric("Records Extracted", record_count)
    
    with col3:
        export_type = processed_data.get('export_type', 'unknown') if processed_data else 'unknown'
        st.metric("Export Type", export_type.title())
    
    # Preview data
    if processed_data and 'data' in processed_data and processed_data['data']:
        with st.expander("📋 Data Preview", expanded=False):
            preview_data = processed_data['data'][:10]  # Show first 10 records
            st.dataframe(preview_data, use_container_width=True)
    
    # Download button
    if processed_data and 'excel_buffer' in processed_data:
        excel_buffer = processed_data['excel_buffer']
        export_type = processed_data.get('export_type', 'data')
        
        st.download_button(
            label="📥 Download Excel File",
            data=excel_buffer,
            file_name=f"cosmed_data_{export_type}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True,
            key="download_excel_main_results"
        )

def render_phase_analyzer_content():
    """Render the phase statistics analyzer content"""
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2>📊 Phase Statistics Analyzer</h2>
            <p style="color: var(--text-secondary);">
                Analyze cardiopulmonary exercise test phases and extract detailed statistics
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Create sub-tabs for single file and batch analysis
    analysis_tab1, analysis_tab2 = st.tabs(["📄 Single File Analysis", "📁 Batch Analysis"])
    
    with analysis_tab1:
        create_single_file_analyzer()
        
        # Display results if available
        if state.get_phase_analysis_results():
            display_phase_analysis_results()
    
    with analysis_tab2:
        create_batch_file_analyzer()

if __name__ == "__main__":
    main()