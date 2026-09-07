import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ShieldCheck, ArrowRight } from "lucide-react";

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState("student@college.local");
  const [password, setPassword] = useState("Student@123");
  const [selectedRole, setSelectedRole] = useState<"student" | "admin">("student");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleRoleSelect = (role: "student" | "admin") => {
    setSelectedRole(role);
    setError(null);
    if (role === "student") {
      setEmail("student@college.local");
      setPassword("Student@123");
    } else {
      setEmail("admin@college.local");
      setPassword("Admin@123");
    }
  };

  const handleLogin = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!email || !password) {
      setError("Please enter both email and password.");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const user = await login(email, password);
      if (user.role === "student") {
        navigate("/student");
      } else if (user.role === "admin") {
        navigate("/admin");
      } else {
        navigate("/");
      }
    } catch (err: any) {
      if (!err.response) {
        setError("Cannot connect to backend server. Please ensure backend is running or check your connection.");
      } else {
        setError(err.response?.data?.detail || "Invalid email or password. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "calc(100vh - 56px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "30px 20px"
      }}
    >
      <div style={{ maxWidth: 420, width: "100%" }}>
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 20 }}>
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              width: 48,
              height: 48,
              borderRadius: "4px",
              backgroundColor: "var(--color-primary-light)",
              color: "var(--color-primary)",
              marginBottom: 10
            }}
          >
            <ShieldCheck size={28} />
          </div>
          <h1 className="page-title" style={{ fontSize: 22 }}>
            Student Grievance System
          </h1>
          <p className="page-subtitle" style={{ marginBottom: 0 }}>
            AI-based grievance classification and automatic department routing
          </p>
        </div>

        {/* Role Selector Tabs */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 8,
            marginBottom: 16
          }}
        >
          <button
            type="button"
            onClick={() => handleRoleSelect("student")}
            style={{
              padding: "10px",
              borderRadius: "var(--radius-md)",
              border: selectedRole === "student" ? "2px solid var(--color-primary)" : "1px solid var(--color-border)",
              backgroundColor: selectedRole === "student" ? "#FFFFFF" : "#F3F4F6",
              color: selectedRole === "student" ? "var(--color-primary)" : "var(--color-text-muted)",
              fontWeight: 600,
              fontSize: 13,
              cursor: "pointer"
            }}
          >
            Student Login
          </button>

          <button
            type="button"
            onClick={() => handleRoleSelect("admin")}
            style={{
              padding: "10px",
              borderRadius: "var(--radius-md)",
              border: selectedRole === "admin" ? "2px solid var(--color-primary)" : "1px solid var(--color-border)",
              backgroundColor: selectedRole === "admin" ? "#FFFFFF" : "#F3F4F6",
              color: selectedRole === "admin" ? "var(--color-primary)" : "var(--color-text-muted)",
              fontWeight: 600,
              fontSize: 13,
              cursor: "pointer"
            }}
          >
            Admin Login
          </button>
        </div>

        {/* Login Card */}
        <div className="card" style={{ padding: 22 }}>
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 14, fontWeight: 600, color: "var(--color-text)" }}>
              {selectedRole === "student" ? "Student Portal Sign In" : "Admin Portal Sign In"}
            </div>
            <div style={{ fontSize: 12, color: "var(--color-text-muted)", marginTop: 2 }}>
              {selectedRole === "student"
                ? "Submit complaints and track resolution status."
                : "Manage departmental queues and oversee routing."}
            </div>
          </div>

          {error && (
            <div
              style={{
                backgroundColor: "var(--color-danger-bg)",
                border: "1px solid #FECACA",
                color: "var(--color-danger)",
                padding: "8px 12px",
                borderRadius: "var(--radius-md)",
                fontSize: 13,
                marginBottom: 14
              }}
            >
              {error}
            </div>
          )}

          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label className="form-label">Email Address</label>
              <input
                type="text"
                className="form-control"
                placeholder={selectedRole === "student" ? "student@college.local" : "admin@college.local"}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Password</label>
              <input
                type="password"
                className="form-control"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: "100%", marginTop: 6 }}
              disabled={loading}
            >
              {loading ? "Signing In..." : `Sign In as ${selectedRole === "student" ? "Student" : "Admin"}`}
              <ArrowRight size={15} />
            </button>
          </form>

          {/* Quick Demo Credentials */}
          <div style={{ marginTop: 18, paddingTop: 14, borderTop: "1px solid var(--color-border)" }}>
            <div style={{ fontSize: 11, fontWeight: 600, textTransform: "uppercase", color: "var(--color-text-muted)", letterSpacing: "0.04em", marginBottom: 8 }}>
              Quick Demo Accounts:
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => handleRoleSelect("student")}
                style={{ fontSize: 11, justifyContent: "center" }}
              >
                student@college.local
              </button>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => handleRoleSelect("admin")}
                style={{ fontSize: 11, justifyContent: "center" }}
              >
                admin@college.local
              </button>
            </div>
          </div>
        </div>

        <div style={{ textAlign: "center", fontSize: 12, color: "var(--color-text-light)", marginTop: 12 }}>
          College Project Demonstration
        </div>
      </div>
    </div>
  );
};