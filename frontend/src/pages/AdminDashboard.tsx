import React, { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { adminApi } from "../services/api";
import { Grievance, AnalyticsData, Department } from "../types";
import { StatusBadge } from "../components/StatusBadge";
import { PriorityBadge } from "../components/PriorityBadge";
import { AdminModelPerformance } from "./AdminModelPerformance";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from "recharts";
import {
  RefreshCw,
  Search
} from "lucide-react";

const PRIORITY_COLORS: Record<string, string> = {
  High: "#C5221F",
  Medium: "#B78103",
  Low: "#1E7E34"
};

export const AdminDashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [grievances, setGrievances] = useState<Grievance[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [deptFilter, setDeptFilter] = useState<number | undefined>(undefined);
  const [priorityFilter, setPriorityFilter] = useState("");
  const [lowConfOnly, setLowConfOnly] = useState(false);

  // Tabs: overview | grievances | model
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get("tab") || "overview";

  const handleTabChange = (tab: string) => {
    if (tab === "overview") {
      setSearchParams({});
    } else {
      setSearchParams({ tab });
    }
  };

  const loadData = async () => {
    try {
      setLoading(true);
      const [analyticsData, allGrievances, depts] = await Promise.all([
        adminApi.getAnalytics(),
        adminApi.getAllGrievances({
          status: statusFilter || undefined,
          category: categoryFilter || undefined,
          department_id: deptFilter || undefined,
          priority: priorityFilter || undefined,
          low_confidence: lowConfOnly ? true : undefined
        }),
        adminApi.getDepartments()
      ]);
      setAnalytics(analyticsData);
      setGrievances(allGrievances);
      setDepartments(depts);
    } catch (err: any) {
      console.error("Failed to load admin data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter, categoryFilter, deptFilter, priorityFilter, lowConfOnly]);

  const filteredGrievances = grievances.filter(g => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      g.ticket_number.toLowerCase().includes(q) ||
      g.title.toLowerCase().includes(q) ||
      (g.student_name && g.student_name.toLowerCase().includes(q))
    );
  });

  // Chart data
  const categoryChartData = analytics
    ? Object.entries(analytics.category_distribution).map(([name, count]) => ({
        name: name.replace(" / ", "/"),
        count
      }))
    : [];

  const priorityChartData = analytics
    ? Object.entries(analytics.priority_distribution).map(([name, count]) => ({
        name,
        value: count
      }))
    : [];

  const totalGrievances = analytics?.total_grievances || 0;
  const resolvedGrievances = analytics?.resolved_count || 0;
  const pendingGrievances = Math.max(0, totalGrievances - resolvedGrievances);
  const manualReviewCount = analytics?.low_confidence_count || 0;

  return (
    <div className="main-content">
      {/* Page Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
        <div>
          <h1 className="page-title">Admin Dashboard</h1>
          <p className="page-subtitle" style={{ marginBottom: 0 }}>
            Central management of student grievances, department queues, and AI routing.
          </p>
        </div>

        <button onClick={loadData} className="btn btn-secondary btn-sm">
          <RefreshCw size={12} className={loading ? "spin" : ""} /> Refresh
        </button>
      </div>

      {/* Compact Summary Stats: Total, Pending, Resolved, Manual Review */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-title">Total Grievances</div>
          <div className="kpi-value">{totalGrievances}</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-title">Pending</div>
          <div className="kpi-value" style={{ color: "#B78103" }}>{pendingGrievances}</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-title">Resolved</div>
          <div className="kpi-value" style={{ color: "#1E7E34" }}>{resolvedGrievances}</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-title">Manual Review</div>
          <div className="kpi-value" style={{ color: "var(--color-primary)" }}>
            <Link to="/admin/manual-review" style={{ color: "inherit", textDecoration: "underline" }}>
              {manualReviewCount}
            </Link>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div style={{ display: "flex", gap: 4, borderBottom: "1px solid var(--color-border)", marginBottom: 20 }}>
        <button
          type="button"
          onClick={() => handleTabChange("overview")}
          style={{
            padding: "8px 16px",
            border: "none",
            borderBottom: activeTab === "overview" ? "2px solid var(--color-primary)" : "2px solid transparent",
            backgroundColor: "transparent",
            color: activeTab === "overview" ? "var(--color-primary)" : "var(--color-text-muted)",
            fontWeight: activeTab === "overview" ? 600 : 400,
            fontSize: 13,
            cursor: "pointer"
          }}
        >
          Overview &amp; Analytics
        </button>

        <button
          type="button"
          onClick={() => handleTabChange("grievances")}
          style={{
            padding: "8px 16px",
            border: "none",
            borderBottom: activeTab === "grievances" ? "2px solid var(--color-primary)" : "2px solid transparent",
            backgroundColor: "transparent",
            color: activeTab === "grievances" ? "var(--color-primary)" : "var(--color-text-muted)",
            fontWeight: activeTab === "grievances" ? 600 : 400,
            fontSize: 13,
            cursor: "pointer"
          }}
        >
          Department Queues &amp; Grievances
        </button>

        <button
          type="button"
          onClick={() => handleTabChange("model")}
          style={{
            padding: "8px 16px",
            border: "none",
            borderBottom: activeTab === "model" ? "2px solid var(--color-primary)" : "2px solid transparent",
            backgroundColor: "transparent",
            color: activeTab === "model" ? "var(--color-primary)" : "var(--color-text-muted)",
            fontWeight: activeTab === "model" ? 600 : 400,
            fontSize: 13,
            cursor: "pointer"
          }}
        >
          AI Model Performance
        </button>
      </div>

      {/* Tab 3: Model Performance */}
      {activeTab === "model" && (
        <AdminModelPerformance isEmbedded={true} />
      )}

      {/* Tab 1: Overview & Analytics */}
      {activeTab === "overview" && (
        <div style={{ display: "grid", gridTemplateColumns: "1.3fr 1fr", gap: 20, marginBottom: 24 }}>
          {/* Category Breakdown Bar Chart */}
          <div className="card" style={{ marginBottom: 0 }}>
            <div className="card-header">
              <h2 className="card-title">Grievances by Category</h2>
            </div>
            <div style={{ width: "100%", height: 260 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoryChartData} margin={{ top: 10, right: 20, left: -15, bottom: 45 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#EEF1F4" />
                  <XAxis dataKey="name" angle={-30} textAnchor="end" interval={0} tick={{ fontSize: 11 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="var(--color-primary)" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Priority Distribution Pie Chart */}
          <div className="card" style={{ marginBottom: 0 }}>
            <div className="card-header">
              <h2 className="card-title">Priority Distribution</h2>
            </div>
            <div style={{ width: "100%", height: 260, display: "flex", alignItems: "center" }}>
              <ResponsiveContainer width="60%" height="100%">
                <PieChart>
                  <Pie
                    data={priorityChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={75}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {priorityChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={PRIORITY_COLORS[entry.name] || "#1F4E79"} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>

              <div style={{ width: "40%", paddingLeft: 10 }}>
                {priorityChartData.map((item) => (
                  <div key={item.name} style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8, fontSize: 13 }}>
                    <span
                      style={{
                        width: 10,
                        height: 10,
                        borderRadius: "50%",
                        backgroundColor: PRIORITY_COLORS[item.name] || "#666666"
                      }}
                    />
                    <span>{item.name}:</span>
                    <strong style={{ fontFamily: "var(--font-mono)" }}>{item.value}</strong>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2 (and lower section of overview): Department Queues & Grievances */}
      {activeTab !== "model" && (
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">All Grievances ({filteredGrievances.length})</h2>
              <div className="card-subtitle">
                Filter and inspect grievances across all campus departments.
              </div>
            </div>
          </div>

          {/* Filters */}
          <div className="filter-row">
            <div style={{ flex: "1 1 200px", position: "relative" }}>
              <Search size={14} style={{ position: "absolute", left: 10, top: 9, color: "var(--color-text-light)" }} />
              <input
                type="text"
                className="form-control"
                placeholder="Search ticket #, title, or student..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{ paddingLeft: 30 }}
              />
            </div>

            <select
              className="form-control"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              style={{ width: 130 }}
            >
              <option value="">All Statuses</option>
              <option value="Submitted">Submitted</option>
              <option value="Assigned">Assigned</option>
              <option value="In Progress">In Progress</option>
              <option value="Resolved">Resolved</option>
              <option value="Closed">Closed</option>
            </select>

            <select
              className="form-control"
              value={deptFilter || ""}
              onChange={(e) => setDeptFilter(e.target.value ? Number(e.target.value) : undefined)}
              style={{ width: 160 }}
            >
              <option value="">All Departments</option>
              {departments.map((d) => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </select>

            <select
              className="form-control"
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              style={{ width: 120 }}
            >
              <option value="">All Priorities</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>

            <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, cursor: "pointer" }}>
              <input
                type="checkbox"
                checked={lowConfOnly}
                onChange={(e) => setLowConfOnly(e.target.checked)}
              />
              <span>Low Confidence</span>
            </label>
          </div>

          {/* Grievances Table */}
          {loading ? (
            <div style={{ textAlign: "center", padding: 30, color: "var(--color-text-muted)" }}>
              Loading grievances...
            </div>
          ) : filteredGrievances.length === 0 ? (
            <div style={{ textAlign: "center", padding: 30, color: "var(--color-text-muted)" }}>
              No grievances found matching the filters.
            </div>
          ) : (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Ticket #</th>
                    <th>Title</th>
                    <th>Student</th>
                    <th>Category</th>
                    <th>Department</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Confidence</th>
                    <th>Date</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredGrievances.map((g) => (
                    <tr key={g.id}>
                      <td>
                        <span className="mono-code">{g.ticket_number}</span>
                      </td>
                      <td style={{ fontWeight: 500, maxWidth: 220 }}>
                        <Link to={`/grievance/${g.id}`} style={{ color: "var(--color-primary)" }}>
                          {g.title}
                        </Link>
                      </td>
                      <td>{g.student_name}</td>
                      <td>{g.category}</td>
                      <td>{g.department_name || g.department_code}</td>
                      <td>
                        <PriorityBadge priority={g.priority} />
                      </td>
                      <td>
                        <StatusBadge status={g.status} />
                      </td>
                      <td>
                        {g.is_low_confidence ? (
                          <span className="badge" style={{ backgroundColor: "var(--color-warning-bg)", color: "var(--color-warning)", border: "1px solid #FDE68A" }}>
                            Low ({Math.round((g.prediction?.confidence_score || 0) * 100)}%)
                          </span>
                        ) : (
                          <span style={{ fontFamily: "var(--font-mono)", fontSize: 12 }}>
                            {Math.round((g.prediction?.confidence_score || 0) * 100)}%
                          </span>
                        )}
                      </td>
                      <td style={{ fontSize: 12, color: "var(--color-text-muted)" }}>
                        {new Date(g.created_at).toLocaleDateString()}
                      </td>
                      <td>
                        <Link to={`/grievance/${g.id}`} className="btn btn-secondary btn-sm">
                          Inspect
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
