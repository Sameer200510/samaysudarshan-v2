import mysql.connector
from mysql.connector import Error
# Tumhari existing DB connection function
from db_connector import get_db_connection 
from typing import Dict, List, Any

# NOTE: Is function ko tum app.py mein import karoge
def fetch_all_ga_constraints_from_db() -> Dict[str, Any]:
    """ 
    Fetches all necessary data from MySQL to serve as constraints for the Genetic Algorithm.
    (DBMS Read Operation)
    """
    conn = None
    constraints = {}
    
    try:
        conn = get_db_connection()
        if conn is None:
            # OS/DBMS: If connection fails, log error and return empty constraints
            print("Error: Database connection failed in data service.")
            return {}
            
        # Cursor dictionary=True returns results as dicts for easy structuring
        cursor = conn.cursor(dictionary=True) 
        
        # --- A. Fetch Subjects Data (GA Input) ---
        # lecture_count: Number of slots required for the subject (e.g., 4 classes/week)
        cursor.execute("SELECT subject_id, subject_code, department_id, lecture_count FROM timetable_subject;")
        constraints['subjects'] = cursor.fetchall()

        # --- B. Fetch Faculty Data (Max Load Constraint) ---
        # max_load: Total slots a faculty member can teach (GA Hard Constraint)
        cursor.execute("SELECT faculty_id, name, department_id, max_load FROM faculty_faculty;")
        constraints['faculty'] = cursor.fetchall() 

        # --- C. Fetch Room Data (Capacity Constraint) ---
        # capacity: Room size (GA Hard Constraint)
        cursor.execute("SELECT room_id, room_name, capacity, room_type FROM rooms_classroom;")
        constraints['rooms'] = cursor.fetchall() 

        # --- D. Fetch Time Slots Data (GA's available timeline) ---
        cursor.execute("SELECT slot_id, day_of_week, TIME_FORMAT(start_time, '%%H:%%i') as start_time, TIME_FORMAT(end_time, '%%H:%%i') as end_time FROM timetable_timeslot;")
        constraints['slots'] = cursor.fetchall()

        # --- E. Fetch Batch Data (Batch size/Lunch Time Constraint) ---
        # student_count: Used with room capacity
        # Lunch Time: GA should not schedule a class during this time
        cursor.execute("SELECT batch_id, student_count, lunch_start_time, lunch_end_time FROM student_batch;")
        constraints['batches'] = cursor.fetchall()
        
        # Structure of constraints dictionary:
        # { 'subjects': [...], 'faculty': [...], 'rooms': [...], ... }
        return constraints

    except Error as e:
        print(f"DBMS Fetch Error for GA: {e}")
        return {}
        
    finally:
        # OS Resource Management: Connection close karna zaroori hai
        if conn:
            conn.close()