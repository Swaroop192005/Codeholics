import streamlit as st
from database.db_functions import init_connection
from database.models import User

def show_login():
    """Display the login page with a modern UI and better alignment"""
    # Add custom CSS for modern styling
    st.markdown("""
        <style>
            /* Title styling */
            .login-title {
                text-align: center;
                font-size: 2rem;
                font-weight: 600;
                color: #1E88E5;
                margin-bottom: 1.5rem;
            }
            /* Form container styling */
            .login-form {
                background-color: white;
                padding: 2rem;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                border: 1px solid #e0e0e0;
                margin: 0 auto;
                max-width: 400px;
            }
            /* Input field styling */
            .stTextInput input, .stTextInput input:focus {
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 0.5rem;
                font-size: 1rem;
                transition: border-color 0.3s ease;
                width: 100%;
            }
            .stTextInput input:focus {
                border-color: #1E88E5;
                box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.2);
            }
            /* Button styling */
            .stButton button {
                background-color: #1E88E5;
                color: white;
                border-radius: 8px;
                padding: 0.5rem 1rem;
                font-size: 1rem;
                transition: background-color 0.3s ease;
                width: 100%;
            }
            .stButton button:hover {
                background-color: #1565C0;
            }
            /* Error message styling */
            .stAlert {
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 1rem;
            }
            /* Dark mode support */
            @media (prefers-color-scheme: dark) {
                .login-title {
                    color: #90CAF9;
                }
                .login-form {
                    background-color: #1e1e1e;
                    border-color: #333;
                }
                .stTextInput input, .stTextInput input:focus {
                    background-color: #333;
                    border-color: #555;
                    color: white;
                }
                .stTextInput input:focus {
                    border-color: #90CAF9;
                }
                .stButton button {
                    background-color: #90CAF9;
                    color: #1e1e1e;
                }
                .stButton button:hover {
                    background-color: #64B5F6;
                }
            }
        </style>
    """, unsafe_allow_html=True)

    # Center the title and form
    st.markdown('<div class="login-title">🔐 Login to Your Account</div>', unsafe_allow_html=True)
    
    # Center the form using columns
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=True):
            st.markdown("### Enter your credentials")
            
            # Email input
            email = st.text_input(
                "Email", 
                placeholder="your.email@example.com",
                key="login_email"
            )
            
            # Password input
            password = st.text_input(
                "Password", 
                type="password", 
                placeholder="••••••••",
                key="login_password"
            )
            
            # Login button
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
                        # Successful login - Store session state variables
                        st.session_state.authenticated = True
                        st.session_state.username = user.username
                        st.session_state.user_id = user.id
                        st.session_state.current_page = "dashboard"
                        
                        # Debug information
                        st.success(f"Login successful! Welcome back, {user.username}.")
                        st.info("Redirecting to dashboard...")
                        
                        # Force a rerun to apply the session state changes
                        conn.close()
                        st.rerun()
                    else:
                        st.error("Invalid email or password")
                    
                    conn.close()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Link to signup page with better styling
        st.markdown("---")
        st.markdown("Don't have an account?")
        if st.button("Create Account", key="signup_button_login", use_container_width=True):
            st.session_state.current_page = "signup"
            st.rerun()