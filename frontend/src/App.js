// src/App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";

import LoginPage from "./pages/Login";
import DashboardLayout from "./components/DashboardLayout";
import DashboardHome from "./pages/DashboardHome";
import SubjectListPage from "./pages/SubjectListPage";
import FacultyListPage from "./pages/FacultyListPage";
import WeeklyTimetable from "./components/WeeklyTimetable";
import ProtectedRoute from "./components/ProtectedRoute";

const Unauthorized = () => (
  <div style={{ padding: 50, textAlign: "center" }}>
    <h1>403 - Forbidden</h1>
    <p>Aapko is page ka access nahi hai.</p>
    <a href="/login">Go to Login</a>
  </div>
);

function App() {
  return (
    <Router>
      <Routes>
        {/* Public */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/unauthorized" element={<Unauthorized />} />

        {/* Admin area (nested under /admin) */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute allowedRoles={["Admin"]}>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<DashboardHome />} />
          <Route path="subjects" element={<SubjectListPage />} />
          <Route path="faculty" element={<FacultyListPage />} />
        </Route>

        {/* Generic protected (any logged-in role) */}
        <Route
          path="/timetable/view"
          element={
            <ProtectedRoute allowedRoles={["Admin", "Faculty", "Student"]}>
              <WeeklyTimetable />
            </ProtectedRoute>
          }
        />

        {/* Default & fallback */}
        <Route path="/" element={<Navigate to="/admin/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/admin/dashboard" replace />} />
      </Routes>
    </Router>
  );
}

export default App;