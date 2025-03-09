import streamlit as st
from database.db_functions import init_connection
from database.models import User
import re

def is_valid_email(email):
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None

def show_signup():
    """Display the signup page with skills and professional information"""
    st.title("🚀 Create Your Learning Account")

    # Center the form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("signup_form", clear_on_submit=True):
            # Basic account information
            st.subheader("Account Information")
            username = st.text_input("Username", placeholder="Choose a unique username")
            email = st.text_input("Email", placeholder="your.email@example.com")
            
            # Password fields side by side
            pw_col1, pw_col2 = st.columns(2)
            with pw_col1:
                password = st.text_input("Password", type="password", placeholder="••••••••")
            with pw_col2:
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••")

            # Skills section (multi-select)
            st.subheader("Skills")
            st.markdown("Select skills to get personalized course recommendations")
            skill_options = [
                "Investment Banking", "GST", "Financial Modeling", "Financial Analysis",
                "Trading Options", "Penny Stocks", "Price Charts", "Stock Chart Patterns",
                "Advanced Stock Profit", "Investment Strategy", "Forex Trading",
                "Money Flow", "Risk and Return", "Trading Robot", "Accounting",
                "Cryptocurrency", "Python", "Machine Learning", "Data Analysis",
                "Web Development", "Cybersecurity", "Project Management", "Java", "JavaScript"
            ]
            skills = st.multiselect("Select Your Skills", skill_options)

            # Education
            st.subheader("Education")
            education_level = st.selectbox("Highest Education Level", 
                                           ["High School", "Associate's Degree", 
                                            "Bachelor's Degree", "Master's Degree", 
                                            "PhD", "Other"])

            # About section
            st.subheader("About You")
            about = st.text_area("Brief Bio", 
                                placeholder="Tell us a bit about yourself and your learning goals",
                                height=100, 
                                help="Max 500 characters")

            # Terms and conditions
            terms_agree = st.checkbox("I agree to the Terms and Conditions")

            submit = st.form_submit_button("Create Account", use_container_width=True)

            if submit:
                # Input validation
                error = False

                if not username or not email or not password or not confirm_password:
                    st.error("Please fill out all required fields")
                    error = True

                elif not is_valid_email(email):
                    st.error("Please enter a valid email address")
                    error = True

                elif password != confirm_password:
                    st.error("Passwords do not match")
                    error = True

                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long")
                    error = True

                elif not terms_agree:
                    st.error("You must agree to the Terms and Conditions")
                    error = True

                if not error:
                    # Connect to database
                    conn = init_connection()

                    # Check if user already exists
                    if User.email_exists(conn, email):
                        st.error("Email already registered")
                    elif User.username_exists(conn, username):
                        st.error("Username already taken")
                    else:
                        # Create new user
                        user = User(
                            username=username,
                            email=email,
                            skills=", ".join(skills),
                            education_level=education_level,
                            about=about
                        )
                        user.set_password(password)
                        user.save(conn)

                        st.success("Account created successfully!")

                        # Redirect to login page
                        st.session_state.current_page = "login"
                        st.rerun()

        # Link to login page
        st.markdown("---")
        st.markdown("Already have an account?")
        if st.button("Login", use_container_width=True):
            st.session_state.current_page = "login"
            st.rerun()

