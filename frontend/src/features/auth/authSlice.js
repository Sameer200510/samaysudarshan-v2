// src/features/auth/authSlice.js
import { createSlice } from "@reduxjs/toolkit";
import { jwtDecode } from "jwt-decode";

// --- Token validity helper ---
const isValidToken = (token) => {
  try {
    const { exp } = jwtDecode(token || "");
    return exp && Date.now() < exp * 1000;
  } catch {
    return false;
  }
};

// --- Initial state load ---
const savedToken = localStorage.getItem("token");
const savedRole = localStorage.getItem("role");

const initialState = {
  token: isValidToken(savedToken) ? savedToken : null,
  role: isValidToken(savedToken) ? savedRole : null,
  isAuthenticated: isValidToken(savedToken),
  loading: false,
  isAuthChecked: false, // flicker guard
};

// --- Slice ---
const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    loginSuccess: (state, action) => {
      const { token, role } = action.payload;
      state.isAuthenticated = true;
      state.token = token;
      state.role = role;
      state.loading = false;
      state.isAuthChecked = true;
      localStorage.setItem("token", token);
      localStorage.setItem("role", role);
    },
    loginFailure: (state, action) => {
      state.isAuthenticated = false;
      state.token = null;
      state.role = null;
      state.loading = false;
      state.isAuthChecked = true;
      localStorage.removeItem("token");
      localStorage.removeItem("role");
    },
    logout: (state) => {
      state.isAuthenticated = false;
      state.token = null;
      state.role = null;
      state.loading = false;
      state.isAuthChecked = true;
      localStorage.removeItem("token");
      localStorage.removeItem("role");
    },
    setLoading: (state, action) => {
      state.loading = !!action.payload;
    },
    markAuthChecked: (state) => {
      state.isAuthChecked = true;
    },
  },
});

export const { loginSuccess, loginFailure, logout, setLoading, markAuthChecked } =
  authSlice.actions;

export default authSlice.reducer;