import streamlit as st
import pandas as pd
import requests
import time
import os
from utils.auth import login_required
from database.db_functions import init_connection, get_skills_by_user_id, get_user_by_id, update_user_skills
from database.models import User
from Cluster import (
    perform_clustering, 
    get_cluster_descriptions, 
    generate_cluster_plot,
    get_course_recommendations_by_cluster,
    predict_cluster_for_preferences
)

# Define API endpoint (Flask server)
API_URL = "http://127.0.0.1:5000"

# Path to dataset
DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                         "data", "cleaned_udemy_course_dataset.csv")

# Add custom CSS for modern styling
st.markdown(
    """
    <style>
    /* General styling for the tab container */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px; /* Space between tabs */
        padding: 10px 0; /* Padding around the tab list */
        border-bottom: 2px solid #e0e0e0; /* Add a subtle line below the tabs */
    }

    /* Individual tab styling */
    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px; /* Padding inside each tab */
        border-radius: 8px 8px 0 0; /* Rounded corners only at the top */
        background-color: #f8f9fa; /* Light background for inactive tabs */
        color: #333; /* Default text color */
        font-weight: 500; /* Medium font weight */
        transition: all 0.3s ease; /* Smooth transition for hover effects */
        border: 1px solid #e0e0e0; /* Light border */
        border-bottom: none; /* Remove bottom border to blend with the container */
    }

    /* Hover effect for tabs */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e9ecef; /* Slightly darker background on hover */
        color: #1E88E5; /* Change text color on hover */
        transform: translateY(-2px); /* Slight lift effect */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Subtle shadow */
    }

    /* Active tab styling */
    .stTabs [aria-selected="true"] {
        background-color: #ffffff; /* White background for active tab */
        color: #1E88E5; /* Primary color for active tab text */
        border-color: #e0e0e0; /* Border color matches the container */
        border-bottom: 2px solid #1E88E5; /* Add a colored line below the active tab */
        box-shadow: 0 4px 12px rgba(30, 136, 229, 0.1); /* Glow effect */
    }

    /* Dark mode support for tabs */
    @media (prefers-color-scheme: dark) {
        .stTabs [data-baseweb="tab"] {
            background-color: #2d2d2d; /* Dark background for tabs */
            color: #e0e0e0; /* Light text color */
            border-color: #444; /* Darker border */
        }

        .stTabs [data-baseweb="tab"]:hover {
            background-color: #3d3d3d; /* Slightly lighter on hover */
            color: #1E88E5; /* Primary color for hover text */
        }

        .stTabs [aria-selected="true"] {
            background-color: #1e1e1e; /* Dark background for active tab */
            color: #1E88E5; /* Primary color for active tab text */
            border-bottom: 2px solid #1E88E5; /* Colored line below active tab */
        }
    }
</style>
""", unsafe_allow_html=True)

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

# Load and cache the dataset
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_course_dataset():
    try:
        return pd.read_csv(DATASET_PATH)
    except Exception as e:
        st.error(f"Error loading course dataset: {e}")
        return pd.DataFrame()

# Perform and cache clustering
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_clustered_data(n_clusters=4):
    df = load_course_dataset()
    if df.empty:
        return None, None, None
    
    df_with_clusters, kmeans_model, scaler = perform_clustering(df, n_clusters)
    return df_with_clusters, kmeans_model, scaler

# Streamlit Dashboard
@login_required  # Protect dashboard with authentication
def show_dashboard():
    st.title("🧠 SkillSphere")
    
    # Get logged-in user details from session
    user_id = st.session_state.get("user_id")
    username = st.session_state.get("username", "User")
    
    # Welcome message with user's name
    st.markdown(f"### Welcome back, {username}! 👋")
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Recommendations", "Popular Courses", "Course Clusters", "Profile"])
    
    # Initialize database connection
    conn = init_connection()
    
    # Fetch user skills
    skills = get_skills_by_user_id(conn, user_id)
    
    # Load clustered data
    df_with_clusters, kmeans_model, scaler = get_clustered_data()
    
    # Store user's preferred cluster if set
    if "preferred_cluster" not in st.session_state:
        st.session_state.preferred_cluster = 0  # Default cluster
    
    with tab1:
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
                fallback_courses = get_popular_courses_from_dataset(DATASET_PATH, 3)
                if not fallback_courses.empty:
                    st.dataframe(fallback_courses, hide_index=True, use_container_width=True)
        
        # Cluster-based recommendations
        if df_with_clusters is not None and not df_with_clusters.empty:
            st.markdown("### Recommended Courses Based on Your Preferences")
            
            cluster_descriptions = get_cluster_descriptions(df_with_clusters)
            preferred_cluster = st.session_state.preferred_cluster
            
            st.info(f"Showing courses from your preferred category: **{cluster_descriptions.get(preferred_cluster, 'Unknown')}**")
            
            # Get recommendations from preferred cluster
            cluster_recommendations = get_course_recommendations_by_cluster(df_with_clusters, preferred_cluster, 4)
            
            if not cluster_recommendations.empty:
                # Create a grid layout for cluster recommendations
                for i in range(0, len(cluster_recommendations), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(cluster_recommendations):
                            rec = cluster_recommendations.iloc[i + j]
                            with cols[j]:
                                with st.container(border=True):
                                    st.markdown(f"#### {rec['course_title']}")
                                    st.markdown(f"**Price:** {'Free' if not rec['is_paid'] else f'${rec['price']}'}")
                                    st.markdown(f"**Subscribers:** {rec['num_subscribers']:,}")
                                    st.markdown(f"[View Course]({rec['url']})")
    
    with tab2:
        st.markdown("### 🔥 Top Trending Courses")
        top_courses = get_popular_courses_from_dataset(DATASET_PATH, 10)
        
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
        st.markdown("### 📊 Course Clusters Analysis")
        
        if df_with_clusters is None or df_with_clusters.empty:
            st.error("Could not load course data for clustering. Please check the dataset path.")
        else:
            # Get cluster descriptions
            cluster_descriptions = get_cluster_descriptions(df_with_clusters)
            
            # Generate and display cluster plot
            st.markdown("#### Course Distribution by Price and Popularity")
            cluster_plot = generate_cluster_plot(df_with_clusters, kmeans_model)
            st.image(f"data:image/png;base64,{cluster_plot}", use_column_width=True)
            
            # Display cluster information
            st.markdown("#### Course Categories")
            cluster_info = []
            for cluster, description in cluster_descriptions.items():
                count = len(df_with_clusters[df_with_clusters['cluster'] == cluster])
                avg_price = df_with_clusters[df_with_clusters['cluster'] == cluster]['price'].mean()
                avg_subscribers = df_with_clusters[df_with_clusters['cluster'] == cluster]['num_subscribers'].mean()
                cluster_info.append({
                    "Cluster": cluster,
                    "Description": description,
                    "Count": count,
                    "Avg. Price": f"${avg_price:.2f}",
                    "Avg. Subscribers": f"{int(avg_subscribers):,}"
                })
            
            # Display as dataframe
            st.dataframe(pd.DataFrame(cluster_info), hide_index=True, use_container_width=True)
            
            # User preference settings
            st.markdown("#### Set Your Course Preferences")
            st.write("This will help us recommend courses that match your learning style.")
            
            col1, col2 = st.columns(2)
            with col1:
                price_preference = st.slider("Price Range:", 0, 200, 50, help="Select your preferred price range")
            with col2:
                popularity_preference = st.slider("Course Popularity:", 0, 200000, 50000, step=10000, 
                                              help="Higher values mean more popular courses with more students")
            
            # Predict user's preferred cluster based on preferences
            if kmeans_model is not None and scaler is not None:
                preferred_cluster = predict_cluster_for_preferences(price_preference, popularity_preference, kmeans_model, scaler)
                st.session_state.preferred_cluster = preferred_cluster
                
                st.success(f"Based on your preferences, we've selected the '{cluster_descriptions.get(preferred_cluster, 'Unknown')}' category for your recommendations!")
            
            # Show top courses for selected cluster
            st.markdown("#### Top Courses in Your Preferred Category")
            preferred_courses = get_course_recommendations_by_cluster(df_with_clusters, st.session_state.preferred_cluster, 5)
            
            if not preferred_courses.empty:
                # Format the preferred courses dataframe
                formatted_preferred = preferred_courses.copy()
                formatted_preferred['price'] = formatted_preferred.apply(
                    lambda x: 'Free' if not x['is_paid'] else f"${x['price']}", axis=1
                )
                formatted_preferred['num_subscribers'] = formatted_preferred['num_subscribers'].apply(lambda x: f"{x:,}")
                formatted_preferred = formatted_preferred.rename(columns={
                    'course_title': 'Course Title',
                    'url': 'URL',
                    'price': 'Price',
                    'num_subscribers': 'Subscribers'
                })
                formatted_preferred = formatted_preferred.drop(columns=['is_paid', 'cluster'])
                
                st.dataframe(formatted_preferred, hide_index=True, use_container_width=True)
    
    with tab4:
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
                
            # Add skill management
            st.markdown("### Manage Your Skills")
            new_skill = st.text_input("Add a new skill:")
            if st.button("Add Skill"):
                if new_skill.strip():
                    updated_skills = skills.copy() if skills else []
                    updated_skills.append(new_skill.strip())
                    
                    # Update in database
                    update_user_skills(conn, user_id, updated_skills)
                    st.success(f"Added skill: {new_skill}")
                    
                    # Refresh page to show updated skills
                    st.rerun()
                else:
                    st.warning("Please enter a valid skill")
        else:
            st.error("Could not load user profile")
    
    # Close database connection
    conn.close()

if __name__ == "__main__":
    show_dashboard()