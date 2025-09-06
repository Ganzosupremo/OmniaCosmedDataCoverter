import streamlit as st
from . import state
from web_modules import XmlDataReader
import os
import tempfile

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

                state.set_available_parameters(sorted(list(params)))
                return True
            else:
                state.set_available_parameters([])
                return False
                
    except Exception as e:
        st.error(f"Error scanning parameters: {str(e)}")
        state.set_available_parameters([])
        return False

def select_key_parameters():
    """Select the standard 15 key parameters with appropriate phases"""
    key_params = [
        't', 'Speed', 'Pace', 'VO2', 'VO2/kg', 'VCO2', 
        'METS', 'RQ', 'VE', 'Rf', 'HR', 'VO2/HR', 
        'P Syst', 'P Diast', 'HRR'
    ]

    state.set_custom_parameters({})

    for param in key_params:
        if param in state.get_available_parameters():
            # Use smart defaults based on parameter type
            if param == 'VO2/kg':
                state.get_custom_parameters()[param] = ['MFO', 'AT', 'RC', 'Max']
            elif param in ['HRR', 'P Syst', 'P Diast']:
                # These parameters typically have their primary data in the 'Value' field
                state.get_custom_parameters()[param] = ['Value']
            else:
                # Most other parameters use Max phase
                state.get_custom_parameters()[param] = ['Max']
