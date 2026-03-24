# database.py
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from config import DB_CONFIG

def get_db_connection():
    # Connect to PostgreSQL database
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"DB connection error: {e}")
        return None

def get_student_info(student_id):
    # Fetch student data by ID
    conn = get_db_connection()
    if not conn: return None
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM students WHERE student_id = %s", (str(student_id),))
        student_info = cursor.fetchone()
        cursor.close()
        return student_info
    except Exception as e:
        print(f"Data fetch error: {e}")
        return None
    finally:
        conn.close()

def mark_attendance(student_id, current_attendance):
    # Increment attendance count and update time
    conn = get_db_connection()
    if not conn: return False
    
    try:
        cursor = conn.cursor()
        new_attendance = current_attendance + 1
        current_time = datetime.now()
        
        cursor.execute("""
            UPDATE students 
            SET total_attendance = %s, last_attendance_time = %s 
            WHERE student_id = %s
        """, (new_attendance, current_time, str(student_id)))
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Attendance update error: {e}")
        return False
    finally:
        conn.close()

def add_new_student_to_db(student_id, name):
    # Register a new student with default values
    conn = get_db_connection()
    if not conn: return False
    
    try:
        cursor = conn.cursor()
        
        query = """
            INSERT INTO students (student_id, name, major, starting_year, total_attendance, standing, year, last_attendance_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            student_id, 
            name, 
            "Unknown",             # major
            datetime.now().year,   # starting_year
            0,                     # total_attendance
            "G",                   # standing
            1,                     # year
            datetime(2000, 1, 1)   # last_attendance_time
        ))
        conn.commit()
        cursor.close()
        print(f"Student {name} added to DB.")
        return True
    except Exception as e:
        print(f"DB insert error: {e}")
        return False
    finally:
        conn.close()