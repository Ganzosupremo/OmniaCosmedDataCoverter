import streamlit as st

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