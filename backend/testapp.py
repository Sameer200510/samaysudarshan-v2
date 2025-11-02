from flask import Flask, jsonify, request
from flask_cors import CORS
from config import db_config
import mysql.connector
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# ✅ Home route
@app.route('/')
def home():
    return {"message": "SamaySudarshan Flask backend is running with dummy data!"}

# ✅ Timetable API route (dummy JSON response)
@app.route('/api/timetable')
def get_timetable():
    data = [

        {
            "day_of_week": "Monday",
            "start_time": "08:00",
            "end_time": "08:55",
            "subject_code": "TOC-501",
            "subject_name": "Foundations of Data Science (Audit Course)",
            "faculty": "",
            "room_name": "CR-7"
        },
        {
            "day_of_week": "Monday",
            "start_time": "09:00",
            "end_time": "09:55",
            "subject_code": "TCS-511",
            "subject_name": "Computer Networks-I",
            "faculty": "Dr. Santosh Kumar",
            "room_name": "CR-7"
        },
        {
            "day_of_week": "Monday",
            "start_time": "09:55",
            "end_time": "10:50",
            "subject_code": "XCS-501",
            "subject_name": "Career Skills (Soft Skills)",
            "faculty": "Dr. Sakshi Gupta",
            "room_name": "CR-7"
        },
        {
            "day_of_week": "Monday",
            "start_time": "11:10",
            "end_time": "12:05",
            "subject_code": "TCS-502",
            "subject_name": "Operating Systems",
            "faculty": "Dr. Neeraj Kumar Pandey",
            "room_name": "CR-7"
        },
        {
            "day_of_week": "Monday",
            "start_time": "12:05",
            "end_time": "13:00",
            "subject_code": "TCS-503",
            "subject_name": "Database Management Systems",
            "faculty": "Dr. Vijay Singh",
            "room_name": "CR-7"
        },
        {
            "day_of_week": "Monday",
            "start_time": "13:55",
            "end_time": "15:50",
            "subject_code": "PCS-597",
            "subject_name": "Computer System Security Lab",
            "faculty": "Dr. Ankit Vishnoi",
            "room_name": "New Lab-1"
        },
        {
            "day_of_week": "Tuesday",
            "start_time": "08:00",
            "end_time": "08:55",
            "subject_code": "XCS-501",
            "subject_name": "Career Skills (Verbal)",
            "faculty": "Shweta Bajaj",
            "room_name": "CR-6"
        },
        {
            "day_of_week": "Tuesday",
            "start_time": "09:00",
            "end_time": "09:55",
            "subject_code": "TCS-511",
            "subject_name": "Computer Networks-I",
            "faculty": "Dr. Santosh Kumar",
            "room_name": "CR-7"
        },
        {
            "day_of_week": "Tuesday",
            "start_time": "09:55",
            "end_time": "10:50",
            "subject_code": "TCS-503",
            "subject_name": "Database Management Systems",
            "faculty": "Dr. Vijay Singh",
            "room_name": "CR-7"
        },
        {
            "day_of_week": "Tuesday",
            "start_time": "11:10",
            "end_time": "12:05",
            "subject_code": "TCS-502",
            "subject_name": "Operating Systems",
            "faculty": "Dr. Neeraj Kumar Pandey",
            "room_name": "CR-7"
        },
        {
            "day_of_week": "Tuesday",
            "start_time": "13:55",
            "end_time": "14:50",
            "subject_code": "TCS-597",
            "subject_name": "Computer System Security",
            "faculty": "Dr. Ankit Vishnoi",
            "room_name": "CR-2"
        },
        {
            "day_of_week": "Tuesday",
            "start_time": "14:55",
            "end_time": "15:50",
            "subject_code": "PCS-511(S)",
            "subject_name": "Operating System & Computer Networks Lab",
            "faculty": "Dr. Neeraj Kumar Pandey & Dr. Santosh Kumar",
            "room_name": "Digital Lab-2"
        },
        {
            "day_of_week": "Wednesday",
            "start_time": "08:00",
            "end_time": "08:55",
            "subject_code": "SWAYAM",
            "subject_name": "Training/Extra-Curricular Activities/LIB",
            "faculty": "",
            "room_name": ""
        },
        {
            "day_of_week": "Wednesday",
            "start_time": "09:00",
            "end_time": "09:55",
            "subject_code": "XCS-501",
            "subject_name": "Career Skills (QAR)",
            "faculty": "Mr. Abhinav Sharma",
            "room_name": "CR-7"
        },
        {
            "day_of_week": "Wednesday",
            "start_time": "09:55",
            "end_time": "10:50",
            "subject_code": "TCS-511",
            "subject_name": "Computer Networks-I",
            "faculty": "Dr. Santosh Kumar",
            "room_name": "CR-7"
        },
        {
            "day_of_week": "Wednesday",
            "start_time": "13:55",
            "end_time": "14:50",
            "subject_code": "TCS-597",
            "subject_name": "Computer System Security",
            "faculty": "Dr. Ankit Vishnoi",
            "room_name": "LT-1"
        },
        {
            "day_of_week": "Wednesday",
            "start_time": "14:55",
            "end_time": "15:50",
            "subject_code": "PCS-597",
            "subject_name": "Computer System Security Lab",
            "faculty": "Dr. Ankit Vishnoi",
            "room_name": "New Lab-1"
        },
        {
            "day_of_week": "Wednesday",
            "start_time": "16:05",
            "end_time": "17:00",
            "subject_code": "TCS-502",
            "subject_name": "Operating Systems",
            "faculty": "Dr. Neeraj Kumar Pandey",
            "room_name": "LT-7"
        },

        {
            "day_of_week": "Thursday",
            "start_time": "08:00",
            "end_time": "08:55",
            "subject_code": "TOC-501",
            "subject_name": "Foundations of Data Science (Audit Course)",
            "faculty": "",
            "room_name": "CR-7"
        },
        {
            "day_of_week": "Thursday",
            "start_time": "09:00",
            "end_time": "09:55",
            "subject_code": "CEC",
            "subject_name": "Career Excellence Classes",
            "faculty": "Mr. Akshay Rajput",
            "room_name": "LT-5"
        },
        {
            "day_of_week": "Thursday",
            "start_time": "09:55",
            "end_time": "10:50",
            "subject_code": "TCS-502",
            "subject_name": "Operating Systems",
            "faculty": "Dr. Neeraj Kumar Pandey",
            "room_name": "CR-7"
        },
        {
            "day_of_week": "Thursday",
            "start_time": "11:10",
            "end_time": "12:05",
            "subject_code": "TCS-503",
            "subject_name": "Database Management Systems",
            "faculty": "Dr. Vijay Singh",
            "room_name": "CR-7"
        },
        {
            "day_of_week": "Thursday",
            "start_time": "13:55",
            "end_time": "14:50",
            "subject_code": "TCS-597",
            "subject_name": "Computer System Security",
            "faculty": "Dr. Ankit Vishnoi",
            "room_name": "CR-6"
        },
        {
            "day_of_week": "Thursday",
            "start_time": "14:55",
            "end_time": "15:50",
            "subject_code": "PCS-503",
            "subject_name": "DBMS Lab",
            "faculty": "Dr. Vijay Singh & Mr. Sujal Bindra",
            "room_name": "New Lab-2"
        },
        {
            "day_of_week": "Thursday",
            "start_time": "16:05",
            "end_time": "17:00",
            "subject_code": "PCS-511(S)",
            "subject_name": "Operating System & Computer Networks Lab",
            "faculty": "Dr. Neeraj Kumar Pandey & Dr. Santosh Kumar",
            "room_name": "Lab-5"
        },

        {
            "day_of_week": "Friday",
            "start_time": "08:00",
            "end_time": "08:55",
            "subject_code": "TOC-501",
            "subject_name": "Foundations of Data Science (Audit Course)",
            "faculty": "",
            "room_name": "CR-7"
        },
        {
            "day_of_week": "Friday",
            "start_time": "09:00",
            "end_time": "09:55",
            "subject_code": "TCS-511",
            "subject_name": "Computer Networks-I",
            "faculty": "Dr. Santosh Kumar",
            "room_name": "CR-3"
        },
        {
            "day_of_week": "Friday",
            "start_time": "09:55",
            "end_time": "10:50",
            "subject_code": "PCS-503",
            "subject_name": "DBMS Lab",
            "faculty": "Dr. Vijay Singh & Mr. Sujal Bindra",
            "room_name": "Aryabhatta Ground Floor"
        },
        {
            "day_of_week": "Friday",
            "start_time": "11:10",
            "end_time": "12:05",
            "subject_code": "TCS-503",
            "subject_name": "Database Management Systems",
            "faculty": "Dr. Vijay Singh",
            "room_name": "CR-7"
        },
        {
            "day_of_week": "Friday",
            "start_time": "13:55",
            "end_time": "14:50",
            "subject_code": "SWAYAM",
            "subject_name": "Training/Extra-Curricular Activities/LIB",
            "faculty": "",
            "room_name": ""
        },
        {
            "day_of_week": "Friday",
            "start_time": "14:55",
            "end_time": "15:50",
            "subject_code": "TCS-597",
            "subject_name": "Computer System Security",
            "faculty": "Dr. Ankit Vishnoi",
            "room_name": "CR-6"
        },
        {
            "day_of_week": "Friday",
            "start_time": "16:05",
            "end_time": "17:00",
            "subject_code": "Elective",
            "subject_name": "Parallel Computer Architecture (Through Swayam)",
            "faculty": "Dr. Hradesh Kumar & Dr. Amit Kumar",
            "room_name": "Online"
        }

    ]
    return jsonify(data)

# ✅ Run the app
if __name__ == '__main__':
    app.run(debug=True)