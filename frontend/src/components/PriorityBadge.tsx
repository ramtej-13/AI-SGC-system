import React from "react";
import { AlertCircle, AlertTriangle, CheckCircle } from "lucide-react";

interface PriorityBadgeProps {
  priority: string;
}

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({ priority }) => {
  const p = priority.toLowerCase();
  
  if (p === "high") {
    return (
      <span
        className="badge"
        style={{
          backgroundColor: "#FEF2F2",
          color: "#B91C1C",
          border: "1px solid #FECACA"
        }}
      >
        <AlertCircle size={12} />
        High
      </span>
    );
  } else if (p === "medium") {
    return (
      <span
        className="badge"
        style={{
          backgroundColor: "#FFFBEB",
          color: "#B45309",
          border: "1px solid #FDE68A"
        }}
      >
        <AlertTriangle size={12} />
        Medium
      </span>
    );
  }

  return (
    <span
      className="badge"
      style={{
        backgroundColor: "#F3F4F6",
        color: "#4B5563",
        border: "1px solid #E5E7EB"
      }}
    >
      <CheckCircle size={12} />
      Low
    </span>
  );
};
