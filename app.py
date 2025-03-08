import streamlit as st
import os
from pages.login import show_login
from pages.signup import show_signup
from pages.dashboard import show_dashboard
from database.db_functions import init_connection

# Set page configuration
st.set_page_config(
    page_title="Streamlit Data App",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"  # ✅ Show sidebar by default
)

# ✅ Remove CSS that hides sidebar
# st.markdown("""
#     <style>
#         [data-testid="stSidebar"], .css-1lcbmhc {
#             display: none;
#         }
#     </style>
# """, unsafe_allow_html=True)

# Initialize session state variables
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "login"

def main():
    """Main function to control navigation and authentication"""
    conn = init_connection()

    # ✅ Sidebar Navigation
    with st.sidebar:
        st.title("📊 Navigation")
        
        if st.session_state.authenticated:
            st.success(f"Logged in as {st.session_state.username}")
            if st.button("Dashboard", key="dashboard_button"):
                st.session_state.current_page = "dashboard"
                st.rerun()
            if st.button("Logout", key="logout_button"):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.current_page = "login"
                st.rerun()
        else:
            if st.button("Login", key="login_button_sidebar"):
                st.session_state.current_page = "login"
                st.rerun()
            if st.button("Sign Up", key="signup_button_sidebar"):
                st.session_state.current_page = "signup"
                st.rerun()

    # ✅ Main Page Content
    st.title("📊 Welcome to Data App")

    if not st.session_state.authenticated:
        if st.session_state.current_page == "login":
            show_login()
        elif st.session_state.current_page == "signup":
            show_signup()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()
