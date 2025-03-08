import sqlite3
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

# --- User Model ---
class User:
    def __init__(self, id=None, username=None, email=None, password_hash=None, 
                 skills=None, education_level=None, about=None, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.skills = skills  # Stored as a comma-separated string
        self.education_level = education_level
        self.about = about
        self.created_at = created_at

    def set_password(self, password):
        """Hash the password and store it"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check the password against the stored hash"""
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def create_table(conn):
        """Create the users table if it doesn't exist"""
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            skills TEXT DEFAULT '',
            education_level TEXT DEFAULT '',
            about TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()

    def save(self, conn):
        """Save user to database"""
        cursor = conn.cursor()
        if self.id is None:
            cursor.execute(
                """INSERT INTO users (username, email, password_hash, skills, education_level, about) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                (self.username, self.email, self.password_hash, 
                 self.skills or '', self.education_level or '', self.about or '')
            )
            self.id = cursor.lastrowid
        else:
            cursor.execute(
                """UPDATE users 
                SET username = ?, email = ?, password_hash = ?, skills = ?, education_level = ?, about = ? 
                WHERE id = ?""",
                (self.username, self.email, self.password_hash,
                 self.skills or '', self.education_level or '', self.about or '', self.id)
            )
        conn.commit()
        return self

    @classmethod
    def get_by_email(cls, conn, email):
        """Find user by email"""
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email, password_hash, skills, education_level, about, created_at FROM users WHERE email = ?", 
            (email,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return cls(id=row[0], username=row[1], email=row[2], password_hash=row[3], 
                   skills=row[4], education_level=row[5], about=row[6], created_at=row[7])

    @classmethod
    def get_all_users(cls, conn):
        """Retrieve all users"""
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, password_hash, skills, education_level, about, created_at FROM users")
        rows = cursor.fetchall()
        return [cls(id=row[0], username=row[1], email=row[2], password_hash=row[3], 
                    skills=row[4], education_level=row[5], about=row[6], created_at=row[7]) for row in rows]

    @classmethod
    def email_exists(cls, conn, email):
        """Check if an email already exists in the database"""
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
        return cursor.fetchone() is not None

    @classmethod
    def username_exists(cls, conn, username):
        """Check if a username already exists in the database"""
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        return cursor.fetchone() is not None

    @classmethod
    def import_from_csv(cls, conn, csv_path):
        """Import users from a CSV file"""
        df = pd.read_csv(csv_path)
        cursor = conn.cursor()
        for _, row in df.iterrows():
            cursor.execute(
                """INSERT INTO users (username, email, password_hash, skills, education_level, about) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                (row["username"], row["email"], generate_password_hash(row["password"]), 
                 row.get("skills", ''), row.get("education_level", ''), row.get("about", ''))
            )
        conn.commit()

# --- Course Model ---
class Course:
    def __init__(self, id=None, name=None, description=None, instructor=None, difficulty="Unknown"):
        self.id = id
        self.name = name
        self.description = description
        self.instructor = instructor
        self.difficulty = difficulty

    @staticmethod
    def create_table(conn):
        """Create the courses table if it doesn't exist"""
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            instructor TEXT NOT NULL,
            difficulty TEXT DEFAULT 'Unknown'
        )
        ''')
        conn.commit()

    def save(self, conn):
        """Save course to database"""
        cursor = conn.cursor()
        if self.id is None:
            cursor.execute(
                "INSERT INTO courses (name, description, instructor, difficulty) VALUES (?, ?, ?, ?)",
                (self.name, self.description, self.instructor, self.difficulty)
            )
            self.id = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE courses SET name = ?, description = ?, instructor = ?, difficulty = ? WHERE id = ?",
                (self.name, self.description, self.instructor, self.difficulty, self.id)
            )
        conn.commit()
        return self

    @classmethod
    def get_all_courses(cls, conn):
        """Retrieve all courses"""
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM courses")
        rows = cursor.fetchall()
        return [cls(*row) for row in rows]

    @classmethod
    def import_from_csv(cls, conn, csv_path):
        """Import courses from a CSV file"""
        df = pd.read_csv(csv_path)
        cursor = conn.cursor()
        for _, row in df.iterrows():
            cursor.execute(
                "INSERT INTO courses (name, description, instructor, difficulty) VALUES (?, ?, ?, ?)",
                (row["name"], row["description"], row["instructor"], row.get("difficulty", "Unknown"))
            )
        conn.commit()

# --- Database Initialization ---
def init_db():
    conn = sqlite3.connect("database.db")
    User.create_table(conn)
    Course.create_table(conn)
    conn.close()

# Initialize database on script run
if __name__ == "__main__":
    init_db()
