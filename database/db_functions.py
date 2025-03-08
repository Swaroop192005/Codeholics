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
    db_path = os.path.join(db_dir, "database.db")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    
    # Create tables
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
    courses = Course.get_all(conn)
    conn.close()
    return courses

def get_course_by_id(course_id):
    """Fetch a single course by ID"""
    conn = init_connection()
    course = Course.get_by_id(conn, course_id)
    conn.close()
    return course
