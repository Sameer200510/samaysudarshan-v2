// src/components/ProtectedRoute.js
import React from "react";
import { useSelector } from "react-redux";
import { Navigate, useLocation } from "react-router-dom";
import { jwtDecode } from "jwt-decode";

const isValidToken = (token) => {
  try {
    const { exp } = jwtDecode(token || "");
    return exp && Date.now() < exp * 1000;
  } catch {
    return false;
  }
};

export default function ProtectedRoute({ children, allowedRoles = ["Admin"] }) {
  const location = useLocation();

  // Support both old and new auth slice shapes
  const {
    // new shape (recommended)
    token: tokenNew,
    role: roleNew,
    isAuthChecked = true, // if your slice doesn't have this, we default to true
    // old shape (current)
    isAuthenticated: isAuthOld,
    userRole: roleOld,
  } = useSelector((s) => s.auth || {});

  const token = tokenNew || localStorage.getItem("token") || null;
  const role = roleNew || roleOld || localStorage.getItem("role") || null;

  // Wait for auth check if your slice uses it (prevents flicker)
  if (!isAuthChecked) return null;

  // 1) Must be logged in + token valid
  const loggedIn =
    (typeof isAuthOld === "boolean" ? isAuthOld : Boolean(token)) &&
    (token ? isValidToken(token) : false);

  if (!loggedIn) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  // 2) Role guard (only if allowedRoles provided)
  if (allowedRoles?.length && role && !allowedRoles.includes(role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
}