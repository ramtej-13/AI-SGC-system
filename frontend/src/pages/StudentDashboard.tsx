import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { grievanceApi } from "../services/api";
import { Grievance } from "../types";
import { StatusBadge } from "../components/StatusBadge";
import { PriorityBadge } from "../components/PriorityBadge";
import { ConfidenceMeter } from "../components/ConfidenceMeter";
import {
  Send,
  RefreshCw,
  Clock,
  ArrowUpRight
} from "lucide-react";

export const StudentDashboard: React.FC = () => {
  const [grievances, setGrievances] = useState<Grievance[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submittedGrievance, setSubmittedGrievance] = useState<Grievance | null>(null);

  const loadGrievances = async () => {
    try {
      setLoading(true);
      const data = await grievanceApi.getMyGrievances();
      setGrievances(data);
    } catch (err: any) {
      console.error("Failed to load grievances", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGrievances();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (description.trim().length < 10) {
      setError("Please enter at least 10 characters in the description.");
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      const created = await grievanceApi.submit({
        title: title.trim(),
        description: description.trim()
      });
      setSubmittedGrievance(created);
      setTitle("");
      setDescription("");
      loadGrievances();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to submit grievance. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="main-content">
      {/* Page Title & Subtitle */}
      <div>
        <h1 className="page-title">Student Grievance Portal</h1>
        <p className="page-subtitle">
          Submit a grievance and track its status.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, alignItems: "start" }}>
        {/* Left: Submission Form */}
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Submit a Grievance</h2>
              <div className="card-subtitle">
                Enter the details of your issue. You do not need to select a department.
              </div>
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

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Grievance Title</label>
              <input
                type="text"
                className="form-control"
                placeholder="e.g., Wi-Fi not working in CSE lab"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                minLength={5}
                maxLength={200}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Description</label>
              <textarea
                className="form-control"
                placeholder="Describe the problem, location, or room number..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                minLength={10}
                maxLength={2000}
                style={{ minHeight: 120 }}
                required
              />
              <div style={{ display: "flex", justifyContent: "space-between", marginTop: 4, fontSize: 11, color: "var(--color-text-light)" }}>
                <span>Minimum 10 characters</span>
                <span>{description.length} / 2000</span>
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: "100%" }}
              disabled={submitting}
            >
              <Send size={14} />
              {submitting ? "Submitting & Classifying..." : "Submit Grievance"}
            </button>
          </form>
        </div>

        {/* Right: Submission Result or Placeholder */}
        <div>
          {submittedGrievance ? (
            <div className="card" style={{ border: "1px solid #BFDBFE", backgroundColor: "#FAFDFE" }}>
              <div className="card-header">
                <div>
                  <h2 className="card-title" style={{ color: "var(--color-primary)" }}>
                    Grievance Submitted
                  </h2>
                  <div className="card-subtitle">
                    Assigned Ticket: <span className="mono-code">{submittedGrievance.ticket_number}</span>
                  </div>
                </div>
              </div>

              {/* Clean Info Rows */}
              <div style={{ marginBottom: 14 }}>
                <div className="info-row">
                  <span className="info-row-label">Category</span>
                  <span className="info-row-value">{submittedGrievance.category}</span>
                </div>
                <div className="info-row">
                  <span className="info-row-label">Assigned Department</span>
                  <span className="info-row-value">{submittedGrievance.department_name}</span>
                </div>
                <div className="info-row">
                  <span className="info-row-label">Priority</span>
                  <span className="info-row-value">
                    <PriorityBadge priority={submittedGrievance.priority} />
                  </span>
                </div>
                <div className="info-row">
                  <span className="info-row-label">Status</span>
                  <span className="info-row-value">
                    <StatusBadge status={submittedGrievance.status} />
                  </span>
                </div>
              </div>

              {submittedGrievance.prediction && (
                <div style={{ marginTop: 10, paddingTop: 10, borderTop: "1px solid var(--color-border)" }}>
                  <ConfidenceMeter
                    confidence={submittedGrievance.prediction.confidence_score}
                    isLowConfidence={submittedGrievance.is_low_confidence}
                    topPredictions={submittedGrievance.prediction.top_predictions}
                  />
                </div>
              )}

              <div style={{ marginTop: 16, display: "flex", justifyContent: "flex-end", gap: 8 }}>
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={() => setSubmittedGrievance(null)}
                >
                  Close
                </button>
                <Link
                  to={`/grievance/${submittedGrievance.id}`}
                  className="btn btn-primary btn-sm"
                >
                  View Ticket Details <ArrowUpRight size={13} />
                </Link>
              </div>
            </div>
          ) : (
            <div className="card" style={{ backgroundColor: "#FAFAFA", border: "1px dashed var(--color-border)" }}>
              <div style={{ padding: "24px 16px" }}>
                <h3 className="section-title" style={{ fontSize: 14 }}>
                  Automatic Classification
                </h3>
                <p style={{ fontSize: 13, color: "var(--color-text-muted)", lineHeight: 1.6, marginBottom: 12 }}>
                  When you submit a grievance, our AI text classification model automatically:
                </p>
                <ul style={{ paddingLeft: 20, fontSize: 13, color: "var(--color-text-muted)", lineHeight: 1.8 }}>
                  <li>Identifies the category from your title and description</li>
                  <li>Assigns the ticket to the responsible department</li>
                  <li>Sets an initial priority level based on urgency rules</li>
                  <li>Routes low-confidence complaints to administrator review</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Bottom: My Grievances History */}
      <div className="card" style={{ marginTop: 20 }}>
        <div className="card-header">
          <div>
            <h2 className="card-title" style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <Clock size={16} /> My Grievances ({grievances.length})
            </h2>
            <div className="card-subtitle">
              List of all grievances submitted by your account.
            </div>
          </div>
          <button
            onClick={loadGrievances}
            className="btn btn-secondary btn-sm"
            disabled={loading}
          >
            <RefreshCw size={12} className={loading ? "spin" : ""} /> Refresh
          </button>
        </div>

        {loading ? (
          <div style={{ textAlign: "center", padding: 30, color: "var(--color-text-muted)" }}>
            Loading grievances...
          </div>
        ) : grievances.length === 0 ? (
          <div style={{ textAlign: "center", padding: 30, color: "var(--color-text-muted)" }}>
            No grievances submitted yet. Fill out the form above to submit your first issue.
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Ticket #</th>
                  <th>Title</th>
                  <th>Category</th>
                  <th>Department</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Date</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {grievances.map((g) => (
                  <tr key={g.id}>
                    <td>
                      <span className="mono-code">{g.ticket_number}</span>
                    </td>
                    <td style={{ fontWeight: 500, maxWidth: 260 }}>
                      <Link to={`/grievance/${g.id}`} style={{ color: "var(--color-primary)" }}>
                        {g.title}
                      </Link>
                    </td>
                    <td>{g.category}</td>
                    <td>{g.department_name || g.department_code}</td>
                    <td>
                      <PriorityBadge priority={g.priority} />
                    </td>
                    <td>
                      <StatusBadge status={g.status} />
                    </td>
                    <td style={{ fontSize: 12, color: "var(--color-text-muted)" }}>
                      {new Date(g.created_at).toLocaleDateString()}
                    </td>
                    <td>
                      <Link
                        to={`/grievance/${g.id}`}
                        className="btn btn-secondary btn-sm"
                      >
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
