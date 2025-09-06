import streamlit as st
from src.utils import state, params
from .help_about import show_help_dialog, show_about_dialog

def create_sidebar():
    """Create sidebar with settings and options"""
    with st.sidebar:
        st.header("⚙️ Export Settings")
        
        # Export type selection
        export_type = st.radio(
            "Choose Export Type:",
            ["selected", "max", "complete", "custom"],
            format_func=lambda x: {
                "selected": "📊 Selected Parameters",
                "max": "📈 Max Values Only", 
                "complete": "📋 Complete Dataset",
                "custom": "⚙️ Custom Parameters"
            }[x],
            help="Select what data to export from the XML files"
        )
        
        # Store in session state
        state.set("export_type", export_type)

        # Show description based on export type
        descriptions = {
            "selected": "Exports 15 key cardiopulmonary parameters including VO2/kg at MFO, AT, RC, and Max phases.",
            "max": "Exports maximum values for all parameters. Simplified dataset for peak performance analysis.",
            "complete": "Exports all measurement phases. Comprehensive data for detailed research.",
            "custom": "Choose specific parameters and phases to export."
        }
        
        st.info(descriptions[export_type])
        
        # Additional settings
        st.header("🔧 Additional Settings")
        
        auto_download = st.checkbox(
            "Auto-download result", 
            value=True,
            help="Automatically download the Excel file after processing"
        )
        state.set("auto_download", auto_download)

        include_metadata = st.checkbox(
            "Include metadata sheet", 
            value=True,
            help="Add a sheet with processing information and file details"
        )
        state.set("include_metadata", include_metadata)

        # Custom parameters (if selected)
        if export_type == "custom":
            st.header("📋 Custom Parameters")

            if state.get_available_parameters():
                st.success(f"✅ Found {len(state.get_available_parameters())} parameters")

                # Quick selection buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Select Key 15", use_container_width=True, help="Select the standard 15 clinical parameters", key="select_key_15_button"):
                        params.select_key_parameters()
                        st.rerun()
                
                with col2:
                    if st.button("Clear All", use_container_width=True, help="Clear all parameter selections", key="clear_all_params_button"):
                        state.set_custom_parameters({})
                        st.rerun()
                
                # Parameter selection
                st.subheader("Select Parameters:")
                
                # Phase explanation
                with st.expander("ℹ️ Understanding Measurement Phases", expanded=False):
                    st.markdown("""
                    **Common Measurement Phases:**
                    - **Value**: Primary measurement value (used for parameters like HRR, blood pressure)
                    - **Rest**: Baseline measurements before exercise
                    - **Warmup**: Initial low-intensity exercise phase
                    - **MFO**: Maximum Fat Oxidation point
                    - **AT**: Anaerobic Threshold (VT1)
                    - **RC**: Respiratory Compensation Point (VT2)
                    - **Max**: Peak exercise values
                    - **Pred**: Predicted values based on demographics
                    - **PercPred**: Percentage of predicted values
                    - **Normal**: Normal reference ranges
                    - **Class**: Classification categories
                    """)
                
                # Available phases (including Value which some parameters use as primary data)
                available_phases = ['Value', 'Rest', 'Warmup', 'MFO', 'AT', 'RC', 'Max', 'Pred', 'PercPred', 'Normal', 'Class']
                
                # Create parameter selection interface
                for param in state.get_available_parameters()[:15]:  # Limit to first 15 for UI
                    with st.expander(f"📊 {param}", expanded=param in state.get_custom_parameters()):
                        
                        # Parameter checkbox
                        param_selected = st.checkbox(
                            f"Include {param}",
                            value=param in state.get_custom_parameters(),
                            key=f"param_{param}"
                        )
                        
                        if param_selected:
                            # Phase selection
                            st.write("Select measurement phases:")
                            
                            # Smart default phases based on parameter type
                            default_phases = ['Max']  # Default fallback
                            
                            # Parameters that typically use 'Value' field
                            if param in ['HRR', 'P Syst', 'P Diast']:
                                default_phases = ['Value']
                            # VO2/kg gets multiple phases for comprehensive analysis
                            elif param == 'VO2/kg':
                                default_phases = ['MFO', 'AT', 'RC', 'Max']
                            # Metabolic and respiratory parameters often have meaningful data across phases
                            elif param in ['VO2', 'VCO2', 'METS', 'RQ', 'VE', 'Rf']:
                                default_phases = ['Max']  # Can be expanded to ['MFO', 'AT', 'RC', 'Max'] if desired
                            # Time and performance parameters
                            elif param in ['t', 'Speed', 'Pace']:
                                default_phases = ['Max']
                            # HR typically measured at multiple phases
                            elif param == 'HR':
                                default_phases = ['Max']  # Can be expanded to ['AT', 'RC', 'Max'] if desired

                            current_phases = state.get_custom_parameters().get(param, default_phases)

                            selected_phases = []
                            
                            # Group phases for better layout
                            primary_phases = ['Value', 'Rest', 'Warmup', 'MFO', 'AT', 'RC', 'Max']
                            secondary_phases = ['Pred', 'PercPred', 'Normal', 'Class']
                            
                            # Primary phases (more commonly used)
                            st.write("**Primary Phases:**")
                            phase_cols = st.columns(4)
                            for i, phase in enumerate(primary_phases):
                                with phase_cols[i % 4]:
                                    if st.checkbox(
                                        phase,
                                        value=phase in current_phases,
                                        key=f"phase_{param}_{phase}",
                                        help=f"Include {phase} phase data for {param}"
                                    ):
                                        selected_phases.append(phase)
                            
                            # Secondary phases (less commonly used)
                            with st.expander("📊 Additional Phases", expanded=False):
                                phase_cols2 = st.columns(4)
                                for i, phase in enumerate(secondary_phases):
                                    with phase_cols2[i % 4]:
                                        if st.checkbox(
                                            phase,
                                            value=phase in current_phases,
                                            key=f"phase_{param}_{phase}",
                                            help=f"Include {phase} data for {param}"
                                        ):
                                            selected_phases.append(phase)
                            
                            if selected_phases:
                                state.set_custom_parameters_phases(param, selected_phases)
                            elif param in state.get_custom_parameters():
                                del state.get_custom_parameters()[param]

                        elif param in state.get_custom_parameters():
                            del state.get_custom_parameters()[param]
                
                # Show selection summary
                if state.get_custom_parameters():
                    param_count = len(state.get_custom_parameters())
                    phase_count = sum(len(phases) for phases in state.get_custom_parameters().values())
                    st.success(f"📊 Selected: {param_count} parameters, {phase_count} total phases")
                else:
                    st.info("🔍 Select parameters above to customize your export")
            else:
                st.info("📤 Upload and scan files first to detect available parameters")
        
        # Help section
        st.header("📖 Help & Info")
        
        if st.button("❓ How to Use", use_container_width=True, key="help_button_sidebar"):
            show_help_dialog()
        
        if st.button("ℹ️ About", use_container_width=True, key="about_button_sidebar"):
            show_about_dialog()