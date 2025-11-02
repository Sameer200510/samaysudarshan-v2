from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

# --- AUTHENTICATION IMPORTS ---
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt
from typing import Dict, Any
# -----------------------------

# Assuming db_connector.py has the function to get connection
from db_connector import get_db_connection

app = Flask(__name__)
CORS(app) # CORS is essential for React to talk to Flask.

# --- 1. CONFIGURATION AND INITIALIZATION ---
app.config['SECRET_KEY'] = 'samaysudarshan_very_secret_key_123'
app.config['JWT_SECRET_KEY'] = 'samaysudarshan_jwt_secret_key_456' 

# Initialize Bcrypt and JWT
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


# ----------------------------------------------------
# 2. AUTHENTICATION AND HELPER FUNCTIONS 
# ----------------------------------------------------

def check_admin_access():
    """ Helper to check if the current user has the 'Admin' role. """
    try:
        current_user_claims = get_jwt()
        user_role = current_user_claims.get('role')
        if user_role != 'Admin':
            return jsonify({"msg": "Authorization failed. Admin access required."}), 403
        return None
    except:
        return jsonify({"msg": "Authentication required."}), 401

# --- MOCK GA IMPORTS (Replace with actual logic later) ---
def fetch_all_ga_constraints_from_db() -> Dict[str, Any]:
    print("--- MOCK: Fetching Constraints from DB ---")
    return {
        'subjects': [{'subject_id': 1, 'lecture_count': 3}],
        'faculty': [{'faculty_id': 101, 'max_load': 15}],
        'rooms': [{'room_id': 201, 'capacity': 60}],
        'slots': [{'slot_id': 5, 'day': 'MONDAY'}, {'slot_id': 6, 'day': 'MONDAY'}, {'slot_id': 7, 'day': 'MONDAY'}],
        'batches': [{'batch_id': 'B1', 'student_count': 60}]
    }

def run_ga(constraints_data: Dict[str, Any]) -> list:
    print("--- MOCK: Running Genetic Algorithm (CPU Intensive) ---")
    # MOCK Output: (subject_id, faculty_id, classroom_id, time_slot_id, student_batch_id)
    return [
        (1, 101, 201, 5, 'B1'), 
        (1, 101, 201, 6, 'B1'),
        (1, 101, 201, 7, 'B1'),
    ]

# ----------------------------------------------------
# 3. AUTHENTICATION ENDPOINTS (Login and Register)
# ----------------------------------------------------

# Registration and Login code remains the same...

@app.route('/api/v1/register', methods=['POST'])
def register():
    conn = None
    cursor = None
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'Student') 

    if not username or not password:
        return jsonify({"msg": "Username and password required, bhai."}), 400

    try:
        conn = get_db_connection()
        if conn is None:
             return jsonify({"msg": "Database connection failed for registration."}), 500
             
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor = conn.cursor()
        query = "INSERT INTO users (username, hashed_password, role) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, hashed_password, role))
        conn.commit() 
        cursor.close()
        
        return jsonify({"msg": f"User {username} registered successfully! Role: {role}"}), 201

    except Error as e:
        print(f"Registration Error: {e}")
        return jsonify({"msg": "Registration failed. Username might already be taken (DBMS Error)."}), 409
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@app.route('/api/v1/login', methods=['POST'])
def login():
    conn = None
    cursor = None
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"msg": "Username aur password dono daalo, yaar."}), 400

    try:
        conn = get_db_connection()
        if conn is None:
             return jsonify({"msg": "Database connection failed for login."}), 500

        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, hashed_password, role FROM users WHERE username = %s"
        cursor.execute(query, [username])
        user_data = cursor.fetchone()
        cursor.close()

        if not user_data:
            return jsonify({"msg": "Invalid credentials (User not found)."}), 401

        if bcrypt.check_password_hash(user_data['hashed_password'], password):
            access_token = create_access_token(
                identity=user_data['id'], 
                expires_delta=False, 
                additional_claims={'role': user_data['role']} 
            )
            
            return jsonify({
                "msg": "Login Successful, bhai!",
                "token": access_token,
                "role": user_data['role']
            }), 200
        else:
            return jsonify({"msg": "Invalid credentials (Password mismatch)."}), 401
            
    except Error as e:
        print(f"Login Error: {e}")
        return jsonify({"msg": "An internal error occurred during login."}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# -----------------------------------------------------------
# 4. DATA INSERTION ENDPOINTS (ADMIN-ONLY CRUD: CREATE)
# -----------------------------------------------------------

# --- A. Subject Insertion Route (FINAL FIX HERE) ---
@app.route('/api/v1/data/add_subject', methods=['POST'])
@jwt_required()
def add_subject():
    conn = None
    cursor = None
    
    # 1. ADMIN CHECK
    auth_check = check_admin_access()
    if auth_check:
        return auth_check 
    
    # 2. DATA ACQUISITION: Form Data se data lein (JSON bypass)
    data = request.form 
    
    subject_name = data.get('subject_name')
    subject_code = data.get('subject_code')
    department_id = data.get('department_id') 
    lecture_count_str = data.get('lecture_count') # String se le rahe hain
    
    # 3. VALIDATION AND TYPE CHECK
    if not all([subject_name, subject_code, department_id, lecture_count_str]):
        return jsonify({"msg": "Validation Error: All fields are required."}), 400

    try:
        lecture_count = int(lecture_count_str)
    except ValueError:
        return jsonify({"msg": "Validation Error: Lecture count must be a number."}), 400


    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 4. DB INSERT 
        sql_query = """
        INSERT INTO timetable_subject (subject_name, subject_code, department_id, lecture_count) 
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql_query, (subject_name, subject_code, department_id, lecture_count))
        conn.commit() 
        
        return jsonify({"status": "success", "msg": f"Subject '{subject_code}' added successfully!"}), 201

    except Error as e:
        print(f"Subject Insertion Error: {e}")
        return jsonify({"status": "error", "msg": "Insertion failed. Check Subject Code uniqueness."}), 500
        
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# --- B. Faculty Insertion Route (Form Data Fix) ---
@app.route('/api/v1/data/add_faculty', methods=['POST'])
@jwt_required()
def add_faculty():
    conn = None
    cursor = None
    
    auth_check = check_admin_access()
    if auth_check: return auth_check 
        
    data = request.form # Use request.form
    name = data.get('name')
    department_id = data.get('department_id')
    max_load_str = data.get('max_load') 
    
    if not all([name, department_id, max_load_str]):
        return jsonify({"msg": "Faculty name, dept ID, and max load required, bhai."}), 400

    try:
        max_load = int(max_load_str)
    except ValueError:
        return jsonify({"msg": "Validation Error: Max load must be a number."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql_query = """
        INSERT INTO faculty_faculty (name, department_id, max_load) 
        VALUES (%s, %s, %s)
        """
        cursor.execute(sql_query, (name, department_id, max_load))
        conn.commit() 
        
        return jsonify({"status": "success", "msg": f"Faculty '{name}' added successfully!"}), 201

    except Error as e:
        print(f"Faculty Insertion Error: {e}")
        return jsonify({"status": "error", "msg": "Insertion failed. Check data validity."}), 500
        
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# --- C. Room Insertion Route (Form Data Fix) ---
@app.route('/api/v1/data/add_room', methods=['POST'])
@jwt_required()
def add_room():
    conn = None
    cursor = None
    
    auth_check = check_admin_access()
    if auth_check: return auth_check 
        
    data = request.form # Use request.form
    room_name = data.get('room_name')
    capacity_str = data.get('capacity')
    room_type = data.get('room_type', 'Theory') 
    
    if not all([room_name, capacity_str]):
        return jsonify({"msg": "Room name and capacity required, bhai."}), 400

    try:
        capacity = int(capacity_str)
    except ValueError:
        return jsonify({"msg": "Validation Error: Capacity must be a number."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql_query = """
        INSERT INTO rooms_classroom (room_name, capacity, room_type) 
        VALUES (%s, %s, %s)
        """
        cursor.execute(sql_query, (room_name, capacity, room_type))
        conn.commit() 
        
        return jsonify({"status": "success", "msg": f"Room '{room_name}' added successfully!"}), 201

    except Error as e:
        print(f"Room Insertion Error: {e}")
        return jsonify({"status": "error", "msg": "Insertion failed. Check room name uniqueness/capacity value."}), 500
        
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# --- D. GA Timetable Generation Route (Form Data Ready) ---
@app.route('/api/v1/generate_timetable', methods=['POST'])
@jwt_required()
def generate_timetable():
    auth_check = check_admin_access()
    if auth_check: 
        return auth_check 
        
    conn = None
    
    try:
        # 1. DATA ACQUISITION
        constraints = fetch_all_ga_constraints_from_db() 
        if not constraints.get('subjects') or not constraints.get('faculty'):
             return jsonify({"msg": "Error: Database is empty! Please add data first."}), 400
        
        # 2. RUN GA (The CPU-intensive step)
        final_timetable_data = run_ga(constraints) 
        
        # 3. SAVE FINAL TIMETABLE (DBMS Transaction Logic)
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM timetable_timetableentry") 
        
        insert_query = """
        INSERT INTO timetable_timetableentry 
        (subject_id, faculty_id, classroom_id, time_slot_id, student_batch_id) 
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.executemany(insert_query, final_timetable_data) 
        
        conn.commit() 
        
        return jsonify({"status": "success", "msg": "Timetable generated and saved to DB successfully!"}), 200

    except Exception as e:
        if conn: 
            conn.rollback() 
        print(f"GA Generation Failed: {e}")
        return jsonify({"status": "error", "msg": "Timetable generation failed due to server error. Changes rolled back."}), 500
        
    finally:
        if conn: conn.close()


# -----------------------------------------------------------
# 5. PROTECTED TIMETABLE ENDPOINT 
# -----------------------------------------------------------
@app.route('/api/timetable/<string:dept_id>/<string:batch_id>', methods=['GET'])
@jwt_required() 
def get_timetable_data(dept_id, batch_id):
    current_user_claims = get_jwt()
    user_role = current_user_claims.get('role')
    
    if user_role not in ['Admin', 'Faculty', 'Student']: 
        return jsonify({"msg": "Authorization failed. Role not permitted."}), 403
    
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor(dictionary=True)
        sql_query = """
        SELECT
            TS.day_of_week, 
            TIME_FORMAT(TS.start_time, '%%H:%%i') AS start_time, 
            TIME_FORMAT(TS.end_time, '%%H:%%i') AS end_time,
            SUB.subject_code, 
            SUB.subject_name,
            FAC.name AS faculty_name,
            CR.room_name, 
            CR.room_type
        FROM
            timetable_timetableentry AS TTE
        JOIN
            timetable_subject AS SUB ON TTE.subject_id = SUB.subject_id
        JOIN
            faculty_faculty AS FAC ON TTE.faculty_id = FAC.faculty_id
        JOIN
            rooms_classroom AS CR ON TTE.classroom_id = CR.room_id
        JOIN
            timetable_timeslot AS TS ON TTE.time_slot_id = TS.slot_id
        JOIN
            faculty_department AS DEPT ON SUB.department_id = DEPT.dept_id
        WHERE
            DEPT.dept_id = %s AND TTE.student_batch_id = %s
        ORDER BY
            FIELD(TS.day_of_week, 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY'), TS.start_time;
        """
        cursor.execute(sql_query, (dept_id, batch_id))
        results = cursor.fetchall()
        
        return jsonify(results)
    
    except Error as e:
        print("--- DATABASE CONNECTION/QUERY ERROR ---")
        print(f"Error Details: {e}")
        return jsonify({"error": "Failed to fetch timetable data"}), 500
        
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# -----------------
# 6. RUN THE APP
# -----------------
if __name__ == '__main__':
    print("----------------------------------------------------------")
    print("✅ SamaySudarshan Flask API Server Started Successfully! ")
    print("----------------------------------------------------------")
    app.run(debug=True, port=5000)
