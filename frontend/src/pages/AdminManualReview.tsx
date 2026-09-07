import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { adminApi } from "../services/api";
import { Grievance, Department } from "../types";
import { PriorityBadge } from "../components/PriorityBadge";
import {
  RefreshCw,
  X
} from "lucide-react";

export const AdminManualReview: React.FC = () => {
  const [queue, setQueue] = useState<Grievance[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);

  // Review modal state
  const [selectedTicket, setSelectedTicket] = useState<Grievance | null>(null);
  const [assignedCategory, setAssignedCategory] = useState("IT / Network");
  const [assignedDeptId, setAssignedDeptId] = useState<number | undefined>(undefined);
  const [reviewNotes, setReviewNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const categories = [
    "IT / Network",
    "Electrical",
    "Plumbing",
    "Cleaning / Housekeeping",
    "Laboratory",
    "Infrastructure / Maintenance",
    "Academic",
    "Hostel / Canteen",
    "Other / Manual Review"
  ];

  const loadQueue = async () => {
    try {
      setLoading(true);
      const [queueData, depts] = await Promise.all([
        adminApi.getLowConfidenceQueue(),
        adminApi.getDepartments()
      ]);
      setQueue(queueData);
      setDepartments(depts);
    } catch (err: any) {
      console.error("Failed to load manual review queue", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQueue();
  }, []);

  const handleOpenReview = (g: Grievance) => {
    setSelectedTicket(g);
    const initialCat = g.prediction?.raw_predicted_category || "IT / Network";
    setAssignedCategory(initialCat);
    setReviewNotes("");

    const matchedDept = departments.find(d => d.name.toLowerCase().includes(initialCat.split(" ")[0].toLowerCase()));
    setAssignedDeptId(matchedDept ? matchedDept.id : departments[0]?.id);
  };

  const handleCategoryChange = (cat: string) => {
    setAssignedCategory(cat);
    const deptPrefix = cat.split(" ")[0].toLowerCase();
    const matched = departments.find(d => d.name.toLowerCase().includes(deptPrefix));
    if (matched) {
      setAssignedDeptId(matched.id);
    }
  };

  const handleConfirmReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTicket) return;
    try {
      setSubmitting(true);
      await adminApi.resolveManualReview(selectedTicket.id, {
        assigned_category: assignedCategory,
        assigned_department_id: assignedDeptId,
        review_notes: reviewNotes.trim() || undefined
      });
      setSuccessMsg(`Ticket ${selectedTicket.ticket_number} successfully reviewed and routed.`);
      setSelectedTicket(null);
      loadQueue();
      setTimeout(() => setSuccessMsg(null), 5000);
    } catch (err: any) {
      alert("Manual review failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="main-content">
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
        <div>
          <h1 className="page-title">Manual Review</h1>
          <p className="page-subtitle" style={{ marginBottom: 0 }}>
            Grievances with low AI confidence are listed here for administrator review.
          </p>
        </div>

        <button onClick={loadQueue} className="btn btn-secondary btn-sm">
          <RefreshCw size={12} className={loading ? "spin" : ""} /> Refresh
        </button>
      </div>

      {successMsg && (
        <div style={{ backgroundColor: "var(--color-success-bg)", border: "1px solid #A7F3D0", color: "var(--color-success)", padding: "8px 12px", borderRadius: "var(--radius-md)", fontSize: 13, marginBottom: 16 }}>
          {successMsg}
        </div>
      )}

      {/* Queue Card */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            Pending Review Queue ({queue.length})
          </h2>
        </div>

        {loading ? (
          <div style={{ textAlign: "center", padding: 30, color: "var(--color-text-muted)" }}>
            Loading pending grievances...
          </div>
        ) : queue.length === 0 ? (
          <div style={{ textAlign: "center", padding: 40, color: "var(--color-text-muted)" }}>
            No low-confidence grievances pending review.
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Ticket #</th>
                  <th>Title</th>
                  <th>Student</th>
                  <th>Predicted Category</th>
                  <th>Confidence</th>
                  <th>Priority</th>
                  <th>Date</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {queue.map((g) => (
                  <tr key={g.id}>
                    <td>
                      <span className="mono-code">{g.ticket_number}</span>
                    </td>
                    <td style={{ fontWeight: 500, maxWidth: 260 }}>
                      <Link to={`/grievance/${g.id}`} style={{ color: "var(--color-primary)" }}>
                        {g.title}
                      </Link>
                    </td>
                    <td>{g.student_name}</td>
                    <td>{g.prediction?.raw_predicted_category || "Uncertain"}</td>
                    <td>
                      <span className="badge" style={{ backgroundColor: "var(--color-warning-bg)", color: "var(--color-warning)", border: "1px solid #FDE68A" }}>
                        {Math.round((g.prediction?.raw_confidence || 0) * 100)}% (&lt; 70%)
                      </span>
                    </td>
                    <td>
                      <PriorityBadge priority={g.priority} />
                    </td>
                    <td style={{ fontSize: 12, color: "var(--color-text-muted)" }}>
                      {new Date(g.created_at).toLocaleDateString()}
                    </td>
                    <td>
                      <button
                        onClick={() => handleOpenReview(g)}
                        className="btn btn-primary btn-sm"
                      >
                        Review
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Review Modal */}
      {selectedTicket && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
              <div>
                <span className="mono-code">{selectedTicket.ticket_number}</span>
                <h3 className="section-title" style={{ marginTop: 4, marginBottom: 0 }}>
                  Manual Review
                </h3>
              </div>
              <button
                onClick={() => setSelectedTicket(null)}
                style={{ background: "none", border: "none", cursor: "pointer", color: "var(--color-text-muted)" }}
              >
                <X size={18} />
              </button>
            </div>

            {/* Student Description */}
            <div style={{ background: "#F8F9FA", padding: 12, borderRadius: "var(--radius-md)", border: "1px solid var(--color-border)", marginBottom: 14 }}>
              <div style={{ fontSize: 11, fontWeight: 600, color: "var(--color-text-muted)", textTransform: "uppercase" }}>
                Student Description:
              </div>
              <div style={{ fontSize: 13, marginTop: 4, whiteSpace: "pre-wrap" }}>
                {selectedTicket.description}
              </div>
            </div>

            <form onSubmit={handleConfirmReview}>
              <div className="form-group">
                <label className="form-label">Category</label>
                <select
                  className="form-control"
                  value={assignedCategory}
                  onChange={(e) => handleCategoryChange(e.target.value)}
                  required
                >
                  {categories.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Department</label>
                <select
                  className="form-control"
                  value={assignedDeptId}
                  onChange={(e) => setAssignedDeptId(Number(e.target.value))}
                  required
                >
                  {departments.map((d) => (
                    <option key={d.id} value={d.id}>{d.name} ({d.code})</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Remarks</label>
                <textarea
                  className="form-control"
                  placeholder="Enter administrator notes or review rationale..."
                  value={reviewNotes}
                  onChange={(e) => setReviewNotes(e.target.value)}
                  style={{ minHeight: 70 }}
                  required
                />
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 16 }}>
                <button
                  type="button"
                  onClick={() => setSelectedTicket(null)}
                  className="btn btn-secondary btn-sm"
                  disabled={submitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary btn-sm"
                  disabled={submitting}
                >
                  {submitting ? "Saving..." : "Confirm Review"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
