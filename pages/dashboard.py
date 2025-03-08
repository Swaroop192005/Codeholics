import streamlit as st
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from PIL import Image
import io
import json



# Define API endpoint (would point to FastAPI server in production)
API_URL = "http://localhost:8000"

# Mock API response for hackathon demo

def show_dashboard():
    @st.cache_data
    def get_mock_user_data():
        return {
            "U001": {"name": "Alice Smith", "title": "Data Science Student"},
            "U002": {"name": "Bob Johnson", "title": "Software Developer"},
            "U003": {"name": "Carol Williams", "title": "Product Manager"},
            "U004": {"name": "Dave Brown", "title": "UX Designer"},
            "U005": {"name": "Eve Davis", "title": "DevOps Engineer"}
        }
    
    @st.cache_data
    def get_mock_learning_path(user_id):
        # Different paths for different users
        paths = {
            "U001": {
                "user_id": "U001",
                "courses": [
                    {"course_id": "C001", "title": "Advanced Python Programming", "skills_covered": ["Python", "Data Structures", "Algorithms"], "duration_hours": 25, "difficulty_level": 4.2},
                    {"course_id": "C015", "title": "Machine Learning Fundamentals", "skills_covered": ["Machine Learning", "Python", "Mathematics"], "duration_hours": 30, "difficulty_level": 4.5},
                    {"course_id": "C022", "title": "Data Visualization", "skills_covered": ["Data Visualization", "Python", "Statistics"], "duration_hours": 20, "difficulty_level": 3.8},
                    {"course_id": "C031", "title": "Deep Learning", "skills_covered": ["Deep Learning", "Neural Networks", "Python"], "duration_hours": 40, "difficulty_level": 4.8},
                    {"course_id": "C042", "title": "Natural Language Processing", "skills_covered": ["NLP", "Python", "Deep Learning"], "duration_hours": 35, "difficulty_level": 4.6}
                ],
                "expected_skills": ["Data Structures", "Algorithms", "Machine Learning", "Data Visualization", "Statistics", "Deep Learning", "Neural Networks", "NLP"],
                "total_duration": 150,
                "career_alignment": 0.85,
                "peer_recommendations": ["U012", "U045", "U078"]
            },
            "U002": {
                "user_id": "U002",
                "courses": [
                    {"course_id": "C003", "title": "Web Development with React", "skills_covered": ["React", "JavaScript", "Web Development"], "duration_hours": 25, "difficulty_level": 3.9},
                    {"course_id": "C014", "title": "Backend Development with Node.js", "skills_covered": ["Node.js", "JavaScript", "APIs"], "duration_hours": 28, "difficulty_level": 4.0},
                    {"course_id": "C025", "title": "DevOps Fundamentals", "skills_covered": ["DevOps", "CI/CD", "Docker"], "duration_hours": 22, "difficulty_level": 4.2},
                    {"course_id": "C037", "title": "Cloud Computing with AWS", "skills_covered": ["AWS", "Cloud Computing", "Serverless"], "duration_hours": 30, "difficulty_level": 4.1},
                    {"course_id": "C049", "title": "Microservices Architecture", "skills_covered": ["Microservices", "System Design", "APIs"], "duration_hours": 35, "difficulty_level": 4.6}
                ],
                "expected_skills": ["React", "Node.js", "APIs", "DevOps", "CI/CD", "Docker", "AWS", "Cloud Computing", "Serverless", "Microservices", "System Design"],
                "total_duration": 140,
                "career_alignment": 0.9,
                "peer_recommendations": ["U023", "U056", "U089"]
            },
            "U003": {
                "user_id": "U003",
                "courses": [
                    {"course_id": "C007", "title": "Product Management Fundamentals", "skills_covered": ["Product Management", "Strategy", "Requirements"], "duration_hours": 20, "difficulty_level": 3.5},
                    {"course_id": "C019", "title": "Agile Methodologies", "skills_covered": ["Agile", "Scrum", "Kanban"], "duration_hours": 15, "difficulty_level": 3.2},
                    {"course_id": "C028", "title": "User Research", "skills_covered": ["User Research", "Interviews", "Surveys"], "duration_hours": 18, "difficulty_level": 3.4},
                    {"course_id": "C036", "title": "Product Analytics", "skills_covered": ["Analytics", "KPIs", "Data Analysis"], "duration_hours": 22, "difficulty_level": 3.8},
                    {"course_id": "C044", "title": "Product Strategy", "skills_covered": ["Product Strategy", "Roadmapping", "Competitive Analysis"], "duration_hours": 25, "difficulty_level": 4.0}
                ],
                "expected_skills": ["Product Management", "Strategy", "Requirements", "Agile", "Scrum", "Kanban", "User Research", "Analytics", "KPIs", "Roadmapping", "Competitive Analysis"],
                "total_duration": 100,
                "career_alignment": 0.95,
                "peer_recommendations": ["U034", "U067", "U099"]
            },
            "U004": {
                "user_id": "U004",
                "courses": [
                    {"course_id": "C008", "title": "UI/UX Design Principles", "skills_covered": ["UI Design", "UX Design", "Design Thinking"], "duration_hours": 25, "difficulty_level": 3.6},
                    {"course_id": "C021", "title": "User Interface Prototyping", "skills_covered": ["Prototyping", "Figma", "UI Design"], "duration_hours": 20, "difficulty_level": 3.5},
                    {"course_id": "C033", "title": "Interaction Design", "skills_covered": ["Interaction Design", "User Flows", "Wireframing"], "duration_hours": 22, "difficulty_level": 3.7},
                    {"course_id": "C041", "title": "Design Systems", "skills_covered": ["Design Systems", "Component Libraries", "Style Guides"], "duration_hours": 18, "difficulty_level": 4.0},
                    {"course_id": "C047", "title": "UX Research Methods", "skills_covered": ["UX Research", "Usability Testing", "Heuristic Evaluation"], "duration_hours": 24, "difficulty_level": 3.8}
                ],
                "expected_skills": ["UI Design", "UX Design", "Design Thinking", "Prototyping", "Figma", "Interaction Design", "User Flows", "Wireframing", "Design Systems", "UX Research"],
                "total_duration": 109,
                "career_alignment": 0.92,
                "peer_recommendations": ["U027", "U058", "U091"]
            },
            "U005": {
                "user_id": "U005",
                "courses": [
                    {"course_id": "C010", "title": "DevOps Pipeline Automation", "skills_covered": ["DevOps", "CI/CD", "Jenkins"], "duration_hours": 30, "difficulty_level": 4.3},
                    {"course_id": "C018", "title": "Container Orchestration with Kubernetes", "skills_covered": ["Kubernetes", "Containers", "Docker"], "duration_hours": 35, "difficulty_level": 4.5},
                    {"course_id": "C026", "title": "Infrastructure as Code", "skills_covered": ["IaC", "Terraform", "CloudFormation"], "duration_hours": 28, "difficulty_level": 4.2},
                    {"course_id": "C039", "title": "Cloud Security", "skills_covered": ["Security", "Cloud", "Compliance"], "duration_hours": 25, "difficulty_level": 4.4},
                    {"course_id": "C043", "title": "Monitoring and Observability", "skills_covered": ["Monitoring", "Observability", "Prometheus"], "duration_hours": 22, "difficulty_level": 4.0}
                ],
                "expected_skills": ["DevOps", "CI/CD", "Jenkins", "Kubernetes", "Containers", "Docker", "IaC", "Terraform", "CloudFormation", "Security", "Cloud", "Compliance", "Monitoring", "Observability", "Prometheus"],
                "total_duration": 140,
                "career_alignment": 0.88,
                "peer_recommendations": ["U018", "U052", "U087"]
            }
        }
        return paths.get(user_id, None)
    
    @st.cache_data
    def get_mock_cluster_data(user_id):
        # Mock cluster data
        clusters = {
            "U001": {"cluster": 0, "cluster_size": 45, "description": "Data Science & ML Focused"},
            "U002": {"cluster": 1, "cluster_size": 38, "description": "Software Development"},
            "U003": {"cluster": 2, "cluster_size": 32, "description": "Product & Management"},
            "U004": {"cluster": 3, "cluster_size": 28, "description": "Design & UX Focused"},
            "U005": {"cluster": 4, "cluster_size": 35, "description": "DevOps & Infrastructure"}
        }
        return clusters.get(user_id, None)
    
    @st.cache_data
    def get_mock_skill_data(user_id):
        # Mock skill data
        skills = {
            "U001": [
                {"skill": "Python", "proficiency": 0.85},
                {"skill": "Data Analysis", "proficiency": 0.78},
                {"skill": "Statistics", "proficiency": 0.72},
                {"skill": "Machine Learning", "proficiency": 0.65},
                {"skill": "SQL", "proficiency": 0.80},
                {"skill": "Data Visualization", "proficiency": 0.75}
            ],
            "U002": [
                {"skill": "JavaScript", "proficiency": 0.88},
                {"skill": "HTML/CSS", "proficiency": 0.92},
                {"skill": "React", "proficiency": 0.75},
                {"skill": "Node.js", "proficiency": 0.70},
                {"skill": "Git", "proficiency": 0.85},
                {"skill": "API Design", "proficiency": 0.72}
            ],
            "U003": [
                {"skill": "Product Management", "proficiency": 0.82},
                {"skill": "Agile", "proficiency": 0.78},
                {"skill": "Requirements Gathering", "proficiency": 0.85},
                {"skill": "Roadmapping", "proficiency": 0.76},
                {"skill": "Stakeholder Management", "proficiency": 0.80},
                {"skill": "Analytics", "proficiency": 0.65}
            ],
            "U004": [
                {"skill": "UI Design", "proficiency": 0.90},
                {"skill": "UX Design", "proficiency": 0.88},
                {"skill": "Wireframing", "proficiency": 0.85},
                {"skill": "User Research", "proficiency": 0.75},
                {"skill": "Figma", "proficiency": 0.92},
                {"skill": "Design Systems", "proficiency": 0.78}
            ],
            "U005": [
                {"skill": "DevOps", "proficiency": 0.87},
                {"skill": "Docker", "proficiency": 0.85},
                {"skill": "Kubernetes", "proficiency": 0.78},
                {"skill": "CI/CD", "proficiency": 0.83},
                {"skill": "Cloud Platforms", "proficiency": 0.80},
                {"skill": "Linux", "proficiency": 0.92}
            ]
        }
        return skills.get(user_id, None)
    
    # Sidebar for user selection
    st.sidebar.title("🧠 SkillSphere")
    st.sidebar.subheader("AI-Powered Learning Paths")
    
    # User selection
    users = get_mock_user_data()
    user_options = [f"{uid} - {data['name']}" for uid, data in users.items()]
    selected_user_option = st.sidebar.selectbox("Select User", user_options)
    selected_user_id = selected_user_option.split(" - ")[0]
    
    # Get user data
    user_data = users[selected_user_id]
    learning_path = get_mock_learning_path(selected_user_id)
    cluster_data = get_mock_cluster_data(selected_user_id)
    skill_data = get_mock_skill_data(selected_user_id)
    
    # Sidebar navigation
    st.sidebar.divider()
    page = st.sidebar.radio("Navigation", ["Dashboard", "Learning Path", "Skill Analysis", "Peer Network"])
    
    # Dashboard
    if page == "Dashboard":
        st.title(f"👤 {user_data['name']} - {user_data['title']}")
        
        # Create three columns for key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Cluster", f"Group {cluster_data['cluster']}", f"{cluster_data['cluster_size']} peers")
            st.caption(f"Cluster Description: {cluster_data['description']}")
        
        with col2:
            st.metric("Career Alignment", f"{int(learning_path['career_alignment'] * 100)}%", "Based on goals")
        
        with col3:
            st.metric("Expected Skills", f"{len(learning_path['expected_skills'])}", "From learning path")
        
        # Dashboard main content
        st.divider()
        
        # Split into two columns
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📚 Recommended Learning Path")
            
            # Create a dataframe for the courses
            courses_df = pd.DataFrame(learning_path['courses'])
            
            # Display the first three courses with expanders for details
            for i, course in enumerate(courses_df.iloc[:3].iterrows()):
                course = course[1]
                with st.expander(f"{i+1}. {course['title']} (Difficulty: {course['difficulty_level']}/5)"):
                    st.write(f"**Duration:** {course['duration_hours']} hours")
                    st.write(f"**Skills Covered:** {', '.join(course['skills_covered'])}")
                    st.progress(0.3 if i == 0 else 0.0)  # Only first course shows progress
            
            st.caption(f"View all {len(courses_df)} courses in the Learning Path tab")
        
        with col2:
            st.subheader("🔍 Skill Breakdown")
            
            # Create a dataframe for skills and plot
            skills_df = pd.DataFrame(skill_data)
            
            # Convert skills to a format suitable for plotting
            skill_names = [item['skill'] for item in skill_data]
            skill_values = [item['proficiency'] for item in skill_data]
            
            # Create the plot
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.barh(skill_names, skill_values, color='skyblue')
            ax.set_xlim(0, 1)
            ax.set_xlabel('Proficiency')
            ax.set_title('Current Skills')
            st.pyplot(fig)
    
    # Learning Path Page
    elif page == "Learning Path":
        st.title(f"📚 Learning Path for {user_data['name']}")
        
        # Top metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Duration", f"{learning_path['total_duration']} hours")
        with col2:
            st.metric("Expected Skills", f"{len(learning_path['expected_skills'])}")
        with col3:
            st.metric("Career Alignment", f"{int(learning_path['career_alignment'] * 100)}%")
        
        # Create a timeline visualization of the learning path
        st.subheader("📈 Learning Journey Progression")
        
        # Create a cumulative skills timeline
        cumulative_hours = 0
        cumulative_skills = []
        timeline_data = []
        
        for i, course in enumerate(learning_path['courses']):
            cumulative_hours += course['duration_hours']
            for skill in course['skills_covered']:
                if skill not in cumulative_skills:
                    cumulative_skills.append(skill)
            
            timeline_data.append({
                'course_index': i + 1,
                'course_title': course['title'],
                'cumulative_hours': cumulative_hours,
                'cumulative_skills': len(cumulative_skills)
            })
        
        df_timeline = pd.DataFrame(timeline_data)
        
        # Plot the timeline
        fig, ax1 = plt.subplots(figsize=(10, 5))
        
        # Plot hours (left axis)
        color = 'tab:blue'
        ax1.set_xlabel('Course Progression')
        ax1.set_ylabel('Cumulative Hours', color=color)
        ax1.plot(df_timeline['course_index'], df_timeline['cumulative_hours'], 'o-', color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        
        # Create a second y-axis for skills
        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('Cumulative Skills', color=color)
        ax2.plot(df_timeline['course_index'], df_timeline['cumulative_skills'], 'o-', color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        
        fig.tight_layout()
        st.pyplot(fig)
        
        # Detailed course information
        st.subheader("🧩 Recommended Courses")
        
        # Create tabs for each course
        tabs = st.tabs([f"Course {i+1}: {course['title']}" for i, course in enumerate(learning_path['courses'])])
        
        # Add content to each tab
        for i, (tab, course) in enumerate(zip(tabs, learning_path['courses'])):
            with tab:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.subheader(course['title'])
                    st.write(f"**Course ID:** {course['course_id']}")
                    st.write(f"**Skills Covered:** {', '.join(course['skills_covered'])}")
                    st.write(f"**Duration:** {course['duration_hours']} hours")
                    st.write(f"**Difficulty Level:** {course['difficulty_level']}/5.0")
                
                with col2:
                    # Create a simple donut chart showing difficulty
                    fig, ax = plt.subplots(figsize=(3, 3))
                    size = 0.3
                    vals = [course['difficulty_level'], 5 - course['difficulty_level']]
                    
                    cmap = plt.get_cmap("Blues")
                    outer_colors = [cmap(0.7), cmap(0.2)]
                    
                    ax.pie(vals, radius=1, colors=outer_colors, wedgeprops=dict(width=size, edgecolor='w'))
                    ax.set_title(f'Difficulty: {course["difficulty_level"]}/5')
                    st.pyplot(fig)
                
                # Show progress bar if it's the first course (assuming in progress)
                if i == 0:
                    st.write("**Progress:**")
                    st.progress(0.3)
                
                # Skill relevance
                st.write("**Skill Relevance to Career Goals:**")
                # Generate random relevance scores for demo
                np.random.seed(i)  # For reproducibility
                relevance_scores = np.random.uniform(0.5, 1.0, len(course['skills_covered']))
                
                skill_rel_df = pd.DataFrame({
                    'Skill': course['skills_covered'],
                    'Relevance': relevance_scores
                })
                
                fig, ax = plt.subplots(figsize=(10, 3))
                ax.barh(skill_rel_df['Skill'], skill_rel_df['Relevance'], color='skyblue')
                ax.set_xlim(0, 1)
                ax.set_xlabel('Relevance to Career Goals')
                st.pyplot(fig)
    
    # Skill Analysis Page
    elif page == "Skill Analysis":
        st.title(f"🎯 Skill Analysis for {user_data['name']}")
        
        # Create two columns for current and projected skills
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Current Skills")
            
            # Create a dataframe for skills
            current_skills_df = pd.DataFrame(skill_data)
            
            # Convert to a suitable format for radar chart
            categories = [s['skill'] for s in skill_data]
            values = [s['proficiency'] for s in skill_data]
            
            # Create a radar chart
            labels = categories
            stats = values
            
            angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
            stats = np.concatenate((stats, [stats[0]]))
            angles = np.concatenate((angles, [angles[0]]))
            labels = np.concatenate((labels, [labels[0]]))
            
            fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
            ax.plot(angles, stats, 'o-', linewidth=2, color='blue')
            ax.fill(angles, stats, alpha=0.25, color='blue')
            ax.set_thetagrids(np.degrees(angles[:-1]), labels[:-1])
            ax.set_ylim(0, 1)
            ax.grid(True)
            ax.set_title('Current Skill Profile', y=1.1)
            st.pyplot(fig)
            
            # Show the skills as a table
            st.dataframe(
                pd.DataFrame([{'Skill': s['skill'], 'Proficiency': f"{int(s['proficiency']*100)}%"} for s in skill_data])
            )
        
        with col2:
            st.subheader("Projected Skills After Learning Path")
            
            # Create projected skills (current + new skills from learning path)
            current_skill_names = [s['skill'] for s in skill_data]
            new_skill_names = [s for s in learning_path['expected_skills'] if s not in current_skill_names]
            
            projected_skills = skill_data.copy()
            # Add new skills
            for skill in new_skill_names:
                projected_skills.append({"skill": skill, "proficiency": 0.6})  # Assume 60% proficiency for new skills
            
            # Boost existing skills that are covered in courses
            for i, skill in enumerate(projected_skills):
                if skill['skill'] in current_skill_names:
                    # Check if this skill is covered in any course
                    for course in learning_path['courses']:
                        if skill['skill'] in course['skills_covered']:
                            # Boost proficiency but don't exceed 1.0
                            projected_skills[i]['proficiency'] = min(1.0, skill['proficiency'] + 0.15)
            
            # Convert to a suitable format for radar chart
            proj_categories = [s['skill'] for s in projected_skills]
            proj_values = [s['proficiency'] for s in projected_skills]
            
            # Create a radar chart
            labels = proj_categories
            stats = proj_values
            
            angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
            stats = np.concatenate((stats, [stats[0]]))
            angles = np.concatenate((angles, [angles[0]]))
            labels = np.concatenate((labels, [labels[0]]))
            
            fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
            ax.plot(angles, stats, 'o-', linewidth=2, color='green')
            ax.fill(angles, stats, alpha=0.25, color='green')
            ax.set_thetagrids(np.degrees(angles[:-1]), labels[:-1])
            ax.set_ylim(0, 1)
            ax.grid(True)
            ax.set_title('Projected Skill Profile', y=1.1)
            st.pyplot(fig)
            
            # Show skills as a table, highlighting new skills
            st.dataframe(
                pd.DataFrame([
                    {
                        'Skill': s['skill'], 
                        'Proficiency': f"{int(s['proficiency']*100)}%",
                        'Status': 'New' if s['skill'] in new_skill_names else 'Improved' if s['skill'] in current_skill_names and any(s['skill'] in c['skills_covered'] for c in learning_path['courses']) else 'Existing'
                    } for s in projected_skills
                ]).style.apply(lambda x: ['background: lightgreen' if x['Status'] == 'New' else 'background: lightyellow' if x['Status'] == 'Improved' else '' for i in range(len(x))], axis=1)
            )
        
        # Skill Gap Analysis
        st.divider()
        st.subheader("🧩 Skill Gap Analysis")
        
        # Career recommendations based on skill profile
        career_options = {
            "U001": ["Data Scientist", "Machine Learning Engineer", "Data Analyst"],
            "U002": ["Senior Software Engineer", "Full Stack Developer", "DevOps Engineer"],
            "U003": ["Senior Product Manager", "Product Director", "Program Manager"],
            "U004": ["UX/UI Lead", "Design Manager", "Creative Director"],
            "U005": ["DevOps Lead", "Cloud Architect", "Site Reliability Engineer"]
        }
        
        career_req_skills = {
            "Data Scientist": ["Python", "Machine Learning", "Statistics", "SQL", "Big Data", "Deep Learning"],
            "Machine Learning Engineer": ["Python", "Machine Learning", "Software Engineering", "DevOps", "Deep Learning"],
            "Data Analyst": ["SQL", "Python", "Data Visualization", "Statistics", "Excel"],
            "Senior Software Engineer": ["JavaScript", "System Design", "APIs", "Cloud Computing", "Algorithms"],
            "Full Stack Developer": ["JavaScript", "HTML/CSS", "React", "Node.js", "Databases", "APIs"],
            "DevOps Engineer": ["CI/CD", "Docker", "Kubernetes", "Cloud Platforms", "Infrastructure as Code"],
            "Senior Product Manager": ["Product Strategy", "User Research", "Analytics", "Roadmapping", "Stakeholder Management"],
            "Product Director": ["Product Strategy", "Leadership", "Business Acumen", "Cross-functional Collaboration", "Market Analysis"],
            "Program Manager": ["Project Management", "Risk Management", "Stakeholder Management", "Budgeting", "Planning"],
            "UX/UI Lead": ["UI Design", "UX Design", "User Research", "Design Systems", "Leadership"],
            "Design Manager": ["Design Leadership", "Design Thinking", "Team Management", "Design Operations", "Client Management"],
            "Creative Director": ["Design Vision", "Brand Strategy", "Team Leadership", "Client Communication", "Portfolio Management"],
            "DevOps Lead": ["DevOps", "Team Leadership", "CI/CD", "Cloud Platforms", "Security"],
            "Cloud Architect": ["Cloud Platforms", "Architecture Design", "Security", "Network Design", "Cost Optimization"],
            "Site Reliability Engineer": ["Linux", "Cloud Platforms", "Monitoring", "Automation", "Performance Optimization"]
        }
        
        # Get recommended careers for current user
        recommended_careers = career_options.get(selected_user_id, ["Career 1", "Career 2", "Career 3"])
        
        # Create tabs for each career option
        career_tabs = st.tabs(recommended_careers)
        
        # Add content to each tab
        for tab, career in zip(career_tabs, recommended_careers):
            with tab:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader(f"Skills for {career}")
                    
                    # Get required skills for this career
                    required_skills = career_req_skills.get(career, ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"])
                    
                    # Check which skills the user has
                    current_skill_names = [s['skill'] for s in skill_data]
                    
                    # For each required skill, check if user has it and their proficiency
                    skill_gap = []
                    for req_skill in required_skills:
                        if req_skill in current_skill_names:
                            # Find proficiency
                            prof = next((s['proficiency'] for s in skill_data if s['skill'] == req_skill), 0)
                            skill_gap.append({
                                "skill": req_skill,
                                "required": True,
                                "current": prof,
                                "gap": max(0, 0.7 - prof)  # Assume 70% is minimum required
                            })
                        else:
                            skill_gap.append({
                                "skill": req_skill,
                                "required": True,
                                "current": 0,
                                "gap": 0.7  # Full gap
                            })
                    
                    # Create a dataframe for skill gap
                    skill_gap_df = pd.DataFrame(skill_gap)
                    
                    # Create a horizontal bar chart showing skill gaps
                    fig, ax = plt.subplots(figsize=(8, 6))
                    ax.barh(skill_gap_df['skill'], skill_gap_df['current'], color='skyblue', label='Current')
                    ax.barh(skill_gap_df['skill'], skill_gap_df['gap'], left=skill_gap_df['current'], color='lightcoral', label='Gap')
                    ax.set_xlim(0, 1)
                    ax.set_xlabel('Proficiency')
                    ax.legend()
                    ax.set_title(f'Skill Gap Analysis for {career}')
                    st.pyplot(fig)
                
                with col2:
                    st.subheader("Learning Recommendations")
                    
                    # Get missing or low-proficiency skills
                    missing_skills = [s['skill'] for s in skill_gap if s['gap'] > 0.2]
                    
                    if missing_skills:
                        st.write(f"To become a {career}, focus on these skills:")
                        
                        for skill in missing_skills:
                            st.write(f"**{skill}**")
                            
                            # Find courses in learning path that teach this skill
                            relevant_courses = [
                                c for c in learning_path['courses'] if skill in c['skills_covered']
                            ]
                            
                            if relevant_courses:
                                st.write("Recommended courses:")
                                for course in relevant_courses[:2]:  # Show at most 2 courses
                                    st.info(f"📚 {course['title']} ({course['duration_hours']} hours)")
                            else:
                                st.write("No specific courses in your current learning path cover this skill.")
                                st.warning("Consider additional courses outside your current learning path.")
                    else:
                        st.success("You have all the required skills for this role! Consider advanced courses to further enhance your expertise.")
                    
                    # Career trend
                    st.subheader("Career Trend")
                    # Simple line chart showing career demand trend
                    trend_data = np.random.normal(loc=0.05, scale=0.02, size=12).cumsum() + 1
                    fig, ax = plt.subplots(figsize=(8, 3))
                    ax.plot(range(1, 13), trend_data, marker='o')
                    ax.set_xlabel('Months')
                    ax.set_ylabel('Demand Index')
                    ax.set_title(f'{career} Demand Trend')
                    ax.grid(True, linestyle='--', alpha=0.7)
                    st.pyplot(fig)
    
    # Peer Network Page
    elif page == "Peer Network":
        st.title(f"👥 Peer Network for {user_data['name']}")
        
        # Get recommended peers
        peer_ids = learning_path['peer_recommendations']
        
        # Create mock peer data
        @st.cache_data
        def get_mock_peer_data(peer_ids):
            peers = {
                "U012": {"name": "John Smith", "title": "Data Scientist", "company": "Tech Analytics Inc.", "skills": ["Python", "Machine Learning", "Deep Learning"]},
                "U023": {"name": "Jennifer Lee", "title": "Senior Developer", "company": "WebSolutions Co.", "skills": ["JavaScript", "React", "Node.js"]},
                "U034": {"name": "Michael Chen", "title": "Product Manager", "company": "InnovateTech", "skills": ["Product Strategy", "Agile", "User Research"]},
                "U045": {"name": "Sarah Johnson", "title": "Data Engineer", "company": "DataFlow Systems", "skills": ["Python", "SQL", "Big Data"]},
                "U056": {"name": "David Wilson", "title": "Full Stack Developer", "company": "CodeMasters", "skills": ["JavaScript", "Python", "React"]},
                "U067": {"name": "Emily Davis", "title": "Senior Product Manager", "company": "ProductFirst", "skills": ["Product Management", "Analytics", "Strategic Planning"]},
                "U078": {"name": "Ryan Thompson", "title": "Machine Learning Engineer", "company": "AI Solutions", "skills": ["Python", "Deep Learning", "TensorFlow"]},
                "U089": {"name": "Jessica Brown", "title": "DevOps Engineer", "company": "CloudOps", "skills": ["Docker", "Kubernetes", "AWS"]},
                "U018": {"name": "Kevin Zhang", "title": "Cloud Engineer", "company": "CloudTech", "skills": ["AWS", "Docker", "Terraform"]},
                "U027": {"name": "Lisa Wang", "title": "UX Designer", "company": "DesignThink", "skills": ["UI Design", "User Research", "Figma"]},
                "U052": {"name": "Mark Johnson", "title": "Site Reliability Engineer", "company": "ReliableSystems", "skills": ["DevOps", "Monitoring", "Kubernetes"]},
                "U058": {"name": "Anna Garcia", "title": "UI/UX Designer", "company": "CreativeDesign", "skills": ["UI Design", "UX Design", "Design Systems"]},
                "U087": {"name": "Tom Wilson", "title": "DevOps Engineer", "company": "InfraOps", "skills": ["CI/CD", "Kubernetes", "Terraform"]},
                "U091": {"name": "Sophie Miller", "title": "Senior Designer", "company": "VisualSolutions", "skills": ["UX Design", "Design Systems", "Prototyping"]},
                "U099": {"name": "Chris Taylor", "title": "Product Strategy Lead", "company": "StrategyWorks", "skills": ["Product Strategy", "Market Analysis", "Roadmapping"]}
            }
            return {pid: peers[pid] for pid in peer_ids if pid in peers}
        
        peer_data = get_mock_peer_data(peer_ids)
        
        # Create a network visualization
        st.subheader("🔍 Your Learning Network")
        
        # Create a network graph
        G = nx.Graph()
        
        # Add center node (current user)
        G.add_node(selected_user_id, name=user_data['name'], title=user_data['title'])
        
        # Add peer nodes and connections
        for pid, data in peer_data.items():
            G.add_node(pid, name=data['name'], title=data['title'])
            G.add_edge(selected_user_id, pid)
        
        # Add some connections between peers for a more interesting network
        # This would ideally come from real data about peer relationships
        if len(peer_ids) >= 3:
            G.add_edge(peer_ids[0], peer_ids[1])
            G.add_edge(peer_ids[1], peer_ids[2])
            if len(peer_ids) > 3:
                G.add_edge(peer_ids[0], peer_ids[2])
        
        # Set positions using spring layout
        pos = nx.spring_layout(G, k=0.5, iterations=50)
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Draw the graph
        nx.draw_networkx_nodes(G, pos, 
                              nodelist=[selected_user_id],
                              node_color='red',
                              node_size=500,
                              alpha=0.8)
        
        nx.draw_networkx_nodes(G, pos, 
                              nodelist=list(peer_data.keys()),
                              node_color='skyblue',
                              node_size=300,
                              alpha=0.8)
        
        nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
        
        # Add labels
        labels = {n: G.nodes[n]['name'] for n in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=10)
        
        plt.axis('off')
        st.pyplot(fig)
        
        # Display peer profiles
        st.subheader("👤 Recommended Learning Peers")
        
        # Create two columns
        col1, col2 = st.columns(2)
        
        # Display peers in alternating columns
        for i, (pid, data) in enumerate(peer_data.items()):
            with col1 if i % 2 == 0 else col2:
                st.write(f"**{data['name']}**")
                st.write(f"*{data['title']} at {data['company']}*")
                st.write(f"Skills: {', '.join(data['skills'])}")
                
                # Calculate skill overlap
                user_skills = [s['skill'] for s in skill_data]
                overlap = [s for s in data['skills'] if s in user_skills]
                
                if overlap:
                    st.write(f"Common skills: {', '.join(overlap)}")
                
                # Add connect button (for demonstration)
                st.button(f"Connect with {data['name']}", key=f"connect_{pid}")
                st.divider()
        
        # Add a feature to find more peers
        st.subheader("🔎 Find More Learning Peers")
        
        # Skills filter
        all_user_skills = [s['skill'] for s in skill_data]
        selected_skills = st.multiselect("Filter by skills", all_user_skills)
        
        # Search button
        if st.button("Search"):
            st.info("This feature would search the platform for additional peers based on selected filters.")
            st.write("In a production environment, this would connect to a backend search API.")
    
    # Add footer
    st.divider()
    st.caption("SkillSphere - AI-Powered Learning Paths | Prototype Demo")
    
    # Add a floating feedback button
    with st.expander("📝 Provide Feedback"):
        st.write("We'd love to hear your thoughts on the SkillSphere platform!")
        feedback_type = st.selectbox("Feedback Type", ["General Feedback", "Bug Report", "Feature Request"])
        feedback_text = st.text_area("Your Feedback")
        if st.button("Submit Feedback"):
            st.success("Thank you for your feedback! We'll use it to improve SkillSphere.")