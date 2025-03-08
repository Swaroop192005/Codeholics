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
    st.title("Create a New Account")

    # Center the form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("signup_form", clear_on_submit=True):
            # Basic account information
            st.subheader("Account Information")
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")

            # # Experience level
            # st.subheader("Professional Information")
            # experience_options = ["Entry Level (0-2 years)", "Mid Level (3-5 years)", 
            #                       "Senior Level (6-10 years)", "Expert (10+ years)"]
            # experience_level = st.selectbox("Experience Level", experience_options)

            # Skills section (multi-select)
            st.subheader("Skills")
            skill_options = ["Python", "Java", "C++", "SQL", "Web Development", 
                            "Machine Learning", "Data Analysis", "Cybersecurity", 
                            "Project Management", "Other"]
            skills = st.multiselect("Select Your Skills", skill_options)

            # Education
            education_level = st.selectbox("Highest Education Level", 
                                           ["High School", "Associate's Degree", 
                                            "Bachelor's Degree", "Master's Degree", 
                                            "PhD", "Other"])

            # About section
            about = st.text_area("Brief Bio", 
                                height=100, 
                                help="Tell us a bit about yourself (max 500 characters)")

            # Terms and conditions
            terms_agree = st.checkbox("I agree to the Terms and Conditions")

            submit = st.form_submit_button("Sign Up")

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
                            # experience_level=experience_level,
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
        st.write("Already have an account?")
        if st.button("Login"):
            st.session_state.current_page = "login"
            st.rerun()
