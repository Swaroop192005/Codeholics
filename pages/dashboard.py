import streamlit as st
import pandas as pd
import requests
import time
from utils.auth import login_required
from database.db_functions import init_connection, get_skills_by_user_id, get_user_by_id
from database.models import User

# Define API endpoint (Flask server)
API_URL = "http://127.0.0.1:5000"

# Function to fetch course recommendations based on skills
def get_recommendations(skills):
    """Fetch recommended courses from Flask API based on skills"""
    if not skills:
        return []
        
    all_recommendations = []
    
    # Show a progress indicator
    with st.spinner("Fetching course recommendations..."):
        for skill in skills:
            try:
                # Clean up the skill string (remove whitespace, lowercase)
                clean_skill = skill.strip().lower()
                if not clean_skill:
                    continue
                    
                # Make the API request
                response = requests.get(f"{API_URL}/recommend?course_title={clean_skill}", timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    # Add the skill as a source to each recommendation
                    for course in data:
                        course['recommended_for'] = skill
                    all_recommendations.extend(data)
                else:
                    st.warning(f"Failed to fetch recommendations for skill: {skill} (Status: {response.status_code})")
            except requests.exceptions.RequestException as e:
                st.error(f"API request failed for skill '{skill}': {e}")
                
    # Remove duplicates based on course_title
    unique_recommendations = []
    seen_titles = set()
    
    for rec in all_recommendations:
        if rec['course_title'] not in seen_titles:
            seen_titles.add(rec['course_title'])
            unique_recommendations.append(rec)
            
    return unique_recommendations

# Function to get popular courses from the dataset
def get_popular_courses_from_dataset(file_path, n=5):
    try:
        df = pd.read_csv(file_path)
        top_courses = df.nlargest(n, 'num_subscribers')[['course_title', 'url', 'is_paid', 'price', 'num_subscribers']]
        return top_courses
    except Exception as e:
        st.error(f"Error loading popular courses: {e}")
        return pd.DataFrame()

# Streamlit Dashboard
@login_required  # Protect dashboard with authentication
def show_dashboard():
    st.title("📚 Your Learning Dashboard")
    
    # Get logged-in user details from session
    user_id = st.session_state.get("user_id")
    username = st.session_state.get("username", "User")
    
    # Welcome message with user's name
    st.markdown(f"### Welcome back, {username}! 👋")
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Recommendations", "Popular Courses", "Profile"])
    
    # ...existing code...

    # ...existing code...

    with tab1:
        # Fetch user skills directly from database
        conn = init_connection()
        skills = get_skills_by_user_id(conn, user_id)

        # Debug information
        st.write(f"Debug - User Skills: {skills}")

        # Display user skills
        if skills:
            st.markdown("### Your Skills")
            skill_cols = st.columns(min(len(skills), 4))
            for i, skill in enumerate(skills):
                with skill_cols[i % min(len(skills), 4)]:
                    st.markdown(f"🔹 **{skill}**")

        # Recommendation courses based on current user skills
        st.markdown("### Recommended Courses")

        if not skills:
            st.info("You haven't added any skills yet. Add skills to get personalized recommendations.")
        else:
            recommendations = get_recommendations(skills)

            if recommendations:
                # Create a grid layout for recommendations
                for i in range(0, len(recommendations), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(recommendations):
                            rec = recommendations[i + j]
                            with cols[j]:
                                with st.container(border=True):
                                    st.markdown(f"#### {rec['course_title']}")
                                    st.markdown(f"**Based on your skill:** {rec.get('recommended_for', 'Your profile')}")
                                    st.markdown(f"**Price:** {'Free' if not rec.get('is_paid') else f'${rec.get('price', 'N/A')}'}")
                                    num_subscribers = rec.get('num_subscribers', 'N/A')
                                    if isinstance(num_subscribers, int):
                                        num_subscribers = f"{num_subscribers:,}"
                                    st.markdown(f"**Subscribers:** {num_subscribers}")
                                    course_url = rec.get('url', '#')
                                    st.markdown(f"[View Course]({course_url})")
                else:
                    st.warning("No recommendations found. The recommendation service might be unavailable.")

                    # Fallback to popular courses if no recommendations
                    st.markdown("### Try these popular courses instead:")
                    dataset_path = 'c:\\web-proj\\hackathon_2\\self_learning\\data\\cleaned_udemy_course_dataset.csv'
                    fallback_courses = get_popular_courses_from_dataset(dataset_path, 3)
                    if not fallback_courses.empty:
                        st.dataframe(fallback_courses, hide_index=True, use_container_width=True)

                # ...existing code...
    
    with tab2:
        st.markdown("### 🔥 Top Trending Courses")
        dataset_path = 'c:\\web-proj\\hackathon_2\\self_learning\\data\\cleaned_udemy_course_dataset.csv'
        top_courses = get_popular_courses_from_dataset(dataset_path, 10)
        
        if not top_courses.empty:
            # Format the dataframe for better display
            formatted_courses = top_courses.copy()
            formatted_courses['price'] = formatted_courses.apply(
                lambda x: 'Free' if not x['is_paid'] else f"${x['price']}", axis=1
            )
            formatted_courses['num_subscribers'] = formatted_courses['num_subscribers'].apply(lambda x: f"{x:,}")
            formatted_courses = formatted_courses.rename(columns={
                'course_title': 'Course Title',
                'url': 'URL',
                'price': 'Price',
                'num_subscribers': 'Subscribers'
            })
            formatted_courses = formatted_courses.drop(columns=['is_paid'])
            
            st.dataframe(formatted_courses, hide_index=True, use_container_width=True)
        else:
            st.warning("Unable to load popular courses. Please check the dataset path.")
    
    with tab3:
        st.markdown("### Your Profile")
        
        # Get full user details
        user = get_user_by_id(conn, user_id)
        
        if user:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Username:** {user.username}")
                st.markdown(f"**Email:** {user.email}")
                st.markdown(f"**Education:** {user.education_level or 'Not specified'}")
            
            with col2:
                st.markdown("**Skills:**")
                if skills:
                    for skill in skills:
                        st.markdown(f"- {skill}")
                else:
                    st.markdown("No skills added yet")
            
            if user.about:
                st.markdown("**About:**")
                st.markdown(f"> {user.about}")
        else:
            st.error("Could not load user profile")

    conn.close()

if __name__ == "__main__":
    show_dashboard()

