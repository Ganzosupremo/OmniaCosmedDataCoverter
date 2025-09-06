import streamlit as st
from web_modules import CSSLoader
import os

def load_css():
    """Load external CSS file"""
    try:
        css_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'styles.css')
        CSSLoader.load_css(css_path)
    except Exception as e:
        st.error(f"Could not load CSS: {e}")

def header(t,s=''): 
    st.markdown(f"### {t}"); st.caption(s) if s else None