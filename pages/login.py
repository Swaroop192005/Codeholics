import streamlit as st
from database.db_functions import init_connection
from database.models import User

def show_login():
    """Display the login page"""
    st.title("🔐 Login to Your Account")
    
    # Center the form with a card-like appearance
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form", clear_on_submit=True):
            st.markdown("### Enter your credentials")
            email = st.text_input("Email", placeholder="your.email@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if not email or not password:
                    st.error("Please enter both email and password")
                else:
                    # Connect to database
                    conn = init_connection()
                    
                    # Check if user exists
                    user = User.get_by_email(conn, email)
                    
                    if user and user.check_password(password):
                        # Successful login - Store ALL necessary session state variables
                        st.session_state.authenticated = True
                        st.session_state.username = user.username
                        st.session_state.user_id = user.id
                        st.session_state.current_page = "dashboard"
                        
                        # Debug information
                        st.success(f"Login successful! User ID: {user.id}, Username: {user.username}")
                        st.info("Redirecting to dashboard...")
                        
                        # Force a rerun to apply the session state changes
                        conn.close()
                        st.rerun()
                    else:
                        st.error("Invalid email or password")
                    
                    conn.close()
        
        # Link to signup page with better styling
        st.markdown("---")
        st.markdown("Don't have an account?")
        if st.button("Create Account", key="signup_button_login", use_container_width=True):
            st.session_state.current_page = "signup"
            st.rerun()
