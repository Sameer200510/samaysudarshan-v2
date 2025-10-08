import React, { useEffect, useState } from "react";
import axios from "axios";
import { Table } from "react-bootstrap";

// ✅ Subject-wise color mapping
const subjectColors = {
  "TOC-501": "#ffcccc",
  "TCS-511": "#ccffcc",
  "XCS-501": "#cce5ff",
  "CEC": "#fff3cd",
  "PCS-503": "#e2ccff",
  "PCS-601": "#ffd6a5",
  "PCS-603": "#caffbf",
  "PCS-605": "#9bf6ff",
  "RAS-601": "#fdffb6",
  "PCS-607": "#bdb2ff",
  "PCS-609": "#ffc6ff",
  "PCS-611": "#a0c4ff"
};

const WeeklyTimetable = () => {
  const [timetable, setTimetable] = useState([]);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:5000/api/timetable")
      .then((res) => setTimetable(res.data))
      .catch((err) => console.error("Error fetching timetable:", err));
  }, []);

  const timeSlots = [
    "08:00-08:55",
    "09:00-09:55",
    "09:55-10:50",
    "11:10-12:05",
    "12:05-13:00", // 👈 Lunch slot
    "13:55-14:50",
    "14:55-15:50",
    "16:05-17:00"
  ];

  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

  const getClass = (day, slot) => {
    // ✅ Lunch Break override
    if (slot === "12:05-13:00") {
      return (
        <div
          style={{
            backgroundColor: "#ffe066",
            borderRadius: "6px",
            padding: "6px",
            fontWeight: "bold"
          }}
        >
          🍴 Lunch Break
        </div>
      );
    }

    // ✅ Normal class lookup
    const entry = timetable.find(
      (item) =>
        item.day_of_week === day &&
        `${item.start_time}-${item.end_time}` === slot
    );
    if (entry) {
      const bgColor = subjectColors[entry.subject_code] || "#f8f9fa";
      return (
        <div
          style={{
            backgroundColor: bgColor,
            borderRadius: "6px",
            padding: "6px",
            fontSize: "0.85rem"
          }}
        >
          <b>{entry.subject_code}</b> <br />
          {entry.subject_name} <br />
          <small>{entry.faculty}</small> <br />
          <span className="text-muted">{entry.room_name}</span>
        </div>
      );
    }
    return <span className="text-secondary">Free</span>;
  };

  return (
    <div className="container mt-4">
      <h2 className="text-center mb-4">
        📅 Weekly Timetable – B.Tech Vth Sem CSE (Cyber Security)
      </h2>
      <Table bordered hover responsive className="align-middle text-center">
        <thead className="table-dark">
          <tr>
            <th>Day</th>
            {timeSlots.map((slot) => (
              <th key={slot}>{slot}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {days.map((day) => (
            <tr key={day}>
              <td className="fw-bold">{day}</td>
              {timeSlots.map((slot) => (
                <td key={day + slot}>{getClass(day, slot)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
};

export default WeeklyTimetable;