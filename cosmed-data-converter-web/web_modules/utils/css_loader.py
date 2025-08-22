import streamlit as st
import os
from pathlib import Path

class CSSLoader:
    """
    CSS loading utility for Streamlit apps
    """
    @staticmethod
    def load_css(css_file_path: str):
        """
        Load CSS from external file and inject into Streamlit app
        Args:
            css_file_path: Path to the CSS file relative to the app root
        """
        try:
            # Get the directory of the current script
            current_dir = Path(__file__).parent.parent.parent
            css_path = current_dir / css_file_path
            
            # Alternative: Use absolute path if file exists
            if not css_path.exists():
                css_path = Path(css_file_path)
            
            if css_path.exists():
                with open(css_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                
                st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
                return True
            else:
                st.error(f"CSS file not found: {css_path}")
                return False
                
        except Exception as e:
            st.error(f"Error loading CSS: {str(e)}")
            return False

    @staticmethod
    def load_css_from_string(css_content: str):
        """
        Load CSS from a string (fallback method)
        
        Args:
            css_content: CSS content as string
        """
        try:
            st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
            return True
        except Exception as e:
            st.error(f"Error applying CSS: {str(e)}")
            return False