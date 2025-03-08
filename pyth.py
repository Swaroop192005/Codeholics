import sqlite3

def check_users_table():
    conn = sqlite3.connect("database/database.db")
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    
    print("✅ Existing columns in users table:")
    for col in columns:
        print(col)
    
    conn.close()

check_users_table()
