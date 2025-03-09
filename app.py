import streamlit as st

# Set page configuration - this should be the first Streamlit command
st.set_page_config(
    page_title="Course Recommendation App",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

import os
from pages.login import show_login
from pages.signup import show_signup
from pages.dashboard import show_dashboard
from database.db_functions import init_connection

# Add custom CSS for better styling
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        h1, h2, h3 {
            color: #1E88E5;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        .stTabs [data-baseweb="tab"] {
            height: 4rem;
            white-space: pre-wrap;
            background-color: #F8F9FA;
            border-radius: 4px 4px 0px 0px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #E3F2FD;
            border-bottom: 2px solid #1E88E5;
        }
        .stButton button {
            border-radius: 4px;
            height: 2.5rem;
        }
        .stForm [data-testid="stForm"] {
            border: 1px solid #EEEEEE;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "login"

def main():

    # Sidebar Navigation
    with st.sidebar:
        st.title("🧠 SkillSphere")
        st.markdown("---")
        
        if st.session_state.authenticated:
            st.success(f"Logged in as {st.session_state.username}")
            st.markdown("---")
            
            if st.button("📊 Dashboard", key="dashboard_button", use_container_width=True):
                st.session_state.current_page = "dashboard"
                st.rerun()
                
            st.markdown("---")
            if st.button("🚪 Logout", key="logout_button", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.user_id = None
                st.session_state.current_page = "login"
                st.rerun()
        else:
            st.info("Please login or create an account")
            
            if st.button("🔑 Login", key="login_button_sidebar", use_container_width=True):
                st.session_state.current_page = "login"
                st.rerun()
                
            if st.button("✏️ Sign Up", key="signup_button_sidebar", use_container_width=True):
                st.session_state.current_page = "signup"
                st.rerun()
        
        # Add some information about the app
        st.markdown("---")
        st.markdown("### About")
        st.markdown(""" 
        This app helps you find courses 
        based on your skills and interests.
        
        Get personalized recommendations
        and discover top trending courses.
        """)

    # Main Page Content - Simplified logic
    if st.session_state.authenticated and st.session_state.current_page == "dashboard":
        show_dashboard()
    elif st.session_state.current_page == "signup":
        show_signup()
    else:
        # Default to login for any other case
        show_login()

if __name__ == "__main__":
    main()
