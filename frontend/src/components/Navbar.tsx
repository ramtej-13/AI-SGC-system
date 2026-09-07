import React from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ShieldCheck, LogOut } from "lucide-react";

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav
      style={{
        backgroundColor: "var(--color-primary)",
        color: "#FFFFFF",
        borderBottom: "1px solid rgba(255, 255, 255, 0.1)"
      }}
    >
      <div
        style={{
          maxWidth: 1200,
          margin: "0 auto",
          padding: "0 20px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          height: 56
        }}
      >
        {/* Brand */}
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <ShieldCheck size={22} color="#93C5FD" />
          <Link
            to="/"
            style={{
              color: "#FFFFFF",
              textDecoration: "none",
              display: "flex",
              flexDirection: "column"
            }}
          >
            <span style={{ fontSize: 16, fontWeight: 700, letterSpacing: "-0.01em", lineHeight: 1.2 }}>
              AI-SGC System
            </span>
            <span style={{ fontSize: 11, color: "#BFDBFE", fontWeight: 400 }}>
              Student Grievance Classification &amp; Smart Routing
            </span>
          </Link>
        </div>

        {/* Navigation Links for Student and Admin */}
        {user && (
          <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
            {user.role === "student" && (
              <Link
                to="/student"
                style={{
                  color: isActive("/student") ? "#FFFFFF" : "#E2E8F0",
                  backgroundColor: isActive("/student") ? "rgba(255, 255, 255, 0.15)" : "transparent",
                  padding: "5px 12px",
                  borderRadius: 4,
                  fontSize: 13,
                  fontWeight: 500
                }}
              >
                Dashboard
              </Link>
            )}

            {user.role === "admin" && (
              <>
                <Link
                  to="/admin"
                  style={{
                    color: location.pathname === "/admin" && !location.search.includes("tab=") ? "#FFFFFF" : "#E2E8F0",
                    backgroundColor: location.pathname === "/admin" && !location.search.includes("tab=") ? "rgba(255, 255, 255, 0.15)" : "transparent",
                    padding: "5px 12px",
                    borderRadius: 4,
                    fontSize: 13,
                    fontWeight: 500
                  }}
                >
                  Dashboard
                </Link>
                <Link
                  to="/admin?tab=grievances"
                  style={{
                    color: location.pathname === "/admin" && location.search.includes("tab=grievances") ? "#FFFFFF" : "#E2E8F0",
                    backgroundColor: location.pathname === "/admin" && location.search.includes("tab=grievances") ? "rgba(255, 255, 255, 0.15)" : "transparent",
                    padding: "5px 12px",
                    borderRadius: 4,
                    fontSize: 13,
                    fontWeight: 500
                  }}
                >
                  Grievances
                </Link>
                <Link
                  to="/admin/manual-review"
                  style={{
                    color: isActive("/admin/manual-review") ? "#FFFFFF" : "#E2E8F0",
                    backgroundColor: isActive("/admin/manual-review") ? "rgba(255, 255, 255, 0.15)" : "transparent",
                    padding: "5px 12px",
                    borderRadius: 4,
                    fontSize: 13,
                    fontWeight: 500
                  }}
                >
                  Manual Review
                </Link>
                <Link
                  to="/admin/model-performance"
                  style={{
                    color: isActive("/admin/model-performance") || (location.pathname === "/admin" && location.search.includes("tab=model")) ? "#FFFFFF" : "#E2E8F0",
                    backgroundColor: isActive("/admin/model-performance") || (location.pathname === "/admin" && location.search.includes("tab=model")) ? "rgba(255, 255, 255, 0.15)" : "transparent",
                    padding: "5px 12px",
                    borderRadius: 4,
                    fontSize: 13,
                    fontWeight: 500
                  }}
                >
                  AI Model Performance
                </Link>
              </>
            )}
          </div>
        )}

        {/* User Account / Logout */}
        {user ? (
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: "#FFFFFF" }}>
                {user.role === "admin" ? "Administrator" : user.full_name}
              </div>
              <div style={{ fontSize: 11, color: "#BFDBFE" }}>
                {user.role === "admin" ? "Admin Role" : "Student"}
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="btn btn-secondary btn-sm"
              style={{
                backgroundColor: "rgba(255, 255, 255, 0.12)",
                borderColor: "rgba(255, 255, 255, 0.25)",
                color: "#FFFFFF"
              }}
            >
              <LogOut size={13} /> Logout
            </button>
          </div>
        ) : (
          <Link
            to="/login"
            className="btn btn-secondary btn-sm"
            style={{ color: "#FFFFFF", backgroundColor: "rgba(255, 255, 255, 0.15)", borderColor: "rgba(255, 255, 255, 0.25)" }}
          >
            Sign In
          </Link>
        )}
      </div>
    </nav>
  );
};