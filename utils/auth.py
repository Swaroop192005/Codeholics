import streamlit as st
import functools

def login_required(func):
    """Decorator to ensure user is authenticated before accessing a page"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Check if user is authenticated
        if not st.session_state.get("authenticated", False):
            st.warning("Please login to access this page")
            st.session_state.current_page = "login"
            st.rerun()
            return None
        
        # Check if user_id is set
        if not st.session_state.get("user_id"):
            st.error("Session error: User ID not found")
            st.session_state.authenticated = False
            st.session_state.current_page = "login"
            st.rerun()
            return None
            
        # If all checks pass, call the original function
        return func(*args, **kwargs)
    return wrapper

