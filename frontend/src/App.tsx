import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { Navbar } from "./components/Navbar";
import { LoginPage } from "./pages/LoginPage";
import { StudentDashboard } from "./pages/StudentDashboard";
import { GrievanceDetailPage } from "./pages/GrievanceDetailPage";
import { AdminDashboard } from "./pages/AdminDashboard";
import { AdminModelPerformance } from "./pages/AdminModelPerformance";
import { AdminManualReview } from "./pages/AdminManualReview";

// Protected Route Component
const ProtectedRoute: React.FC<{
  children: React.ReactNode;
  allowedRoles?: string[];
}> = ({ children, allowedRoles }) => {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div style={{ textAlign: "center", padding: 80, color: "var(--color-text-muted)" }}>
        Loading session...
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    if (user.role === "student") return <Navigate to="/student" replace />;
    if (user.role === "admin") return <Navigate to="/admin" replace />;
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Root Router Redirector
const RootRedirect: React.FC = () => {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div style={{ textAlign: "center", padding: 80, color: "var(--color-text-muted)" }}>
        Loading session...
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  if (user.role === "student") return <Navigate to="/student" replace />;
  if (user.role === "admin") return <Navigate to="/admin" replace />;

  return <Navigate to="/login" replace />;
};

export const App: React.FC = () => {
  return (
    <Router>
      <AuthProvider>
        <div className="app-container">
          <Navbar />
          <Routes>
            <Route path="/login" element={<LoginPage />} />

            <Route
              path="/student"
              element={
                <ProtectedRoute allowedRoles={["student"]}>
                  <StudentDashboard />
                </ProtectedRoute>
              }
            />

            <Route
              path="/grievance/:id"
              element={
                <ProtectedRoute>
                  <GrievanceDetailPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/admin"
              element={
                <ProtectedRoute allowedRoles={["admin"]}>
                  <AdminDashboard />
                </ProtectedRoute>
              }
            />

            <Route
              path="/admin/model-performance"
              element={
                <ProtectedRoute allowedRoles={["admin"]}>
                  <AdminModelPerformance />
                </ProtectedRoute>
              }
            />

            <Route
              path="/admin/manual-review"
              element={
                <ProtectedRoute allowedRoles={["admin"]}>
                  <AdminManualReview />
                </ProtectedRoute>
              }
            />

            <Route path="/" element={<RootRedirect />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </AuthProvider>
    </Router>
  );
};

export default App;