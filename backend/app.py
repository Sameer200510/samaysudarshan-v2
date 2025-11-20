# C:\Users\SAMEER LOHANI\samaysudarshan-v2\backend\app.py
# FINAL UPDATED VERSION (GA integrated via timetable_ga + JWT expiry + robust room-type)

from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    create_access_token, jwt_required, JWTManager,
    get_jwt, get_jwt_identity
)
from typing import Dict, Any
from datetime import timedelta
import random
import os

# --- DB connection helper ---
from db_connector import get_db_connection

# --- Clean GA integration (NEW) ---
from timetable_ga import (
    run_ga, GAInput, Gene, Subject, Section, Room, Faculty, chromosome_to_rows
)

# -------------------------
# APP INIT
# -------------------------
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Secrets (env var preferred)
app.config['SECRET_KEY'] = os.environ.get('APP_SECRET_KEY', 'samaysudarshan_very_secret_key_123')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'samaysudarshan_jwt_secret_key_456')

# ✅ Tokens now expire in 8 hours
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=8)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# -------------------------
# AUTH HELPERS
# -------------------------
def check_admin_access():
    """Ensure current user has Admin role."""
    try:
        claims = get_jwt()
        if claims.get('role') != 'Admin':
            return jsonify({"msg": "Authorization failed. Admin access required."}), 403
        return None
    except Exception:
        return jsonify({"msg": "Authentication required."}), 401

# -------------------------
# JWT ERROR CALLBACKS
# -------------------------
@jwt.invalid_token_loader
def invalid_token_callback(reason):
    return jsonify({"msg": f"Invalid token: {reason}"}), 401

@jwt.unauthorized_loader
def missing_token_callback(reason):
    return jsonify({"msg": "Missing Authorization Header"}), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "Token expired"}), 401

# -------------------------
# AUTH ROUTES
# -------------------------
@app.route('/api/v1/register', methods=['POST'])
def register():
    conn = None; cursor = None
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'Student')

    if not username or not password:
        return jsonify({"msg": "Username and password required."}), 400

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"msg": "Database connection failed for registration."}), 500

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor = conn.cursor()
        query = "INSERT INTO users (username, hashed_password, role) VALUES (%s, %s, %s)"
        cursor.execute(query, (username.strip(), hashed_password, role))
        conn.commit()
        return jsonify({"msg": f"User {username} registered successfully!", "role": role}), 201

    except Error as e:
        print(f"Registration Error: {e}")
        return jsonify({"msg": "Registration failed. Username might already be taken."}), 409
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route('/api/v1/login', methods=['POST'])
def login():
    conn = None; cursor = None
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Username aur password dono daalo."}), 400

    try:
        conn = get_db_connection()
        if conn is None:
            print("Login Error: DB connection failed")
            return jsonify({"msg": "Database connection failed for login."}), 500

        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, hashed_password, role FROM users WHERE username = %s"
        cursor.execute(query, [username])
        user = cursor.fetchone()

        if not user:
            return jsonify({"msg": "Invalid credentials (user not found)."}), 401

        if bcrypt.check_password_hash(user['hashed_password'], password):
            # ✅ Use configured expiry (8h)
            access_token = create_access_token(
                identity=str(user['id']),
                additional_claims={'role': user['role']}
            )
            return jsonify({"msg": "Login Successful!", "token": access_token, "role": user['role']}), 200
        else:
            return jsonify({"msg": "Invalid credentials (password mismatch)."}), 401

    except Error as e:
        print(f"Login Error: {e}")
        return jsonify({"msg": "An internal error occurred during login."}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# -------------------------
# ADMIN CREATE ROUTES
# -------------------------

# A) SUBJECT INSERTION
@app.route('/api/v1/add_subject', methods=['POST'])
@jwt_required()
def add_subject():
    auth_check = check_admin_access()
    if auth_check: return auth_check

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"msg": "Invalid or empty JSON"}), 400

    subject_name = data.get('subject_name')
    subject_code = data.get('subject_code')
    department_id_val = data.get('department_id')
    lecture_count_val = data.get('lecture_count')

    # Optional NEW
    subj_type = (data.get('type') or 'THEORY').upper()
    contiguous_size = int(data.get('contiguous_block_size') or 1)

    if not all([subject_name, subject_code, department_id_val, lecture_count_val]):
         return jsonify({"msg": "Validation Error: All fields are required."}), 400

    try:
        department_id = str(department_id_val)
        lecture_count = int(lecture_count_val)
    except (TypeError, ValueError):
        return jsonify({"msg": "Type Error: Lecture count must be an integer."}), 422

    conn = None; cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_sql = """
            INSERT INTO timetable_subject
            (subject_code, subject_name, lecture_count, department_id, type, contiguous_block_size)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (subject_code, subject_name, lecture_count, department_id, subj_type, contiguous_size))
        conn.commit()
        new_id = cursor.lastrowid
        return jsonify({"status": "success", "message": "Subject added successfully", "subject_id": new_id}), 201

    except Error as e:
        print(f"Subject Insertion Error: {e}")
        return jsonify({"status": "error", "msg": f"Insertion failed. Check constraints. Error: {e}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# B) FACULTY INSERTION
@app.route('/api/v1/add_faculty', methods=['POST'])
@jwt_required()
def add_faculty():
    auth_check = check_admin_access()
    if auth_check: return auth_check

    data = request.get_json(silent=True)
    if data is None: return jsonify({"msg": "Invalid JSON"}), 400

    faculty_name = data.get('faculty_name')
    faculty_id_code = data.get('faculty_id_code')
    designation = data.get('designation')
    email = data.get('email')
    department_id_val = data.get('department_id')
    max_load_val = data.get('max_load')

    if not all([faculty_name, faculty_id_code, department_id_val, max_load_val]):
        return jsonify({"msg": "Faculty name, ID Code, Department, and Max Load required."}), 400

    try:
        dept_id_str = str(department_id_val)
        max_load_int = int(max_load_val)
    except (TypeError, ValueError):
        return jsonify({"msg": "department_id and max_load must be valid types."}), 422

    conn = None; cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_sql = """
            INSERT INTO faculty_faculty (name, faculty_id_code, designation, email, department_id, max_load)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (faculty_name, faculty_id_code, designation, email, dept_id_str, max_load_int))
        conn.commit()
        return jsonify({"status": "success", "message": "Faculty added successfully", "faculty_id": cursor.lastrowid}), 201

    except Error as e:
        print(f"Faculty Insertion Error: {e}")
        return jsonify({"status": "error", "msg": "Insertion failed. Check unique constraints/department id."}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# C) ROOM INSERTION
@app.route('/api/v1/add_room', methods=['POST'])
@jwt_required()
def add_room():
    auth_check = check_admin_access()
    if auth_check: return auth_check

    data = request.get_json(silent=True)
    if data is None: return jsonify({"msg": "Invalid JSON"}), 400

    room_name = data.get('room_name')
    room_capacity_val = data.get('room_capacity')
    room_type = data.get('room_type', 'LECTURE')
    is_available = data.get('is_available', True)

    if not room_name or room_capacity_val is None:
        return jsonify({"msg": "Room name and capacity required."}), 400

    try:
        capacity = int(room_capacity_val)
    except (TypeError, ValueError):
        return jsonify({"msg": "capacity must be an integer."}), 422

    # ✅ Robust room type normalization
    rt_in = str(room_type or "").strip().upper()
    if "LAB" in rt_in:
        room_type_db = "LAB"
    elif "LECTURE" in rt_in or "THEORY" in rt_in or "LEC" in rt_in:
        room_type_db = "LECTURE"
    else:
        room_type_db = "LECTURE"

    is_available_db = 1 if bool(is_available) else 0

    conn = None; cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql_query = "INSERT INTO rooms_classroom (room_name, capacity, room_type, is_available) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_query, (room_name, capacity, room_type_db, is_available_db))
        conn.commit()
        return jsonify({"status": "success", "message": f"Room '{room_name}' added!", "room_id": cursor.lastrowid}), 201

    except Error as e:
        print(f"Room Insertion Error: {e}")
        return jsonify({"status": "error", "message": "Insertion failed. Check room name uniqueness."}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# ---------------------------------------------
# --- NEW SECTION & CURRICULUM ROUTES ---
# ---------------------------------------------
@app.route('/api/v1/add_section', methods=['POST'])
@jwt_required()
def add_section():
    auth_check = check_admin_access()
    if auth_check: return auth_check
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid JSON data"}), 400
    section_name = data.get('section_name')
    dept_id = data.get('dept_id')
    student_count = data.get('student_count')
    if not all([section_name, dept_id, student_count]):
        return jsonify({"message": "All fields are required"}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO sections (section_name, dept_id, student_count) VALUES (%s, %s, %s)"
        cursor.execute(query, (section_name, str(dept_id), int(student_count)))
        conn.commit()
        return jsonify({"status": "success", "message": f"Section '{section_name}' added!"}), 201
    except Error as e:
        print(f"Section Add Error: {e}")
        return jsonify({"status": "error", "message": f"DB Error: {e}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route('/api/v1/assign_curriculum', methods=['POST'])
@jwt_required()
def assign_curriculum():
    auth_check = check_admin_access()
    if auth_check: return auth_check
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid JSON data"}), 400
    section_id = data.get('section_id')
    subject_id = data.get('subject_id')
    faculty_id = data.get('faculty_id')
    if not all([section_id, subject_id, faculty_id]):
        return jsonify({"message": "All 3 IDs are required"}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO curriculum (section_id, subject_id, faculty_id) VALUES (%s, %s, %s)"
        cursor.execute(query, (int(section_id), int(subject_id), int(faculty_id)))
        conn.commit()
        return jsonify({"status": "success", "message": "Curriculum assigned successfully!"}), 201
    except Error as e:
        print(f"Curriculum Assign Error: {e}")
        if getattr(e, "errno", None) == 1062:
            return jsonify({"status": "error", "message": "This subject is already assigned to this section."}), 409
        return jsonify({"status": "error", "message": f"DB Error: {e}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# --- Dropdown GETs ---
@app.route('/api/v1/sections', methods=['GET'])
@jwt_required()
def get_sections():
    conn = None; cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # ✅ dept_id bhi bhejo; DataGrid ke liye 'id' bhi set kar do
        cursor.execute("""
            SELECT section_id, section_name, dept_id
            FROM sections
            ORDER BY section_name
        """)
        rows = cursor.fetchall()
        for r in rows:
            r['id'] = r['section_id']       # DataGrid friendly
        return jsonify(rows), 200
    except Error as e:
        print(f"/api/v1/sections error: {e}")
        return jsonify({"message": f"DB Error: {e}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route('/api/v1/subjects', methods=['GET'])
@jwt_required()
def get_subjects():
    conn = None; cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                s.subject_id, 
                s.subject_name, 
                s.subject_code, 
                s.lecture_count,
                s.type,
                s.contiguous_block_size,
                d.dept_name 
            FROM timetable_subject AS s
            JOIN faculty_department AS d ON s.department_id = d.dept_id
            ORDER BY s.subject_name
        """
        cursor.execute(query)
        results = cursor.fetchall()
        for row in results:
            row['id'] = row['subject_id']
        return jsonify(results)
    except Error as e:
        print(f"Get Subjects Error: {e}")
        return jsonify({"message": "Failed to fetch subjects"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route('/api/timetable/section/<int:section_id>', methods=['GET'])
@jwt_required()
def get_timetable_by_section(section_id):
    claims = get_jwt()
    if claims.get('role') not in ['Admin', 'Faculty', 'Student']:
        return jsonify({"msg": "Authorization failed. Role not permitted."}), 403
    conn = None; cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
        SELECT
            TS.day_of_week,
            TIME_FORMAT(TS.start_time, '%%H:%%i') AS start_time,
            TIME_FORMAT(TS.end_time, '%%H:%%i') AS end_time,
            SUB.subject_code, SUB.subject_name, FAC.name AS faculty_name,
            CR.room_name, CR.room_type
        FROM timetable_timetableentry AS TTE
        JOIN timetable_subject AS SUB ON TTE.subject_id = SUB.subject_id
        JOIN faculty_faculty AS FAC ON TTE.faculty_id = FAC.faculty_id
        JOIN rooms_classroom AS CR ON TTE.classroom_id = CR.room_id
        JOIN timetable_timeslot AS TS ON TTE.time_slot_id = TS.slot_id
        WHERE TTE.student_batch_id = %s
        ORDER BY FIELD(TS.day_of_week,'MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY'), TS.start_time;
        """
        cursor.execute(sql, (section_id,))
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        print(f"Timetable fetch error: {e}")
        return jsonify({"error": "Failed to fetch timetable data"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route('/api/v1/faculty', methods=['GET'])
@jwt_required()
def get_faculty():
    conn = None; cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT faculty_id, name, faculty_id_code FROM faculty_faculty ORDER BY name")
        results = cursor.fetchall()
        return jsonify(results)
    except Error as e:
        return jsonify({"message": f"DB Error: {e}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# ---------------------------------------------
# --- GA TIMETABLE GENERATION ---
# ---------------------------------------------
@app.route('/api/v1/generate_timetable', methods=['POST'])
@jwt_required()
def generate_timetable():
    auth_check = check_admin_access()
    if auth_check:
        return auth_check
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"msg": "GA Error: Database connection failed."}), 500
        cursor = conn.cursor(dictionary=True)

        # ----------------------------
        # sections
        # ----------------------------
        cursor.execute("SELECT section_id, section_name, student_count FROM sections")
        sec_rows = cursor.fetchall()
        sections = {
            r['section_id']: Section(r['section_id'], r['section_name'], int(r['student_count']))
            for r in sec_rows
        }

        # ----------------------------
        # subjects (derive type + block if missing)
        # ----------------------------
        cursor.execute("""
            SELECT 
                subject_id,
                COALESCE(lecture_count, 0) AS lecture_count,
                UPPER(COALESCE(subject_code, '')) AS s_code,
                UPPER(COALESCE(subject_name, '')) AS s_name,
                UPPER(COALESCE(type, '')) AS s_type,
                COALESCE(contiguous_block_size, 0) AS csize
            FROM timetable_subject
        """)
        sub_rows = cursor.fetchall()

        LAB_HINTS = ("LAB", "PRACTICAL", "PRAC", "PR", "WORKSHOP", "WS")

        def _derive(sub):
            if sub["s_type"] == "LAB":
                dtype = "LAB"
            elif sub["s_type"] == "THEORY":
                dtype = "THEORY"
            else:
                text = f'{sub["s_code"]} {sub["s_name"]}'
                if any(h in text for h in LAB_HINTS) or int(sub["csize"] or 0) >= 2:
                    dtype = "LAB"
                else:
                    dtype = "THEORY"
            csize = int(sub["csize"] or 0)
            if csize <= 0:
                csize = 2 if dtype == "LAB" else 1
            return dtype, csize

        subjects = {}
        for r in sub_rows:
            dtype, csize = _derive(r)
            subjects[r["subject_id"]] = Subject(
                subject_id=r["subject_id"],
                lecture_count=int(r["lecture_count"]),
                subj_type=dtype,
                contiguous_block_size=int(csize)
            )

        # LAB feasibility quick check
        for s in subjects.values():
            if s.subj_type == 'LAB' and (s.lecture_count % s.contiguous_block_size != 0):
                return jsonify({
                    "status": "error",
                    "msg": (
                        f"Invalid LAB config for subject_id={s.subject_id}: "
                        f"lecture_count ({s.lecture_count}) must be multiple of "
                        f"contiguous_block_size ({s.contiguous_block_size})."
                    )
                }), 400

        # ----------------------------
        # rooms
        # ----------------------------
        cursor.execute("""
            SELECT room_id, UPPER(room_type) AS room_type, capacity
            FROM rooms_classroom
            WHERE is_available = 1
        """)
        room_rows = cursor.fetchall()

        def _norm_room(rt: str) -> str:
            if not rt:
                return 'LECTURE'
            u = rt.upper()
            return 'LAB' if 'LAB' in u else 'LECTURE'

        rooms = {
            r['room_id']: Room(r['room_id'], _norm_room(r['room_type']), int(r['capacity']))
            for r in room_rows
        }

        # ----------------------------
        # faculty
        # ----------------------------
        cursor.execute("SELECT faculty_id, COALESCE(max_load,16) AS max_load FROM faculty_faculty")
        f_rows = cursor.fetchall()
        faculty = {r['faculty_id']: Faculty(r['faculty_id'], int(r['max_load'])) for r in f_rows}

        # ----------------------------
        # curriculum
        # ----------------------------
        cursor.execute("SELECT section_id, subject_id, faculty_id FROM curriculum")
        curriculum = [
            (int(r['section_id']), int(r['subject_id']), int(r['faculty_id']))
            for r in cursor.fetchall()
        ]

        # ----------------------------
        # timeslots (ordered + usable)
        # ----------------------------
        cursor.execute("""
            SELECT slot_id, day_of_week,
                   TIME_FORMAT(start_time,'%H:%i') AS st
            FROM timetable_timeslot
            ORDER BY FIELD(day_of_week,'MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY','SUNDAY'),
                     start_time
        """)
        ts_rows = cursor.fetchall()

        # slot order
        cursor.execute("""
            SELECT slot_id, TIME_FORMAT(start_time,'%H:%i') AS st
            FROM timetable_timeslot
            ORDER BY FIELD(day_of_week,'MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY','SUNDAY'),
                     start_time
        """)
        slot_rows = cursor.fetchall()
        slot_order = [int(r["slot_id"]) for r in slot_rows]

        # periods/day and days
        first_day = ts_rows[0]['day_of_week'] if ts_rows else None
        periods_per_day = sum(1 for r in ts_rows if r['day_of_week'] == first_day) if first_day else 0
        days = len({r['day_of_week'] for r in ts_rows})

        # usable set
        cursor.execute("SHOW COLUMNS FROM timetable_timeslot LIKE 'is_usable'")
        has_is_usable = cursor.fetchone() is not None
        if has_is_usable:
            cursor.execute("SELECT slot_id FROM timetable_timeslot WHERE is_usable=1")
            usable = {int(r['slot_id']) for r in cursor.fetchall()}
        else:
            usable = set(slot_order)  # all slots usable by default

        # ----------------------------
        # compute lunch window slots (10:50 - 13:55) across all days
        # ----------------------------
        # NOTE: times in DB are expected as HH:MM (24h). We compare lexicographically.
        LUNCH_START = "10:50"
        LUNCH_END = "13:55"
        lunch_window_slots = set()
        # we already fetched slot_rows with start times
        for r in slot_rows:
            st = r.get("st") or ""
            try:
                sid = int(r.get("slot_id"))
            except Exception:
                continue
            if LUNCH_START <= st <= LUNCH_END:
                lunch_window_slots.add(sid)

        # ----------------------------
        # faculty unavailability
        # ----------------------------
        cursor.execute("SHOW TABLES LIKE 'faculty_unavailability'")
        if cursor.fetchone():
            cursor.execute("SELECT faculty_id, slot_id FROM faculty_unavailability")
            fu_rows = cursor.fetchall()
            fac_unavail = {}
            for r in fu_rows:
                fid = int(r['faculty_id']); sid = int(r['slot_id'])
                fac_unavail.setdefault(fid, set()).add(sid)
        else:
            fac_unavail = {}

        if not sections or not subjects or not rooms or not curriculum or not usable:
            return jsonify({"msg": "Error: Database is empty! Please add Curriculum, Rooms, and Time Slots first."}), 400

        # ----------------------------
        # GAInput — FINAL (include lunch_slots)
        # ----------------------------
        # NOTE: timetable_ga.models.GAInput must be updated to accept lunch_slots parameter (set of slot_ids)
        data = GAInput(
            sections=sections,
            subjects=subjects,
            curriculum=curriculum,
            rooms=rooms,
            faculty=faculty,
            faculty_unavailability=fac_unavail,
            timeslots_usable=usable,
            periods_per_day=periods_per_day,
            days=days,
            slot_order=slot_order,
            lunch_slots=lunch_window_slots,   # <-- pass lunch window to GA
        )

        # ----------------------------
        # Run GA
        # ----------------------------
        print(f"--- Starting Genetic Timetable Algorithm ---")
        # IMPORTANT: use parameters matching timetable_ga.run_ga(...) signature
        result = run_ga(
            data,
            population_size=80,
            generations=300,
            tournament_k=3,
            crossover_rate=0.9,   # use crossover_rate if your ga.py expects it
            mutate_rate=0.05,     # rename/adjust to match your ga.py (mutate_rate used in latest ga.py)
            elitism_fraction=0.08,
            seed=None
        )

        fitness = result["fitness"]
        eval_bd = result["eval"]
        best = result["best_chromosome"]

        # encode rows to DB
        rows = chromosome_to_rows(best)
        values = [
            (int(r["subject_id"]), int(r["faculty_id"]), int(r["room_id"]), int(r["slot_id"]), int(r["section_id"]))
            for r in rows
        ]

        save_cursor = conn.cursor()
        save_cursor.execute("DELETE FROM timetable_timetableentry")

        insert_query = """
            INSERT INTO timetable_timetableentry 
            (subject_id, faculty_id, classroom_id, time_slot_id, student_batch_id) 
            VALUES (%s, %s, %s, %s, %s)
        """
        save_cursor.executemany(insert_query, values)
        conn.commit()

        return jsonify({
            "status": "success",
            "msg": f"Timetable generated and saved! {len(values)} lectures scheduled.",
            "meta": {
                "fitness": fitness,
                "generations": result.get("generations"),
                "violations_found": sum(eval_bd.get("soft_breakdown", {}).values()) if eval_bd else None,
                "hard_violations": eval_bd.get("hard_breakdown", {}) if eval_bd else {}
            },
            "timetable_json": rows,
            # optionally return the lunch window slots so frontend can show lunch cards
            "lunch_slots": sorted(list(lunch_window_slots))
        }), 200

    except Error as e:
        if conn: conn.rollback()
        print(f"GA Generation Failed (MySQL Error): {e}")
        return jsonify({"status": "error", "msg": f"Timetable generation failed. DB Error: {e}"}), 500
    except Exception as e:
        print(f"GA Generation Failed (Python Error): {e}")
        return jsonify({"status": "error", "msg": f"A server error occurred: {e}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# -------------------------
# CRUD ROUTES (UPDATE/DELETE)
# -------------------------
@app.route('/api/v1/subject/<int:subject_id>', methods=['PUT'])
@jwt_required()
def update_subject(subject_id):
    auth_check = check_admin_access()
    if auth_check: return auth_check
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid JSON data"}), 400
    subject_name = data.get('subject_name')
    subject_code = data.get('subject_code')
    lecture_count = data.get('lecture_count')
    subj_type = (data.get('type') or 'THEORY').upper()
    contiguous_size = int(data.get('contiguous_block_size') or 1)
    if not all([subject_name, subject_code, lecture_count]):
        return jsonify({"message": "All fields are required"}), 400
    conn = None; cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            UPDATE timetable_subject 
            SET subject_name = %s, subject_code = %s, lecture_count = %s, type = %s, contiguous_block_size = %s
            WHERE subject_id = %s
        """
        cursor.execute(query, (subject_name, subject_code, int(lecture_count), subj_type, contiguous_size, subject_id))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "Subject not found"}), 404
        return jsonify({"status": "success", "message": "Subject updated successfully"}), 200
    except Error as e:
        print(f"Update Subject Error: {e}")
        return jsonify({"status": "error", "message": f"DB Error: {e}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route('/api/v1/subject/<int:subject_id>', methods=['DELETE'])
@jwt_required()
def delete_subject(subject_id):
    auth_check = check_admin_access()
    if auth_check: return auth_check
    conn = None; cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM curriculum WHERE subject_id = %s", (subject_id,))
        if cursor.fetchone():
            return jsonify({
                "status": "error", 
                "message": "Cannot delete subject. It is already assigned to a section."
            }), 409
        query = "DELETE FROM timetable_subject WHERE subject_id = %s"
        cursor.execute(query, (subject_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "Subject not found"}), 404
        return jsonify({"status": "success", "message": "Subject deleted successfully"}), 200
    except Error as e:
        print(f"Delete Subject Error: {e}")
        return jsonify({"status": "error", "message": f"DB Error: {e}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# -------------------------
# PROTECTED TIMETABLE FETCH
# -------------------------
@app.route('/api/timetable/<string:dept_id>/<string:batch_id>', methods=['GET'])
@jwt_required()
def get_timetable_data(dept_id, batch_id):
    claims = get_jwt()
    if claims.get('role') not in ['Admin', 'Faculty', 'Student']:
        return jsonify({"msg": "Authorization failed. Role not permitted."}), 403
    conn = None; cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)
        sql_query = """
    SELECT
    TS.day_of_week,
    TIME_FORMAT(TS.start_time, '%H:%i') AS start_time,
    TIME_FORMAT(TS.end_time,   '%H:%i') AS end_time,
    SUB.subject_code, SUB.subject_name, FAC.name AS faculty_name,
    CR.room_name, CR.room_type
    FROM timetable_timetableentry AS TTE
    JOIN timetable_subject AS SUB ON TTE.subject_id = SUB.subject_id
    JOIN faculty_faculty AS FAC ON TTE.faculty_id = FAC.faculty_id
    JOIN rooms_classroom AS CR ON TTE.classroom_id = CR.room_id
    JOIN timetable_timeslot AS TS ON TTE.time_slot_id = TS.slot_id
    JOIN sections AS SEC ON TTE.student_batch_id = SEC.section_id
    WHERE SEC.dept_id = %s AND TTE.student_batch_id = %s
    ORDER BY FIELD(TS.day_of_week,'MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY'),
         TS.start_time;
"""
        cursor.execute(sql_query, (dept_id, batch_id))
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        print("--- DATABASE CONNECTION/QUERY ERROR ---")
        print(f"Error Details: {e}")
        return jsonify({"error": "Failed to fetch timetable data"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# -------------------------
# RUN APP
# -------------------------
if __name__ == '__main__':
    print("----------------------------------------------------------")
    print("✅ SamaySudarshan Flask API Server Started Successfully! ")
    print("--------------------------------G-V-2-Multi-Section-Ready")
    app.run(debug=True, port=5000)
