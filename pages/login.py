import streamlit as st
from database.db_functions import init_connection
from database.models import User

def show_login():
    """Display the login page"""
    st.title("Login to Data App")
    
    # Center the form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form", clear_on_submit=True):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if not email or not password:
                    st.error("Please enter both email and password")
                else:
                    # Connect to database
                    conn = init_connection()
                    
                    # Check if user exists
                    user = User.get_by_email(conn, email)
                    
                    if user and user.check_password(password):
                        # Successful login
                        st.session_state.authenticated = True
                        st.session_state.username = user.username
                        st.session_state.current_page = "dashboard"
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password")
        
        # Link to signup page
        st.write("Don't have an account?")
        if st.button("Sign Up", key="signup_button_login"):  # Unique key
            st.session_state.current_page = "signup"
            st.rerun()
