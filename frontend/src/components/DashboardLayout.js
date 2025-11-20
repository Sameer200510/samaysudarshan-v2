import React, { useState } from "react";
import {
  Box, Drawer, AppBar, Toolbar, Typography, Divider,
  List, ListItem, ListItemButton, ListItemIcon, ListItemText,
  IconButton, CssBaseline, Tooltip
} from "@mui/material";
import { Outlet, useNavigate } from "react-router-dom";
import MenuIcon from "@mui/icons-material/Menu";
import DashboardIcon from "@mui/icons-material/Dashboard";
import SubjectIcon from "@mui/icons-material/Book";
import PeopleIcon from "@mui/icons-material/People";
import LogoutIcon from "@mui/icons-material/Logout";
import ViewWeekIcon from "@mui/icons-material/ViewWeek";
import { useDispatch } from "react-redux";
import { logout } from "../features/auth/authSlice";

const drawerWidth = 240;

const menuItems = [
  { text: "Dashboard", icon: <DashboardIcon />, path: "/admin/dashboard" },
  { text: "Manage Subjects", icon: <SubjectIcon />, path: "/admin/subjects" },
  { text: "Manage Faculty", icon: <PeopleIcon />, path: "/admin/faculty" },
  { text: "View Timetable", icon: <ViewWeekIcon />, path: "/timetable/view" },
];

export default function DashboardLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const handleDrawerToggle = () => setMobileOpen((v) => !v);
  const goTo = (path) => { navigate(path); setMobileOpen(false); };
  const handleLogout = () => { dispatch(logout()); navigate("/login", { replace: true }); };

  const drawer = (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <Toolbar sx={{ backgroundColor: "primary.main", minHeight: "64px!important" }}>
        <Typography variant="h6" noWrap color="white" sx={{ m: "0 auto" }}>
          SamaySudarshan
        </Typography>
      </Toolbar>
      <Divider />
      <List sx={{ flexGrow: 1 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton onClick={() => goTo(item.path)}>
              <ListItemIcon sx={{ color: "inherit" }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider />
      <List>
        <ListItem disablePadding>
          <ListItemButton onClick={handleLogout}>
            <ListItemIcon><LogoutIcon color="error" /></ListItemIcon>
            <ListItemText primary="Logout" />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: "flex" }}>
      <CssBaseline />

      <AppBar
        position="fixed"
        elevation={1}
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml:   { sm: `${drawerWidth}px` },
          backgroundColor: "#fff",
          color: "#1e293b",
          borderBottom: "1px solid #eef2f7",
        }}
      >
        <Toolbar sx={{ minHeight: 64 }}>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: "none" } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>Admin Panel</Typography>
          <Tooltip title="Logout">
            <IconButton color="error" onClick={handleLogout} sx={{ display: { xs: "none", sm: "block" } }}>
              <LogoutIcon />
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Box component="nav" sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }} aria-label="sidebar">
        {/* Mobile */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: "block", sm: "none" },
            "& .MuiDrawer-paper": {
              width: drawerWidth, boxSizing: "border-box",
              backgroundColor: "#ffffff", borderRight: "1px solid #eee",
            },
          }}
        >
          {drawer}
        </Drawer>
        {/* Desktop */}
        <Drawer
          variant="permanent"
          open
          sx={{
            display: { xs: "none", sm: "block" },
            "& .MuiDrawer-paper": {
              width: drawerWidth, boxSizing: "border-box",
              backgroundColor: "#ffffff", borderRight: "1px solid #eee",
            },
          }}
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          backgroundColor: "#f5f7fb",
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <Toolbar />

        {/* Centered page container for consistent alignment */}
        <Box
          className="page-container"
          sx={{
            maxWidth: 1200,          // <- uniform width
            mx: "auto",              // center horizontally
            px: { xs: 2, sm: 3 },    // side padding
            py: { xs: 2, sm: 3 },    // top/bottom padding
            width: "100%",
          }}
        >
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}