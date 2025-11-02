import mysql.connector
from datetime import time, timedelta

# --- DBMS Configuration ---
# You must update this with your actual MySQL credentials
DB_CONFIG = {
    'user': 'SamaySudarshan',
    'password': '1212',  # <--- CHANGE THIS!
    'host': 'localhost',
    'database': 'samay_sudarshan_db',
    'raise_on_warnings': True
}
# --------------------------

# Sample Data matching your project's structure
DATA = {
    "departments": [
        ('CSE', 'Computer Science and Engineering', 'Dr. A. Sharma'),
        ('ECE', 'Electronics and Communication', 'Dr. V. Gupta'),
        ('CYS', 'Cyber Security', 'Dr. R. Verma'),
    ],
    "batches": [
        ('CYSB1', 'B.Tech Vth Sem - Cyber', '2025', 120, 'CYS'), 
        ('CSEB1', 'B.Tech Vth Sem - CSE', '2025', 150, 'CSE'), 
    ],
    "faculty": [
        ('F01', 'Prof. Smith', 'smith@univ.edu', 'Professor', 'CSE'),
        ('F02', 'Dr. Jones', 'jones@univ.edu', 'Asst. Prof', 'CYS'),
    ],
    "rooms": [
        ('CR7', 'Class Room 7', 60, 'CLASS'),
        ('LAB1', 'New Lab 1', 30, 'LAB'),
    ],
    "timeslots": [
        ('T1', 'MONDAY', time(9, 0, 0), time(10, 0, 0)),
        ('T2', 'MONDAY', time(10, 0, 0), time(11, 0, 0)),
        ('TL', 'MONDAY', time(13, 0, 0), time(14, 0, 0)), # LUNCH slot
    ],
    "subjects": [
        ('S101', 'TCS-503', 'Database Management Systems', 4, 3, 1, 'CSE'),
        ('S102', 'TCS-597', 'Computer System Security', 4, 3, 1, 'CYS'),
        ('SLCH', 'LUNCH', 'LUNCH', 0, 0, 0, 'CSE'),
    ],
    "timetable_entries": [
        # Timetable Entry 1: CSE Dept, CSEB1 Batch, TCS-503
        ('E01', 'Lecture', 'F01', 'S101', 'CR7', 'CSEB1', 'T1'), 
        
        # Timetable Entry 2: CYS Dept, CYSB1 Batch, TCS-597 
        ('E02', 'Lecture', 'F02', 'LAB1', 'CYSB1', 'S102', 'T2'), 
        
        # Timetable Entry 3: LUNCH Slot
        ('E03', 'Break', 'F01', 'CR7', 'CSEB1', 'SLCH', 'TL'),
    ]
}

def insert_data_into_db():
    conn = None
    try:
        # Check for password update
        if DB_CONFIG['password'] == 'your_mysql_password':
            print("\n❌ ERROR: Please update 'your_mysql_password' in db_connector.py!")
            return

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Disable foreign key checks temporarily for bulk insert (DBMS Integrity)
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        # --- INSERTION LOGIC (Simplified for clarity) ---
        
        # Department
        for dept_id, name, hod in DATA['departments']:
            cursor.execute(f"INSERT IGNORE INTO faculty_department VALUES ('{dept_id}', '{name}', '{hod}')")

        # StudentBatch
        for batch_id, name, year, strength, dept_id in DATA['batches']:
            # Columns: batch_id, batch_name, program, year, strength, department_id
            cursor.execute(f"INSERT IGNORE INTO timetable_studentbatch (batch_id, batch_name, program, year, strength, department_id) VALUES ('{batch_id}', '{name}', 'B.Tech', '{year}', '{strength}', '{dept_id}')")

        # Faculty
        for fid, name, email, designation, dept_id in DATA['faculty']:
            cursor.execute(f"INSERT IGNORE INTO faculty_faculty (faculty_id, name, email, designation, department_id) VALUES ('{fid}', '{name}', '{email}', '{designation}', '{dept_id}')")

        # Rooms
        for rid, name, capacity, type in DATA['rooms']:
            cursor.execute(f"INSERT IGNORE INTO rooms_classroom VALUES ('{rid}', '{name}', '{capacity}', '{type}')")

        # TimeSlots
        for tid, day, start, end in DATA['timeslots']:
            cursor.execute(f"INSERT IGNORE INTO timetable_timeslot VALUES ('{tid}', '{day}', '{start}', '{end}')")

        # Subjects
        for sid, code, name, credits, lec, lab, dept_id in DATA['subjects']:
            cursor.execute(f"INSERT IGNORE INTO timetable_subject (subject_id, subject_code, subject_name, credits, lecture_hours, lab_hours, department_id) VALUES ('{sid}', '{code}', '{name}', '{credits}', '{lec}', '{lab}', '{dept_id}')")

        # Timetable Entries (CRITICAL FINAL TABLE)
        for eid, type, fid, sid, rid, bid, tid in DATA['timetable_entries']:
            # Columns: entry_id, entry_type, faculty_id, subject_id, classroom_id, batch_id, time_slot_id
            cursor.execute(f"INSERT IGNORE INTO timetable_timetableentry (entry_id, entry_type, faculty_id, subject_id, classroom_id, batch_id, time_slot_id) VALUES ('{eid}', '{type}', '{fid}', '{sid}', '{rid}', '{bid}', '{tid}')")

        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        
        conn.commit()
        print("\n✅ Data inserted successfully! Database is ready.")

    except mysql.connector.Error as err:
        print(f"\n❌ Error inserting data: {err}")
        print("Please check your MySQL credentials and ensure all tables exist.")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    insert_data_into_db()