import streamlit as st
from functools import wraps

def login_required(func):
    """Decorator to check if user is authenticated"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not st.session_state.get("authenticated", False):
            st.error("Please login to access this page")
            st.session_state.current_page = "login"
            st.experimental_rerun()
        return func(*args, **kwargs)
    return wrapper