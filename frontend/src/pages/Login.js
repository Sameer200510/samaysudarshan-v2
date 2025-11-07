// src/pages/Login.js
import React, { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate, useLocation } from "react-router-dom";
import axiosInstance from "../api/axiosInstance";
import { loginSuccess, loginFailure, setLoading, logout } from "../features/auth/authSlice";
import { jwtDecode } from "jwt-decode";

// MUI
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  CircularProgress,
  Alert,
} from "@mui/material";
import LockIcon from "@mui/icons-material/Lock";

const isValidToken = (token) => {
  try {
    const { exp } = jwtDecode(token || "");
    return exp && Date.now() < exp * 1000;
  } catch {
    return false;
  }
};

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [statusMsg, setStatusMsg] = useState("");

  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  // jahan se redirect hua tha wahan wapas
  const from = location.state?.from?.pathname || "/admin/dashboard";

  const { isAuthenticated, loading, token, role } = useSelector((state) => state.auth);

  // ---- Mount pe token validate (flicker fix) ----
  useEffect(() => {
    const saved = token || localStorage.getItem("token");
    if (saved) {
      if (isValidToken(saved)) {
        // already valid login → go to intended page
        navigate(from, { replace: true });
      } else {
        // stale/expired token → clear everything
        dispatch(logout());
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Auth state change hone par safe redirect
  useEffect(() => {
    if (isAuthenticated && token && isValidToken(token)) {
      if (role === "Admin") {
        navigate(from, { replace: true });
      } else {
        navigate("/timetable/view", { replace: true });
      }
    }
  }, [isAuthenticated, token, role, from, navigate]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setStatusMsg("");
    dispatch(setLoading(true));

    try {
      const { data } = await axiosInstance.post("/api/v1/login", {
        username: username.trim(),
        password: password,
      });

      const { token, role, msg } = data;
      // (slice should store token+role to localStorage)
      dispatch(loginSuccess({ token, role }));
      setStatusMsg(msg || "Login Successful!");

      // immediate redirect
      if (role === "Admin") {
        navigate(from, { replace: true });
      } else {
        navigate("/timetable/view", { replace: true });
      }
    } catch (error) {
      const errorMsg = error?.response?.data?.msg || "Login failed. Check credentials or server.";
      dispatch(loginFailure(errorMsg));
      setStatusMsg(errorMsg);
    } finally {
      dispatch(setLoading(false));
    }
  };

  // Agar authenticated & valid token, login page render na karo (no flicker)
  if (isAuthenticated && token && isValidToken(token)) return null;

  return (
    <Container component="main" maxWidth="xs">
      <Paper
        elevation={10}
        sx={{
          p: 4,
          mt: 8,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          borderRadius: "10px",
        }}
      >
        <LockIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
        <Typography component="h1" variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
          SamaySudarshan Login
        </Typography>

        {statusMsg && (
          <Alert
            severity={
              statusMsg.toLowerCase().includes("fail") || statusMsg.toLowerCase().includes("error")
                ? "error"
                : "success"
            }
            sx={{ width: "100%", mb: 2 }}
          >
            {statusMsg}
          </Alert>
        )}

        <Box component="form" onSubmit={handleLogin} noValidate sx={{ width: "100%" }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="username"
            label="Username / Admin ID"
            name="username"
            autoFocus
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            variant="outlined"
          />
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            variant="outlined"
            sx={{ mb: 3 }}
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            disabled={loading}
            sx={{ mt: 1, mb: 2, height: "48px", position: "relative" }}
          >
            {loading ? <CircularProgress size={24} sx={{ color: "white" }} /> : "Sign In"}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
}

export default Login;