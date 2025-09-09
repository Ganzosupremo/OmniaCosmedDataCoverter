"""Enhanced Streamlit app with SaaS authentication and job management."""

import streamlit as st
import requests
import os
from datetime import datetime
import pandas as pd

from src.utils import state, layout
from src.components import (
    create_sidebar,
    render_upload_panel,
    display_phase_analysis_results,
    create_single_file_analyzer,
    create_batch_file_analyzer,
    create_footer
)

# Configuration
try:
    API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")
except:
    # Fallback to environment variable or default if secrets not available
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="COSMED Phase Analyzer",
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
    
    # Check authentication
    if not is_authenticated():
        render_auth_page()
        return
    
    # Header with user info
    render_header_with_user_info()
    
    # Create tabs for different functionalities
    tab1, tab2, tab3, tab4 = st.tabs(["🔄 XML Converter", "📊 Phase Statistics", "📋 Jobs", "👤 Account"])
    
    with tab1:
        render_xml_converter_tab()
    
    with tab2:
        render_phase_analyzer_tab()
    
    with tab3:
        render_jobs_tab()
    
    with tab4:
        render_account_tab()
    
    # Footer
    create_footer()


def is_authenticated():
    """Check if user is authenticated."""
    return st.session_state.get('access_token') is not None


def render_auth_page():
    """Render authentication page."""
    st.markdown("""
        <div style="text-align: center; margin: 4rem auto; max-width: 500px;">
            <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem;">🫁 COSMED Phase Analyzer</h1>
            <p style="font-size: 1.2rem; color: var(--text-secondary); margin-bottom: 3rem;">
                Professional cardiopulmonary exercise test analysis platform
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Authentication tabs
    auth_tab1, auth_tab2 = st.tabs(["🔑 Sign In", "📝 Sign Up"])
    
    with auth_tab1:
        render_signin_form()
    
    with auth_tab2:
        render_signup_form()


def render_signin_form():
    """Render sign-in form."""
    with st.form("signin_form"):
        st.subheader("Sign In to Your Account")
        
        email = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Sign In", use_container_width=True):
            if sign_in_user(email, password):
                st.success("Successfully signed in!")
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")


def render_signup_form():
    """Render sign-up form."""
    with st.form("signup_form"):
        st.subheader("Create Your Account")
        
        name = st.text_input("Full Name", placeholder="John Doe")
        email = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.form_submit_button("Create Account", use_container_width=True):
            if password != confirm_password:
                st.error("Passwords do not match.")
                return
            
            if create_user_account(name, email, password):
                st.success("Account created successfully! Please sign in.")
            else:
                st.error("Failed to create account. Email might already be in use.")


def sign_in_user(email: str, password: str) -> bool:
    """Authenticate user and store token."""
    # In a real implementation, you'd call your auth endpoint
    # For now, we'll simulate with a mock token
    if email and password:
        # Mock authentication - replace with actual API call
        mock_token = f"mock_token_{email}"
        st.session_state.access_token = mock_token
        st.session_state.user_email = email
        return True
    return False


def create_user_account(name: str, email: str, password: str) -> bool:
    """Create a new user account."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/users/",
            json={"name": name, "email": email},
            headers={"Content-Type": "application/json"}
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error creating account: {e}")
        return False


def render_header_with_user_info():
    """Render header with user information and logout."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
            <div style="margin-bottom: 2rem;">
                <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">🫁 COSMED Phase Analyzer</h1>
                <p style="font-size: 1rem; color: var(--text-secondary);">
                    Professional cardiopulmonary exercise test analysis
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"**Welcome, {st.session_state.get('user_email', 'User')}**")
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()


def logout_user():
    """Logout user and clear session."""
    st.session_state.clear()
    st.rerun()


def render_xml_converter_tab():
    """Render the XML converter tab."""
    # Check user entitlements
    entitlements = get_user_entitlements()
    
    if entitlements:
        st.info(f"**Your Plan Limits:** {entitlements['max_files']} files, {entitlements['max_mb']}MB total")
    
    # Sidebar configuration
    create_sidebar()
    
    # Main content for XML conversion
    render_upload_panel()
    
    # Results panel (if data has been processed)
    if state.get('processed_data'):
        render_results_panel()


def render_phase_analyzer_tab():
    """Render the phase analyzer tab."""
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


def render_jobs_tab():
    """Render the jobs management tab."""
    st.header("📋 Your Processing Jobs")
    
    # Get user jobs
    jobs = get_user_jobs()
    
    if not jobs:
        st.info("No jobs found. Upload some files to get started!")
        return
    
    # Display jobs in a table
    jobs_df = pd.DataFrame([
        {
            "Job ID": job["job_id"][:8] + "...",
            "Status": job["status"].title(),
            "Files": job["file_count"],
            "Size (MB)": f"{job['total_size_mb']:.1f}",
            "Created": datetime.fromisoformat(job["created_at"].replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M"),
            "Download": "✅" if job["output_url"] else "⏳"
        }
        for job in jobs
    ])
    
    st.dataframe(jobs_df, use_container_width=True)
    
    # Job details
    st.subheader("Job Details")
    job_ids = [job["job_id"] for job in jobs]
    selected_job_id = st.selectbox("Select a job to view details:", job_ids)
    
    if selected_job_id:
        selected_job = next(job for job in jobs if job["job_id"] == selected_job_id)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Status", selected_job["status"].title())
        
        with col2:
            st.metric("Files", selected_job["file_count"])
        
        with col3:
            st.metric("Size", f"{selected_job['total_size_mb']:.1f} MB")
        
        # Download button if completed
        if selected_job["output_url"]:
            st.success("✅ Job completed successfully!")
            if st.button("📥 Download Results", use_container_width=True):
                st.markdown(f"[Download Results]({selected_job['output_url']})")
        elif selected_job["status"] == "failed":
            st.error(f"❌ Job failed: {selected_job.get('error_message', 'Unknown error')}")
        else:
            st.info("⏳ Job is still processing...")


def render_account_tab():
    """Render the account management tab."""
    st.header("👤 Account Settings")
    
    # Current plan info
    entitlements = get_user_entitlements()
    
    if entitlements:
        st.subheader("Current Plan")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Max Files", entitlements["max_files"])
        
        with col2:
            st.metric("Max Size", f"{entitlements['max_mb']} MB")
        
        with col3:
            st.metric("Batch Processing", "✅" if entitlements["batch"] else "❌")
    
    # Upgrade options
    st.subheader("Upgrade Your Plan")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            **Free Plan**
            - 10 files max
            - 50 MB total
            - Basic support
            
            *Current Plan*
        """)
    
    with col2:
        st.markdown("""
            **Pro Plan**
            - 20 files max
            - 150 MB total
            - Priority support
            - Advanced analytics
            
            **$19/month**
        """)
        
        if st.button("Upgrade to Pro", use_container_width=True):
            st.info("Redirecting to checkout...")
    
    with col3:
        st.markdown("""
            **Team Plan**
            - 100 files max
            - 1000 MB total
            - Team collaboration
            - API access
            
            **$49/month**
        """)
        
        if st.button("Upgrade to Team", use_container_width=True):
            st.info("Redirecting to checkout...")


def get_user_entitlements():
    """Get current user's plan entitlements."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/users/me/entitlements",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching entitlements: {e}")
    return None


def get_user_jobs():
    """Get user's processing jobs."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/jobs/",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching jobs: {e}")
    return []


def render_results_panel():
    """Render the results panel with download functionality."""
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


def render_test_mode():
    """Render test mode interface for developers."""
    st.markdown("### 🧪 Test Mode")
    st.info("This is a test mode for developers to test SaaS functionality without external dependencies.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### API Tests")
        if st.button("Test API Health", use_container_width=True):
            try:
                response = requests.get(f"{API_BASE_URL}/health", timeout=5)
                if response.status_code == 200:
                    st.success("✅ API is healthy")
                else:
                    st.error(f"❌ API unhealthy: {response.status_code}")
            except Exception as e:
                st.error(f"❌ API connection failed: {e}")
        
        if st.button("Test User Creation", use_container_width=True):
            try:
                test_data = {
                    "username": f"testuser_{int(datetime.now().timestamp())}",
                    "email": f"test_{int(datetime.now().timestamp())}@example.com",
                    "password": "testpassword123"
                }
                response = requests.post(f"{API_BASE_URL}/test/create-user", params=test_data, timeout=10)
                if response.status_code == 200:
                    st.success("✅ Test user created successfully")
                    st.json(response.json())
                else:
                    st.error(f"❌ User creation failed: {response.text}")
            except Exception as e:
                st.error(f"❌ Test failed: {e}")
    
    with col2:
        st.markdown("#### System Tests")
        if st.button("Test Email Service", use_container_width=True):
            test_email_data = {
                "to_email": "test@example.com",
                "user_name": "Test User",
                "job_id": f"test_job_{int(datetime.now().timestamp())}",
                "status": "completed",
                "download_url": "https://example.com/download"
            }
            st.success("✅ Email service test (mock)")
            st.json(test_email_data)
        
        if st.button("Test Worker Health", use_container_width=True):
            worker_health = {
                "status": "healthy",
                "active_jobs": 2,
                "pending_jobs": 5,
                "average_processing_time_seconds": 120,
                "timestamp": datetime.now().isoformat()
            }
            st.success("✅ Worker service healthy (mock)")
            st.json(worker_health)
    
    st.markdown("#### Database Tests")
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("Test Plan Limits", use_container_width=True):
            plan_limits = {
                "free": {"daily_file_limit": 5, "batch_size_limit": 10},
                "pro": {"daily_file_limit": 50, "batch_size_limit": 100},
                "team": {"daily_file_limit": 200, "batch_size_limit": 500}
            }
            st.success("✅ Plan limits configured")
            st.json(plan_limits)
    
    with col4:
        if st.button("Test Job Queue", use_container_width=True):
            job_queue = {
                "pending_jobs": 3,
                "active_jobs": 1,
                "completed_jobs_today": 15,
                "failed_jobs_today": 1,
                "queue_health": "normal"
            }
            st.success("✅ Job queue status (mock)")
            st.json(job_queue)


if __name__ == "__main__":
    # Check if test mode is enabled
    if os.getenv("STREAMLIT_TEST_MODE", "false").lower() == "true" or st.sidebar.checkbox("🧪 Test Mode"):
        render_test_mode()
    else:
        main()
