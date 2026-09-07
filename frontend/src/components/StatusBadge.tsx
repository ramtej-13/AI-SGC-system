import React from "react";

interface StatusBadgeProps {
  status: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  let bg = "#F3F4F6";
  let color = "#374151";
  let border = "#E5E7EB";

  switch (status.toLowerCase()) {
    case "submitted":
      bg = "#EFF6FF";
      color = "#1D4ED8";
      border = "#BFDBFE";
      break;
    case "assigned":
      bg = "#F5F3FF";
      color = "#6D28D9";
      border = "#DDD6FE";
      break;
    case "in progress":
      bg = "#FFFBEB";
      color = "#B45309";
      border = "#FDE68A";
      break;
    case "resolved":
      bg = "#ECFDF5";
      color = "#047857";
      border = "#A7F3D0";
      break;
    case "closed":
      bg = "#F3F4F6";
      color = "#4B5563";
      border = "#D1D5DB";
      break;
  }

  return (
    <span
      className="badge"
      style={{
        backgroundColor: bg,
        color: color,
        border: `1px solid ${border}`
      }}
    >
      <span
        style={{
          width: 6,
          height: 6,
          borderRadius: "50%",
          backgroundColor: color,
          display: "inline-block"
        }}
      />
      {status}
    </span>
  );
};
