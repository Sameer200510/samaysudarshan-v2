// src/pages/DashboardHome.js
import React, { Suspense, lazy } from "react";
import { Typography, Box, Grid, Divider, Paper } from "@mui/material";
import { useSelector } from "react-redux";

// 🔹 Lazy imports (agar koi file me error ho to page poora crash na ho)
const AddSectionForm = lazy(() => import("../components/Admin/AddSectionForm"));
const AssignCurriculumForm = lazy(() => import("../components/Admin/AssignCurriculumForm"));
const GenerateTimetableButton = lazy(() => import("../components/Admin/GenerateTimetableButton"));

const AddSubjectForm = lazy(() => import("../components/Admin/AddSubjectForm"));
const AddFacultyForm = lazy(() => import("../components/Admin/AddFacultyForm"));
const AddRoomForm = lazy(() => import("../components/Admin/AddRoomForm"));

// 🔹 Minimal Error Boundary per-card level
class CardBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, err: null };
  }
  static getDerivedStateFromError(err) {
    return { hasError: true, err };
  }
  render() {
    if (this.state.hasError) {
      return (
        <Paper elevation={2} sx={{ p: 2, color: "error.main" }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>Component failed to load</Typography>
          <Typography variant="body2">{String(this.state.err)}</Typography>
        </Paper>
      );
    }
    return this.props.children;
  }
}

// 🔹 Reusable card wrapper with Suspense fallback
function CardSuspense({ children, height = 260 }) {
  return (
    <Suspense
      fallback={
        <Paper elevation={0} sx={{ p: 2, height, bgcolor: "background.default", border: "1px dashed #ddd" }}>
          <Typography variant="body2">Loading…</Typography>
        </Paper>
      }
    >
      {children}
    </Suspense>
  );
}

export default function DashboardHome() {
  const role = useSelector((s) => s.auth?.role || s.auth?.userRole) || "Admin";

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        👑 Admin Dashboard
      </Typography>
      <Typography variant="h6" color="text.secondary" gutterBottom>
        Welcome, {role}! Yahaan se naya data add karein.
      </Typography>

      <Divider sx={{ my: 4 }} />

      {/* --- NAYA LOGIC: Section & Curriculum --- */}
      <Typography variant="h5" gutterBottom sx={{ fontWeight: 500 }}>
        Step 1: Sections & Curriculum (Naya Plan)
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6} lg={5}>
          <CardBoundary>
            <CardSuspense>
              <AddSectionForm />
            </CardSuspense>
          </CardBoundary>
        </Grid>
        <Grid item xs={12} md={6} lg={7}>
          <CardBoundary>
            <CardSuspense height={320}>
              <AssignCurriculumForm />
            </CardSuspense>
          </CardBoundary>
        </Grid>
      </Grid>

      {/* --- PURAANA LOGIC: Subjects, Faculty, Rooms --- */}
      <Typography variant="h5" gutterBottom sx={{ fontWeight: 500 }}>
        Step 2: Add Core Data (Subjects, Faculty, Rooms)
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} lg={4}>
          <CardBoundary>
            <CardSuspense>
              <AddSubjectForm />
            </CardSuspense>
          </CardBoundary>
        </Grid>
        <Grid item xs={12} lg={4}>
          <CardBoundary>
            <CardSuspense>
              <AddFacultyForm />
            </CardSuspense>
          </CardBoundary>
        </Grid>
        <Grid item xs={12} lg={4}>
          <CardBoundary>
            <CardSuspense>
              <AddRoomForm />
            </CardSuspense>
          </CardBoundary>
        </Grid>
      </Grid>

      <Divider sx={{ my: 4 }} />

      <CardBoundary>
        <CardSuspense height={160}>
          <GenerateTimetableButton />
        </CardSuspense>
      </CardBoundary>
    </Box>
  );
}