import { Link } from "react-router-dom";

const menu = [
  { name: "Dashboard", path: "/dashboard" },
  { name: "Claim History", path: "/claims" },
  { name: "Submit Claim", path: "/submit" },
  { name: "Investigation", path: "/investigation" },
  { name: "Reports", path: "/reports" }
];

export default function Sidebar() {
  return (
    <div
      style={{
        width: "240px",
        background: "#0f172a",
        color: "white",
        minHeight: "100vh",
        padding: "20px"
      }}
    >
      <h2 style={{ marginBottom: "30px" }}>
        Healthcare Fraud
      </h2>

      {menu.map((item) => (
        <Link
          key={item.name}
          to={item.path}
          style={{
            display: "block",
            color: "white",
            textDecoration: "none",
            padding: "12px",
            borderRadius: "8px",
            marginBottom: "10px",
            background: "#1e293b"
          }}
        >
          {item.name}
        </Link>
      ))}
    </div>
  );
}