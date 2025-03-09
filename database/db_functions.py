import sqlite3
import pandas as pd
import os
import csv
from database.models import User, Course  # Import Course model


def init_connection():
    """Initialize database connection and create tables if they don't exist"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Create a database directory if it doesn't exist
    db_dir = os.path.join(base_dir, "database")
    os.makedirs(db_dir, exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(os.path.join(db_dir, "database.db"))
    
    # Create tables if they don't exist
    User.create_table(conn)
    Course.create_table(conn)
    
    return conn


# --- User Management ---
def import_users_from_csv():
    """Import users from users.csv into the database"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "data", "users.csv")

    if not os.path.exists(csv_path):
        print("Users CSV file not found.")
        return

    conn = init_connection()
    try:
        User.import_from_csv(conn, csv_path)
        print("Users imported successfully.")
    except Exception as e:
        print(f"Error importing users: {e}")
    finally:
        conn.close()

def get_all_users():
    """Fetch all users from the database"""
    conn = init_connection()
    users = User.get_all_users(conn)
    conn.close()
    return users

def get_user_by_email(email):
    """Fetch a single user by email"""
    conn = init_connection()
    user = User.get_by_email(conn, email)
    conn.close()
    return user

def get_skills_by_user_id(conn, user_id):
    """Fetch skills for a given user ID"""
    if not user_id:
        return []
        
    cursor = conn.cursor()
    cursor.execute("SELECT skills FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    
    if result and result[0]:
        # Split by comma and strip whitespace
        skills = [skill.strip() for skill in result[0].split(",") if skill.strip()]
        return skills
    return []

def get_user_by_id(conn, user_id):
    """Fetch a single user by ID"""
    if not user_id:
        return None
        
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email, password_hash, skills, education_level, about, created_at FROM users WHERE id = ?", 
            (user_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return User(id=row[0], username=row[1], email=row[2], password_hash=row[3], 
                   skills=row[4], education_level=row[5], about=row[6], created_at=row[7])
    except Exception as e:
        print(f"Error fetching user by ID: {e}")
        return None

# --- Course Management ---
def import_courses_from_csv():
    """Import courses from courses.csv into the database"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "data", "courses.csv")

    if not os.path.exists(csv_path):
        print("Courses CSV file not found.")
        return

    conn = init_connection()
    try:
        Course.import_from_csv(conn, csv_path)
        print("Courses imported successfully.")
    except Exception as e:
        print(f"Error importing courses: {e}")
    finally:
        conn.close()

def get_all_courses():
    """Fetch all courses from the database"""
    conn = init_connection()
    courses = Course.get_all_courses(conn)
    conn.close()
    return courses

def get_course_by_id(course_id):
    """Fetch a single course by ID"""
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return Course(id=row[0], name=row[1], description=row[2], 
                     instructor=row[3], difficulty=row[4], num_subscribers=row[5])
    return None

def update_user_skills(conn, user_id, skills):
    """Update a user's skills"""
    if not user_id:
        return False
        
    try:
        cursor = conn.cursor()
        skills_str = ", ".join(skills) if isinstance(skills, list) else skills
        cursor.execute("UPDATE users SET skills = ? WHERE id = ?", (skills_str, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating user skills: {e}")
        return False

