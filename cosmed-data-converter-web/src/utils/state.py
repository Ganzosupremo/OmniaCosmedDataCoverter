import streamlit as st

DEFAULTS={
    'processed_data': None,
    'available_parameters': [],
    'phase_analysis_results': None,
    'batch_analysis_results': None,
    'file_count': 0,
    'custom_parameters': {},
    'uploaded_files_data': None,
    'export_type': 'selected'
}

def init_session_state():
    for key,value in DEFAULTS.items():
        if key not in st.session_state: st.session_state[key]= value

def get(key, default=None): return st.session_state.get(key, default)

def set(key,value): st.session_state[key]=value

def set_available_parameters(value): set('available_parameters', list(value or []))

def get_available_parameters(): return get('available_parameters', [])

def set_custom_parameters(value): set('custom_parameters', value)

def set_custom_parameters_phases(param, phases): 
    custom_params = get_custom_parameters()
    if param not in custom_params:
        custom_params[param] = []
    custom_params[param] = phases
    set('custom_parameters', custom_params)

def get_custom_parameters() -> dict: return get('custom_parameters', {})

def set_phase_analysis_results(value): set('phase_analysis_results', value)

def get_phase_analysis_results() -> dict: return get('phase_analysis_results')

def set_batch_analysis_results(value): set('batch_analysis_results', value)

def get_batch_analysis_results(): return get('batch_analysis_results')