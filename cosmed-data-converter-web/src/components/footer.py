import streamlit as st

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
