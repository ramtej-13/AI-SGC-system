import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { grievanceApi, departmentApi } from "../services/api";
import { Grievance } from "../types";
import { useAuth } from "../context/AuthContext";
import { StatusBadge } from "../components/StatusBadge";
import { PriorityBadge } from "../components/PriorityBadge";
import { ConfidenceMeter } from "../components/ConfidenceMeter";
import {
  ArrowLeft
} from "lucide-react";

export const GrievanceDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [grievance, setGrievance] = useState<Grievance | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Status update state for Administrator
  const [newStatus, setNewStatus] = useState("In Progress");
  const [remarks, setRemarks] = useState("");
  const [updating, setUpdating] = useState(false);
  const [updateSuccess, setUpdateSuccess] = useState(false);

  const fetchGrievance = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const data = await grievanceApi.getById(Number(id));
      setGrievance(data);
      setNewStatus(data.status === "Submitted" ? "In Progress" : data.status);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load grievance details");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGrievance();
  }, [id]);

  const handleStatusUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!grievance) return;
    try {
      setUpdating(true);
      const updated = await departmentApi.updateStatus(grievance.id, {
        status: newStatus,
        remarks: remarks.trim()
      });
      setGrievance(updated);
      setRemarks("");
      setUpdateSuccess(true);
      setTimeout(() => setUpdateSuccess(false), 4000);
    } catch (err: any) {
      alert("Error updating status: " + (err.response?.data?.detail || err.message));
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="main-content" style={{ textAlign: "center", padding: 60, color: "var(--color-text-muted)" }}>
        Loading grievance details...
      </div>
    );
  }

  if (error || !grievance) {
    return (
      <div className="main-content">
        <div className="card" style={{ textAlign: "center", padding: 30 }}>
          <p style={{ color: "var(--color-danger)", marginBottom: 14 }}>{error || "Grievance not found"}</p>
          <button onClick={() => navigate(-1)} className="btn btn-secondary btn-sm">
            <ArrowLeft size={14} /> Go Back
          </button>
        </div>
      </div>
    );
  }

  const canUpdate = user && user.role === "admin";

  return (
    <div className="main-content">
      {/* Back button */}
      <div style={{ marginBottom: 16 }}>
        <button
          onClick={() => navigate(-1)}
          className="btn btn-secondary btn-sm"
        >
          <ArrowLeft size={13} /> Back to Dashboard
        </button>
      </div>

      {/* Main Ticket Summary Card */}
      <div className="card">
        <div className="card-header" style={{ alignItems: "flex-start" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
              <span className="mono-code" style={{ fontSize: 13, fontWeight: 700 }}>
                {grievance.ticket_number}
              </span>
              <StatusBadge status={grievance.status} />
              <PriorityBadge priority={grievance.priority} />
            </div>
            <h1 className="page-title" style={{ fontSize: 18, marginBottom: 0 }}>
              {grievance.title}
            </h1>
          </div>

          <div style={{ textAlign: "right", fontSize: 12, color: "var(--color-text-muted)" }}>
            <div>Lodged: {new Date(grievance.created_at).toLocaleDateString()}</div>
            <div>Updated: {new Date(grievance.updated_at).toLocaleDateString()}</div>
          </div>
        </div>

        {/* Info Rows */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 16 }}>
          <div>
            <div className="info-row">
              <span className="info-row-label">Student</span>
              <span className="info-row-value">{grievance.student_name} ({grievance.student_email})</span>
            </div>
            <div className="info-row">
              <span className="info-row-label">Category</span>
              <span className="info-row-value">{grievance.category}</span>
            </div>
          </div>
          <div>
            <div className="info-row">
              <span className="info-row-label">Assigned Department</span>
              <span className="info-row-value">{grievance.department_name} ({grievance.department_code})</span>
            </div>
            <div className="info-row">
              <span className="info-row-label">Priority Rationale</span>
              <span className="info-row-value">{grievance.priority_reason || "Standard priority rules"}</span>
            </div>
          </div>
        </div>

        {/* Description */}
        <div style={{ marginTop: 12 }}>
          <div style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", color: "var(--color-text-muted)", marginBottom: 6 }}>
            Description
          </div>
          <div
            style={{
              background: "#F8F9FA",
              border: "1px solid var(--color-border)",
              borderRadius: "var(--radius-md)",
              padding: "12px 14px",
              fontSize: 13,
              lineHeight: 1.6,
              whiteSpace: "pre-wrap"
            }}
          >
            {grievance.description}
          </div>
        </div>

        {/* Resolution remarks if exists */}
        {grievance.resolution_remarks && (
          <div
            style={{
              backgroundColor: "var(--color-success-bg)",
              border: "1px solid #A7F3D0",
              borderRadius: "var(--radius-md)",
              padding: "12px 14px",
              marginTop: 14
            }}
          >
            <div style={{ fontSize: 12, fontWeight: 600, color: "var(--color-success)" }}>
              Resolution Remarks:
            </div>
            <div style={{ fontSize: 13, color: "#065F46", marginTop: 4 }}>
              {grievance.resolution_remarks}
            </div>
          </div>
        )}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, alignItems: "start" }}>
        {/* Left Column: AI Model Prediction & Explainability */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">AI Classification Details</h2>
          </div>

          {grievance.prediction ? (
            <div>
              <div className="info-row">
                <span className="info-row-label">Inference Time</span>
                <span className="info-row-value">
                  {grievance.prediction.inference_time_ms ? `${grievance.prediction.inference_time_ms.toFixed(1)} ms` : "N/A"}
                </span>
              </div>
              <div className="info-row">
                <span className="info-row-label">Predicted Category</span>
                <span className="info-row-value">
                  {grievance.prediction.raw_predicted_category || grievance.prediction.predicted_category}
                </span>
              </div>

              <div style={{ marginTop: 12 }}>
                <ConfidenceMeter
                  confidence={grievance.prediction.raw_confidence || grievance.prediction.confidence_score}
                  isLowConfidence={grievance.is_low_confidence}
                  topPredictions={grievance.prediction.top_predictions}
                />
              </div>
            </div>
          ) : (
            <div style={{ color: "var(--color-text-muted)", fontSize: 13 }}>
              No prediction metadata recorded.
            </div>
          )}
        </div>

        {/* Right Column: Update Status (Admin only) & Audit Trail */}
        <div>
          {canUpdate && (
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Update Status</h3>
              </div>

              {updateSuccess && (
                <div style={{ background: "var(--color-success-bg)", color: "var(--color-success)", padding: "8px 12px", borderRadius: "var(--radius-sm)", fontSize: 12, marginBottom: 12 }}>
                  Status successfully updated.
                </div>
              )}

              <form onSubmit={handleStatusUpdate}>
                <div className="form-group">
                  <label className="form-label">New Status</label>
                  <select
                    className="form-control"
                    value={newStatus}
                    onChange={(e) => setNewStatus(e.target.value)}
                  >
                    <option value="Assigned">Assigned</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Resolved">Resolved</option>
                    <option value="Closed">Closed</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Remarks</label>
                  <textarea
                    className="form-control"
                    placeholder="Provide resolution details or update rationale..."
                    value={remarks}
                    onChange={(e) => setRemarks(e.target.value)}
                    style={{ minHeight: 70 }}
                    required
                  />
                </div>

                <button
                  type="submit"
                  className="btn btn-primary btn-sm"
                  style={{ width: "100%" }}
                  disabled={updating}
                >
                  {updating ? "Saving..." : "Update Status"}
                </button>
              </form>
            </div>
          )}

          {/* Timeline */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">
                Status History ({grievance.history?.length || 0})
              </h3>
            </div>

            {grievance.history && grievance.history.length > 0 ? (
              <div className="timeline">
                {grievance.history.map((h, i) => (
                  <div key={h.id || i} className="timeline-item">
                    <div className="timeline-dot" />
                    <div className="timeline-header">
                      <div className="timeline-status">
                        {h.previous_status ? (
                          <span>{h.previous_status} &rarr; <strong>{h.new_status}</strong></span>
                        ) : (
                          <span>Initial: <strong>{h.new_status}</strong></span>
                        )}
                      </div>
                      <span className="timeline-date">
                        {new Date(h.created_at).toLocaleString()}
                      </span>
                    </div>

                    <div style={{ fontSize: 11, color: "var(--color-primary)", fontWeight: 500, marginTop: 2 }}>
                      By: {h.changed_by_name || "System"}
                    </div>

                    {h.remarks && (
                      <div className="timeline-remarks">
                        {h.remarks}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ color: "var(--color-text-muted)", fontSize: 13 }}>
                No history entries recorded yet.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
