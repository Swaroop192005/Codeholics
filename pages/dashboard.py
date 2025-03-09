import streamlit as st
import pandas as pd
import requests
import time
import os
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from matplotlib.colors import Normalize

# Mock functions and data to ensure the app runs without external dependencies
class MockConnection:
    def close(self):
        pass

class MockUser:
    def __init__(self, user_id=1, username="DemoUser", email="demo@example.com", education_level="Bachelor's Degree", about="Learning enthusiast"):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.education_level = education_level
        self.about = about

# Mock database functions
def init_connection():
    return MockConnection()

def get_skills_by_user_id(conn, user_id):
    # Return mock skills
    return ["Python", "Data Science", "Machine Learning", "Web Development"]

def get_user_by_id(conn, user_id):
    return MockUser(user_id=user_id)

def update_user_skills(conn, user_id, skills):
    # Mock function to update skills
    st.session_state.user_skills = skills
    return True

# Path to dataset - using demo data if file doesn't exist
DATASET_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                         "cleaned_udemy_course_dataset.csv")

# Create mock dataset if needed
def create_mock_dataset():
    data = {
        'course_title': [
            'Complete Python Bootcamp', 'Machine Learning A-Z', 'Web Development Bootcamp',
            'Data Science Masterclass', 'JavaScript Essentials', 'React - The Complete Guide',
            'Deep Learning Specialization', 'SQL for Data Analysis', 'Flutter App Development',
            'AWS Certified Solutions Architect'
        ],
        'url': ['https://example.com/course/' + str(i) for i in range(1, 11)],
        'is_paid': [True, True, True, True, False, True, True, False, True, True],
        'price': [94.99, 89.99, 79.99, 129.99, 0, 94.99, 119.99, 0, 84.99, 149.99],
        'num_subscribers': [
            125000, 98000, 110000, 85000, 62000, 105000, 
            78000, 45000, 72000, 92000
        ],
        'level': ['All Levels', 'Intermediate', 'Beginner', 'Advanced', 'Beginner', 
                 'All Levels', 'Advanced', 'Beginner', 'Intermediate', 'Advanced'],
        'content_duration': [35.5, 42.0, 63.5, 55.0, 28.5, 40.5, 38.0, 25.5, 32.0, 45.5]
    }
    return pd.DataFrame(data)

# Load and cache the dataset
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_course_dataset():
    try:
        return pd.read_csv(DATASET_PATH)
    except Exception:
        # Return mock dataset if file doesn't exist
        return create_mock_dataset()

# Cluster functionality
def perform_clustering(df, n_clusters=4):
    # Select features for clustering
    features = df[['price', 'num_subscribers']].copy()
    
    # Handle NaN values
    features = features.fillna(features.mean())
    
    # Scale features
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    
    # Perform KMeans clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df['cluster'] = kmeans.fit_predict(scaled_features)
    
    return df, kmeans, scaler

def get_cluster_descriptions(df_with_clusters):
    """Generate descriptions for each cluster based on their characteristics"""
    # Calculate mean values for each cluster
    cluster_means = df_with_clusters.groupby('cluster').agg({
        'price': 'mean',
        'num_subscribers': 'mean'
    })
    
    descriptions = {}
    for cluster in cluster_means.index:
        price = cluster_means.loc[cluster, 'price']
        popularity = cluster_means.loc[cluster, 'num_subscribers']
        
        # Classify based on price and popularity
        if price < 50:
            price_category = "Budget-friendly"
        elif price < 100:
            price_category = "Mid-range"
        else:
            price_category = "Premium"
            
        if popularity < 50000:
            popularity_category = "Niche"
        elif popularity < 100000:
            popularity_category = "Popular"
        else:
            popularity_category = "Trending"
            
        descriptions[cluster] = f"{popularity_category} {price_category} Courses"
        
    return descriptions

def generate_cluster_plot(df, kmeans_model):
    """Generate a scatter plot of courses colored by cluster"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create color map
    norm = Normalize(vmin=0, vmax=kmeans_model.n_clusters-1)
    scatter = ax.scatter(
        df['price'], 
        df['num_subscribers'],
        c=df['cluster'], 
        cmap='viridis', 
        alpha=0.6, 
        s=50,
        norm=norm
    )
    
    # Add labels and title
    ax.set_xlabel('Course Price ($)', fontsize=12)
    ax.set_ylabel('Number of Subscribers', fontsize=12)
    ax.set_title('Course Clusters by Price and Popularity', fontsize=14)
    
    # Add colorbar legend
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Cluster', fontsize=12)
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Improve aesthetics
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    
    # Convert plot to base64 string
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close(fig)
    
    return base64.b64encode(image_png).decode('utf-8')

def get_course_recommendations_by_cluster(df, cluster_id, n=5):
    """Get top courses from a specific cluster"""
    cluster_df = df[df['cluster'] == cluster_id]
    top_courses = cluster_df.nlargest(n, 'num_subscribers')
    return top_courses

def predict_cluster_for_preferences(price_preference, popularity_preference, kmeans_model, scaler):
    """Predict the most suitable cluster based on user preferences"""
    # Create a sample with user preferences
    user_preferences = np.array([[price_preference, popularity_preference]])
    
    # Scale the preferences
    scaled_preferences = scaler.transform(user_preferences)
    
    # Predict the cluster
    predicted_cluster = kmeans_model.predict(scaled_preferences)[0]
    
    return predicted_cluster

# Function to get popular courses from the dataset
def get_popular_courses_from_dataset(df, n=5):
    try:
        top_courses = df.nlargest(n, 'num_subscribers')[['course_title', 'url', 'is_paid', 'price', 'num_subscribers']]
        return top_courses
    except Exception as e:
        st.error(f"Error loading popular courses: {e}")
        return pd.DataFrame()

# Function to mock recommendations
def get_recommendations(skills):
    """Mock function to get course recommendations based on skills"""
    if not skills:
        return []
        
    all_recommendations = []
    df = load_course_dataset()
    
    # Show a progress indicator
    with st.spinner("Fetching course recommendations..."):
        for skill in skills:
            # Mock recommendations by filtering dataset
            matching_courses = df[df['course_title'].str.contains(skill, case=False)].head(2)
            if not matching_courses.empty:
                for _, course in matching_courses.iterrows():
                    all_recommendations.append({
                        'course_title': course['course_title'],
                        'is_paid': course['is_paid'],
                        'price': course['price'],
                        'num_subscribers': course['num_subscribers'],
                        'url': course['url'],
                        'recommended_for': skill
                    })
            
            # Add more mock recommendations if needed
            if skill.lower() == 'python':
                all_recommendations.append({
                    'course_title': 'Advanced Python Programming',
                    'is_paid': True,
                    'price': 89.99,
                    'num_subscribers': 75000,
                    'url': 'https://example.com/advanced-python',
                    'recommended_for': skill
                })
            elif skill.lower() == 'data science':
                all_recommendations.append({
                    'course_title': 'Data Science: R Programming',
                    'is_paid': True,
                    'price': 94.99,
                    'num_subscribers': 65000,
                    'url': 'https://example.com/r-programming',
                    'recommended_for': skill
                })
                
    # Remove duplicates based on course_title
    unique_recommendations = []
    seen_titles = set()
    
    for rec in all_recommendations:
        if rec['course_title'] not in seen_titles:
            seen_titles.add(rec['course_title'])
            unique_recommendations.append(rec)
            
    return unique_recommendations

# Perform and cache clustering
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_clustered_data(n_clusters=4):
    df = load_course_dataset()
    if df.empty:
        return None, None, None
    
    df_with_clusters, kmeans_model, scaler = perform_clustering(df, n_clusters)
    return df_with_clusters, kmeans_model, scaler

# Add custom CSS for modern styling
def add_custom_styles():
    st.markdown(
        """
        <style>
        /* General styling for the tab container */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px; /* Space between tabs */
            padding: 8px 0; /* Padding around the tab list */
            background-color: transparent; /* Transparent background for the tab container */
            border-bottom: 2px solid #e0e0e0; /* Add a subtle line below the tabs */
        }

        /* Individual tab styling */
        .stTabs [data-baseweb="tab"] {
            padding: 10px 20px; /* Padding inside each tab */
            border-radius: 8px; /* Rounded corners for all tabs */
            background-color: #f8f9fa; /* Light background for inactive tabs */
            color: #333; /* Default text color */
            font-weight: 500; /* Medium font weight */
            transition: all 0.3s ease; /* Smooth transition for hover effects */
            border: 1px solid #e0e0e0; /* Light border */
            margin: 0 2px; /* Add a small margin between tabs */
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

        /* Card styling */
        .course-card {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            background-color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }

        .course-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        }

        /* Skill chip styling */
        .skill-chip {
            display: inline-block;
            background-color: #e3f2fd;
            color: #1976d2;
            padding: 5px 15px;
            border-radius: 20px;
            margin: 3px;
            font-size: 0.85rem;
            font-weight: 500;
        }

        /* Button styling */
        .stButton>button {
            background-color: #1E88E5;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 8px 16px;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        .stButton>button:hover {
            background-color: #1565C0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
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

# Initialize session state variables
def init_session_state():
    if "user_id" not in st.session_state:
        st.session_state.user_id = 1
    if "username" not in st.session_state:
        st.session_state.username = "DemoUser"
    if "preferred_cluster" not in st.session_state:
        st.session_state.preferred_cluster = 0
    if "user_skills" not in st.session_state:
        st.session_state.user_skills = get_skills_by_user_id(None, st.session_state.user_id)
    if "show_login" not in st.session_state:
        st.session_state.show_login = False

# Streamlit Dashboard
def show_dashboard():
    # Initialize session state
    init_session_state()
    
    # Add custom styles
    add_custom_styles()
    
    # Login screen (for demo purposes)
    if st.session_state.show_login:
        st.title("🧠 SkillSphere - Login")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            username = st.text_input("Username", "DemoUser")
            password = st.text_input("Password", type="password", value="password123")
            
            if st.button("Login"):
                st.session_state.username = username
                st.session_state.show_login = False
                st.rerun()
                
        with col2:
            st.image("https://via.placeholder.com/300x150?text=SkillSphere", use_column_width=True)
            st.markdown("#### Your Learning Journey Starts Here!")
            st.markdown("Discover courses based on your skills and preferences.")
            
        st.markdown("---")
        st.markdown("#### Demo Mode")
        if st.button("Continue as Demo User"):
            st.session_state.show_login = False
            st.rerun()
            
        return

    # Main dashboard
    st.title("🧠 SkillSphere")
    
    # Get logged-in user details from session
    user_id = st.session_state.user_id
    username = st.session_state.username
    
    # Welcome message with user's name
    st.markdown(f"### Welcome back, {username}! 👋")
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Recommendations", "Popular Courses", "Course Clusters", "Profile"])
    
    # Initialize database connection
    conn = init_connection()
    
    # Fetch user skills from session state (for demo)
    skills = st.session_state.user_skills
    
    # Load clustered data
    df_with_clusters, kmeans_model, scaler = get_clustered_data()
    
    with tab1:
        # Display user skills
        if skills:
            st.markdown("### Your Skills")
            skill_cols = st.columns(min(len(skills), 4))
            for i, skill in enumerate(skills):
                with skill_cols[i % min(len(skills), 4)]:
                    st.markdown(f'<div class="skill-chip">🔹 {skill}</div>', unsafe_allow_html=True)

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
                fallback_courses = get_popular_courses_from_dataset(load_course_dataset(), 3)
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
        dataset = load_course_dataset()
        top_courses = get_popular_courses_from_dataset(dataset, 10)
        
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
                        st.markdown(f'<div class="skill-chip">{skill}</div>', unsafe_allow_html=True)
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
                    if new_skill.strip() not in updated_skills:
                        updated_skills.append(new_skill.strip())
                        
                        # Update in session state
                        st.session_state.user_skills = updated_skills
                        st.success(f"Added skill: {new_skill}")
                        
                        # Refresh page to show updated skills
                        st.rerun()
                    else:
                        st.warning(f"Skill '{new_skill}' already exists!")
                else:
                    st.warning("Please enter a valid skill")
                    
            # Option to remove skills
            if skills:
                st.markdown("### Remove Skills")
                skill_to_remove = st.selectbox("Select skill to remove:", skills)
                if st.button("Remove Selected Skill"):
                    updated_skills = [s for s in skills if s != skill_to_remove]
                    st.session_state.user_skills = updated_skills
                    st.success(f"Removed skill: {skill_to_remove}")
                    st.rerun()
        else:
            st.error("Could not load user profile")
            
        # Add a logout button
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.show_login = True
            st.rerun()
    
    # Close database connection
    conn.close()

if __name__ == "__main__":
    show_dashboard()