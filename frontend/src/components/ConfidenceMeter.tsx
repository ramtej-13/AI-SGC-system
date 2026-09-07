import React from "react";
import { TopPrediction } from "../types";

interface ConfidenceMeterProps {
  confidence: number;
  isLowConfidence: boolean;
  topPredictions?: TopPrediction[];
  threshold?: number;
}

export const ConfidenceMeter: React.FC<ConfidenceMeterProps> = ({
  confidence,
  isLowConfidence,
  topPredictions = [],
  threshold = 0.70
}) => {
  const pct = Math.round(confidence * 100);
  const barColor = isLowConfidence ? "#B78103" : "#1E7E34";

  return (
    <div style={{ marginTop: 8 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
        <span style={{ fontSize: 12, fontWeight: 500, color: "var(--color-text-muted)" }}>
          Confidence Score
        </span>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          {isLowConfidence ? (
            <span style={{ fontSize: 11, color: "var(--color-warning)" }}>
              Below Threshold ({Math.round(threshold * 100)}%)
            </span>
          ) : (
            <span style={{ fontSize: 11, color: "#1E7E34" }}>
              High Confidence
            </span>
          )}
          <span style={{ fontFamily: "var(--font-mono)", fontWeight: 600, fontSize: 13 }}>
            {pct}%
          </span>
        </div>
      </div>

      {/* Confidence Bar */}
      <div style={{ width: "100%", height: 5, backgroundColor: "#E5E7EB", borderRadius: 3, overflow: "hidden" }}>
        <div
          style={{
            width: `${Math.min(pct, 100)}%`,
            height: "100%",
            backgroundColor: barColor
          }}
        />
      </div>

      {/* Top 3 Predictions Explainability */}
      {topPredictions.length > 0 && (
        <div style={{ marginTop: 10, background: "#F8F9FA", padding: "8px 10px", borderRadius: "var(--radius-sm)", border: "1px solid var(--color-border)" }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: "var(--color-text-muted)", textTransform: "uppercase", marginBottom: 4 }}>
            Top Predictions:
          </div>
          {topPredictions.map((pred, i) => (
            <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: 12, margin: "2px 0" }}>
              <span style={{ color: i === 0 ? "var(--color-primary)" : "var(--color-text)", fontWeight: i === 0 ? 600 : 400 }}>
                {i + 1}. {pred.category}
              </span>
              <span style={{ fontFamily: "var(--font-mono)", color: "var(--color-text-muted)" }}>
                {(pred.probability * 100).toFixed(1)}%
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
