// src/pages/DashboardHome.js
import React, { Suspense, lazy } from "react";
// Added Box and Stack for cleaner alignment controls
import { Typography, Box, Grid, Divider, Paper, Container, Stack } from "@mui/material";
import { useSelector } from "react-redux";
// Using fun, modern icons
import SectionAddIcon from '@mui/icons-material/AddCircleOutline';
import CurriculumIcon from '@mui/icons-material/AutoStoriesOutlined';
import SubjectIcon from '@mui/icons-material/CodeOutlined';
import FacultyIcon from '@mui/icons-material/GroupsOutlined';
import RoomIcon from '@mui/icons-material/HolidayVillageOutlined';
import TimetableIcon from '@mui/icons-material/ScheduleSendOutlined';
import AdminPanelSettingsIcon from '@mui/icons-material/SettingsApplications';


// 🔹 Lazy imports (Kept as is)
const AddSectionForm = lazy(() => import("../components/Admin/AddSectionForm"));
const AssignCurriculumForm = lazy(() => import("../components/Admin/AssignCurriculumForm"));
const GenerateTimetableButton = lazy(() => import("../components/Admin/GenerateTimetableButton"));

const AddSubjectForm = lazy(() => import("../components/Admin/AddSubjectForm"));
const AddFacultyForm = lazy(() => import("../components/Admin/AddFacultyForm"));
const AddRoomForm = lazy(() => import("../components/Admin/AddRoomForm"));

// 🔹 Minimal Error Boundary (Kept as is)
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
        <Paper elevation={0} sx={{ p: 2, bgcolor: 'error.dark', color: 'white', border: '1px solid', borderColor: 'error.light', borderRadius: 2 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>ERROR: Component Failed to Render</Typography>
          <Typography variant="caption">{String(this.state.err)}</Typography>
        </Paper>
      );
    }
    return this.props.children;
  }
}

// 🔹 Reusable Card Suspense (Updated styling)
function CardSuspense({ children, minHeight = 200, title = "Loading Module..." }) {
  return (
    <Suspense
      fallback={
        <Box sx={{ p: 3, minHeight, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', bgcolor: 'primary.light', opacity: 0.8, border: '2px dashed', borderColor: 'primary.main', borderRadius: 2 }}>
          <Typography variant="h6" color="primary.dark" sx={{ mb: 1 }}>{title}</Typography>
          <Typography variant="body2" color="primary.dark">Initializing data...</Typography>
        </Box>
      }
    >
      {children}
    </Suspense>
  );
}

// 🔹 Asymmetrical Form Card (The key to the "Crazzyyy" look)
// NOTE: `height: '100%'` is crucial for aligning cards in a row.
const AsymmetricalFormCard = ({ title, description, icon: Icon, children, minHeight = 300, shadowColor = '#2196f3', sx = {} }) => (
  <Paper elevation={0} 
    sx={{ 
      p: { xs: 3, sm: 4 }, 
      borderRadius: 3, 
      height: '100%', 
      bgcolor: 'background.paper',
      // Crazzyyy Shadow Effect
      boxShadow: `8px 8px 0px 0px ${shadowColor}, 0px 0px 15px rgba(0, 0, 0, 0.1)`, 
      border: '1px solid #e0e0e0',
      transition: 'transform 0.3s ease-in-out',
      '&:hover': {
        transform: 'translateY(-4px)',
        boxShadow: `12px 12px 0px 0px ${shadowColor}, 0px 0px 20px rgba(0, 0, 0, 0.15)`,
      },
      ...sx,
      display: 'flex', // Crucial for inner height alignment
      flexDirection: 'column', // Crucial for inner height alignment
    }}
  >
    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
      {Icon && <Icon sx={{ mr: 1.5, color: 'primary.main', fontSize: 32 }} />}
      <Typography variant="h5" component="h3" sx={{ fontWeight: 800, color: 'text.primary' }}>
        {title}
      </Typography>
    </Box>
    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
      {description}
    </Typography>
    <Box sx={{ flexGrow: 1 }}> {/* The form content box is set to flexGrow: 1 */}
      <CardBoundary>
        {/* minHeight is passed here to ensure consistency while loading */}
        <CardSuspense minHeight={minHeight} title={`Loading ${title}...`}>
          {children}
        </CardSuspense>
      </CardBoundary>
    </Box>
  </Paper>
);


export default function DashboardHome() {
  const role = useSelector((s) => s.auth?.role || s.auth?.userRole) || "Admin";

  return (
    <Container maxWidth="xl" sx={{ py: { xs: 4, md: 8 }, bgcolor: '#f4f7f9' }}> {/* Light background for contrast */}
        
      {/* --------------------------- HEADER: The Crazy Title --------------------------- */}
      <Box sx={{ mb: { xs: 6, md: 8 }, p: 3, bgcolor: 'primary.dark', color: 'white', borderRadius: 2 }}>
        <Stack direction="row" alignItems="center" spacing={2}>
          <AdminPanelSettingsIcon sx={{ fontSize: 64, color: '#FFD700' }} /> {/* Gold icon */}
          <Box>
            <Typography variant="h3" component="h1" sx={{ fontWeight: 900, letterSpacing: 1 }}>
              🚀 ADMIN CONTROL GRID
            </Typography>
            <Typography variant="subtitle1" color="text.disabled" sx={{ color: '#bdbdbd' }}>
              You're logged in as <Box component="span" sx={{ fontWeight: 700, color: '#FFC107' }}>{role}</Box>! Let's get this data aligned.
            </Typography>
          </Box>
        </Stack>
      </Box>

      <Grid container spacing={5}> {/* More spacing for the crazy look */}

        {/* --------------------------- LEFT COLUMN: ACADEMIC STRUCTURE (Section 1) - TALL STACK --------------------------- */}
        <Grid item xs={12} lg={6}>
          <Box sx={{ pb: 2, borderBottom: '3px solid', borderColor: 'secondary.main', mb: 3 }}>
            <Typography variant="h4" sx={{ fontWeight: 700, color: 'secondary.dark', mb: 0.5 }}>
              1. ACADEMIC STRUCTURE
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Define your learning environment and syllabus assignments.
            </Typography>
          </Box>

          <Stack spacing={4}>
            <AsymmetricalFormCard 
              icon={SectionAddIcon} 
              title="ADD NEW SECTION" 
              description="Set up a new section/batch, ready for curriculum mapping."
              shadowColor="#FFC107" 
              minHeight={180} // Adjusted minHeight
            >
              <AddSectionForm />
            </AsymmetricalFormCard>

            <AsymmetricalFormCard 
              icon={CurriculumIcon} 
              title="ASSIGN CURRICULUM" 
              description="Map subjects to the created sections below."
              shadowColor="#9C27B0" 
              minHeight={300}
            >
              <AssignCurriculumForm />
            </AsymmetricalFormCard>
          </Stack>
        </Grid>

        {/* --------------------------- RIGHT COLUMN: CORE DATA & TIMETABLE (Section 2 & 3) - ALIGNED ROWS --------------------------- */}
        <Grid item xs={12} lg={6}>
          <Box sx={{ pb: 2, borderBottom: '3px solid', borderColor: 'primary.main', mb: 3 }}>
            <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.dark', mb: 0.5 }}>
              2. CORE DATA & TIMETABLE
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Inputs for the timetable generator. Data alignment is key!
            </Typography>
          </Box>

          <Grid container spacing={4} sx={{ mb: 4 }}>
            {/* --- ROW 1: Subjects and Faculty (Aligned) --- */}
            <Grid item xs={12} md={6} sx={{ display: 'flex' }}> {/* Ensures inner components align vertically */}
              <AsymmetricalFormCard 
                icon={SubjectIcon} 
                title="SUBJECT REGISTRATION" 
                description="Add subjects with their code and weekly commitment."
                shadowColor="#00BCD4" 
                minHeight={350} // Set a definite minimum height
              >
                <AddSubjectForm />
              </AsymmetricalFormCard>
            </Grid>

            <Grid item xs={12} md={6} sx={{ display: 'flex' }}> {/* Ensures inner components align vertically */}
              <AsymmetricalFormCard 
                icon={FacultyIcon} 
                title="FACULTY ONBOARDING" 
                description="Input new teaching staff details."
                shadowColor="#FF5722" 
                minHeight={350} // Set a definite minimum height (Must be equal to the card beside it)
              >
                <AddFacultyForm />
              </AsymmetricalFormCard>
            </Grid>

            {/* --- ROW 2: Room and Timetable Generator (Aligned) --- */}
            <Grid item xs={12} md={6} sx={{ display: 'flex' }}> {/* Ensures inner components align vertically */}
              <AsymmetricalFormCard 
                icon={RoomIcon} 
                title="ROOM ALLOCATION" 
                description="Register new rooms/labs with their capacities."
                shadowColor="#8BC34A" 
                minHeight={200} // Set a definite minimum height
              >
                <AddRoomForm />
              </AsymmetricalFormCard>
            </Grid>
            
            <Grid item xs={12} md={6} sx={{ display: 'flex' }}> {/* Ensures inner components align vertically */}
              <AsymmetricalFormCard 
                icon={TimetableIcon} 
                title="GENERATE TIMETABLE" 
                description="One click to auto-create the optimized schedule."
                shadowColor="#E91E63" 
                minHeight={200} // Set a definite minimum height (Must be equal to the card beside it)
              >
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                  <GenerateTimetableButton />
                </Box>
              </AsymmetricalFormCard>
            </Grid>

          </Grid>

        </Grid>
      </Grid>

    </Container>
  );
}