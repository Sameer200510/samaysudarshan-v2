// src/components/DashboardLayout.js
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
import { logout } from "../features/auth/authSlice"; // ✅ use logout action

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

  const goTo = (path) => {
    navigate(path);
    setMobileOpen(false); // ✅ close on mobile
  };

  const handleLogout = () => {
    dispatch(logout());                 // ✅ clear redux + localStorage
    navigate("/login", { replace: true });
  };

  const drawer = (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <Toolbar sx={{ backgroundColor: "primary.main", minHeight: "64px!important" }}>
        <Typography variant="h6" noWrap component="div" color="white" sx={{ margin: "0 auto" }}>
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
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          backgroundColor: "white",
          color: "#333",
        }}
        elevation={1}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: "none" } }}
          >
            <MenuIcon />
          </IconButton>

          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Admin Panel
          </Typography>

          <Tooltip title="Logout">
            <IconButton color="error" onClick={handleLogout} sx={{ display: { xs: "none", sm: "block" } }}>
              <LogoutIcon />
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>

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
              boxSizing: "border-box",
              width: drawerWidth,
              backgroundColor: "#ffffff",
              borderRight: "1px solid #eee",
            },
          }}
        >
          {drawer}
        </Drawer>
        {/* Desktop */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: "none", sm: "block" },
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              width: drawerWidth,
              backgroundColor: "#ffffff",
              borderRight: "1px solid #eee",
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          backgroundColor: "#f4f6f8",
          minHeight: "100vh",
        }}
      >
        <Toolbar />
        {/* 👇 nested routes render here */}
        <Outlet />
      </Box>
    </Box>
  );
}