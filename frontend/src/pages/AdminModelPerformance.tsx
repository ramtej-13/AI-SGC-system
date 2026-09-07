import React, { useState, useEffect } from "react";
import { adminApi } from "../services/api";
import { ModelPerformanceData, GeneralizationTestResult } from "../types";
import { ConfidenceMeter } from "../components/ConfidenceMeter";
import { PriorityBadge } from "../components/PriorityBadge";
import {
  RefreshCw,
  Play
} from "lucide-react";

interface AdminModelPerformanceProps {
  isEmbedded?: boolean;
}

export const AdminModelPerformance: React.FC<AdminModelPerformanceProps> = ({ isEmbedded = false }) => {
  const [data, setData] = useState<ModelPerformanceData | null>(null);
  const [loading, setLoading] = useState(true);

  // Live Tester State
  const [testText, setTestText] = useState("");
  const [threshold, setThreshold] = useState(0.70);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<GeneralizationTestResult | null>(null);

  const loadMetadata = async () => {
    try {
      setLoading(true);
      const res = await adminApi.getModelPerformance();
      setData(res);
    } catch (err: any) {
      console.error("Failed to load model performance metadata", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMetadata();
  }, []);

  const handleRunTest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!testText.trim()) return;
    try {
      setTesting(true);
      const res = await adminApi.testModel({
        text: testText.trim(),
        threshold: threshold
      });
      setTestResult(res);
    } catch (err: any) {
      alert("Test failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setTesting(false);
    }
  };

  const sampleInputs = [
    "The Ethernet cable is unplugged in CS lab and Wi-Fi cannot connect.",
    "Ceiling fan in room 204 is throwing electrical sparks and burning smell.",
    "Major water leak from ceiling pipe in 3rd floor washroom.",
    "Restrooms on ground floor are extremely dirty without liquid soap.",
    "Digital oscilloscope in electronics lab showing Err-04 calibration failure.",
    "Ceiling plaster fell down during lecture and bench has an exposed sharp nail.",
    "Internal assessment marks for data structures were recorded wrongly.",
    "Dead insect found in dinner curry served in hostel mess hall.",
    "Can someone please help me find my missing umbrella?"
  ];

  return (
    <div className={isEmbedded ? "" : "main-content"}>
      {/* Header */}
      {!isEmbedded ? (
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
          <div>
            <h1 className="page-title">AI Model Performance</h1>
            <p className="page-subtitle" style={{ marginBottom: 0 }}>
              Evaluation metrics for the TF-IDF + Logistic Regression classification pipeline.
            </p>
          </div>

          <button onClick={loadMetadata} className="btn btn-secondary btn-sm">
            <RefreshCw size={12} className={loading ? "spin" : ""} /> Refresh
          </button>
        </div>
      ) : (
        <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 14 }}>
          <button onClick={loadMetadata} className="btn btn-secondary btn-sm">
            <RefreshCw size={12} className={loading ? "spin" : ""} /> Refresh
          </button>
        </div>
      )}

      {/* Primary Metrics Grid */}
      {data && (
        <>
          <div className="kpi-grid">
            <div className="kpi-card">
              <div className="kpi-title">Accuracy</div>
              <div className="kpi-value">{(data.evaluation_metrics.accuracy * 100).toFixed(1)}%</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-title">Macro F1</div>
              <div className="kpi-value" style={{ color: "#1E7E34" }}>{data.evaluation_metrics.macro_f1.toFixed(3)}</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-title">Weighted F1</div>
              <div className="kpi-value" style={{ color: "var(--color-primary)" }}>{data.evaluation_metrics.weighted_f1.toFixed(3)}</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-title">Vocabulary Size</div>
              <div className="kpi-value">{data.vocabulary_size}</div>
            </div>
          </div>

          <div className="simple-panel" style={{ fontSize: 13, marginBottom: 20 }}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 10 }}>
              <div>
                <span style={{ color: "var(--color-text-muted)" }}>Model:</span>{" "}
                <strong>{data.selected_model}</strong>
              </div>
              <div>
                <span style={{ color: "var(--color-text-muted)" }}>Data Split:</span>{" "}
                <strong>{data.train_samples} Train / {data.test_samples} Test (80/20 Stratified)</strong>
              </div>
              <div>
                <span style={{ color: "var(--color-text-muted)" }}>Total Dataset Samples:</span>{" "}
                <strong>{data.total_samples}</strong>
              </div>
              <div>
                <span style={{ color: "var(--color-text-muted)" }}>Confidence Threshold:</span>{" "}
                <strong>{Math.round(data.default_confidence_threshold * 100)}% (Fallback to Review)</strong>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Test a New Grievance Section */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">Test a New Grievance</h2>
            <div className="card-subtitle">
              Enter any sentence to observe real-time classification, confidence score, and department routing.
            </div>
          </div>
        </div>

        <form onSubmit={handleRunTest}>
          <div className="form-group">
            <label className="form-label">Input Text</label>
            <textarea
              className="form-control"
              placeholder="Type or paste a sample grievance..."
              value={testText}
              onChange={(e) => setTestText(e.target.value)}
              style={{ minHeight: 70 }}
              required
            />
          </div>

          {/* Quick preset samples */}
          <div style={{ marginBottom: 12 }}>
            <span style={{ fontSize: 11, fontWeight: 600, color: "var(--color-text-muted)", textTransform: "uppercase" }}>
              Sample Inputs:
            </span>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 4 }}>
              {sampleInputs.map((sample, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setTestText(sample)}
                  className="btn btn-secondary btn-sm"
                  style={{ fontSize: 11, padding: "2px 8px" }}
                >
                  Sample #{idx + 1}
                </button>
              ))}
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ fontSize: 12, color: "var(--color-text-muted)" }}>
                Confidence Threshold: <strong>{Math.round(threshold * 100)}%</strong>
              </span>
              <input
                type="range"
                min="0.40"
                max="0.95"
                step="0.05"
                value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                style={{ width: 120 }}
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-sm"
              disabled={testing || !testText.trim()}
            >
              <Play size={12} /> {testing ? "Testing..." : "Test Model"}
            </button>
          </div>
        </form>

        {/* Live Result Output */}
        {testResult && (
          <div style={{ marginTop: 16, background: "#F8F9FA", border: "1px solid var(--color-border)", borderRadius: "var(--radius-md)", padding: 14 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--color-border)", paddingBottom: 8, marginBottom: 10 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontWeight: 700, fontSize: 15, color: testResult.is_low_confidence ? "var(--color-warning)" : "var(--color-primary)" }}>
                  {testResult.predicted_category}
                </span>
                {testResult.is_low_confidence && (
                  <span className="badge" style={{ backgroundColor: "var(--color-warning-bg)", color: "var(--color-warning)", border: "1px solid #FDE68A" }}>
                    Fallback to Review (&lt; {Math.round(threshold * 100)}%)
                  </span>
                )}
              </div>

              <div style={{ fontSize: 13 }}>
                <span style={{ color: "var(--color-text-muted)" }}>Assigned Department: </span>
                <strong style={{ color: "var(--color-primary)" }}>{testResult.suggested_department}</strong>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
              <div className="simple-panel" style={{ padding: 10, margin: 0 }}>
                <div style={{ fontSize: 11, color: "var(--color-text-muted)", textTransform: "uppercase" }}>Priority Heuristic</div>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 4 }}>
                  <PriorityBadge priority={testResult.suggested_priority} />
                  <span style={{ fontSize: 12, color: "var(--color-text-muted)" }}>{testResult.priority_reason}</span>
                </div>
              </div>

              <div className="simple-panel" style={{ padding: 10, margin: 0 }}>
                <div style={{ fontSize: 11, color: "var(--color-text-muted)", textTransform: "uppercase" }}>Normalized Cleaned Text</div>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--color-text)", marginTop: 4 }}>
                  {testResult.cleaned_text || "(empty)"}
                </div>
              </div>
            </div>

            <ConfidenceMeter
              confidence={testResult.raw_confidence}
              isLowConfidence={testResult.is_low_confidence}
              topPredictions={testResult.top_predictions}
              threshold={threshold}
            />
          </div>
        )}
      </div>

      {/* Candidate Algorithm Comparison Table */}
      {data && (
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Model Comparison Benchmarks</h2>
              <div className="card-subtitle">
                Comparison evaluated on identical 20% test split.
              </div>
            </div>
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Algorithm</th>
                  <th>Accuracy</th>
                  <th>Precision</th>
                  <th>Recall</th>
                  <th>Macro F1</th>
                  <th>Weighted F1</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(data.comparison_benchmarks).map(([modelName, metrics]) => (
                  <tr key={modelName} style={{ backgroundColor: modelName === data.selected_model ? "#F8FFF8" : "transparent" }}>
                    <td style={{ fontWeight: 600 }}>
                      {modelName} {modelName === data.selected_model && <span style={{ color: "#1E7E34", fontSize: 11 }}>(Active)</span>}
                    </td>
                    <td style={{ fontFamily: "var(--font-mono)" }}>{(metrics.accuracy * 100).toFixed(1)}%</td>
                    <td style={{ fontFamily: "var(--font-mono)" }}>{metrics.macro_precision.toFixed(4)}</td>
                    <td style={{ fontFamily: "var(--font-mono)" }}>{metrics.macro_recall.toFixed(4)}</td>
                    <td style={{ fontFamily: "var(--font-mono)", fontWeight: 600 }}>{metrics.macro_f1.toFixed(4)}</td>
                    <td style={{ fontFamily: "var(--font-mono)" }}>{metrics.weighted_f1.toFixed(4)}</td>
                    <td style={{ fontSize: 12 }}>
                      {modelName === data.selected_model ? (
                        <span style={{ color: "#1E7E34", fontWeight: 600 }}>Selected Model</span>
                      ) : (
                        <span style={{ color: "var(--color-text-muted)" }}>Baseline</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Per-Category Evaluation Metrics */}
      {data && (
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Per-Category Performance</h2>
              <div className="card-subtitle">
                Class-level precision, recall, and F1 metrics on test data.
              </div>
            </div>
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Precision</th>
                  <th>Recall</th>
                  <th>F1-Score</th>
                  <th>Support (Test Rows)</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(data.per_class_metrics).map(([cat, m]) => (
                  <tr key={cat}>
                    <td style={{ fontWeight: 500 }}>{cat}</td>
                    <td style={{ fontFamily: "var(--font-mono)" }}>{m.precision.toFixed(3)}</td>
                    <td style={{ fontFamily: "var(--font-mono)" }}>{m.recall.toFixed(3)}</td>
                    <td style={{ fontFamily: "var(--font-mono)", fontWeight: 600 }}>{m["f1-score"].toFixed(3)}</td>
                    <td style={{ fontFamily: "var(--font-mono)" }}>{m.support}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Confusion Matrix */}
      {data && data.confusion_matrix && (
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Confusion Matrix</h2>
              <div className="card-subtitle">
                Rows = Actual category; Columns = Predicted category.
              </div>
            </div>
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th style={{ backgroundColor: "#F0F2F5" }}>Actual \ Predicted</th>
                  {data.confusion_matrix.labels.map((lbl, idx) => (
                    <th key={idx} style={{ fontSize: 10, maxWidth: 75, overflow: "hidden", textOverflow: "ellipsis" }} title={lbl}>
                      {lbl.split(" ")[0]}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.confusion_matrix.matrix.map((row, rowIdx) => (
                  <tr key={rowIdx}>
                    <td style={{ fontWeight: 600, fontSize: 12, backgroundColor: "#F8F9FA" }}>
                      {data.confusion_matrix.labels[rowIdx]}
                    </td>
                    {row.map((val, colIdx) => (
                      <td
                        key={colIdx}
                        style={{
                          textAlign: "center",
                          fontFamily: "var(--font-mono)",
                          fontSize: 12,
                          backgroundColor: rowIdx === colIdx ? (val > 0 ? "#EDF7ED" : "#F8F9FA") : (val > 0 ? "#FDE8E8" : "transparent"),
                          color: rowIdx === colIdx ? "#1E7E34" : (val > 0 ? "#C5221F" : "#888888"),
                          fontWeight: val > 0 ? 600 : 400
                        }}
                      >
                        {val}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
