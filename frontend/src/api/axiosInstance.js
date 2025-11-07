// src/api/axiosInstance.js
import axios from "axios";
import store from "../app/store";
import { logout } from "../features/auth/authSlice";

// 1️⃣ Axios instance (base config)
const axiosInstance = axios.create({
  baseURL: "http://127.0.0.1:5000", // Flask backend
  headers: {
    "Content-Type": "application/json",
  },
});

// 2️⃣ Request interceptor — har API call ke saath token lagana
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && !config.url.endsWith('/login') && !config.url.endsWith('/register')) {
    config.headers['Authorization'] = 'Bearer ' + token;
  }
  return config;

  },
  (error) => Promise.reject(error)
);

// 3️⃣ Response interceptor — 401/403 aate hi logout + redirect
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    if (status === 401 || status === 403) {
      console.warn("⚠️ Token expired or unauthorized. Logging out...");
      store.dispatch(logout());

      // Clean localStorage (safety)
      localStorage.removeItem("token");
      localStorage.removeItem("role");

      // Redirect only if not already on login
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;