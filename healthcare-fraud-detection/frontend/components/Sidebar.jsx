import { Link } from "react-router-dom";

export default function Sidebar() {
  return (
    <div style={{
      width:"240px",
      background:"#1f2937",
      color:"white",
      minHeight:"100vh",
      padding:"20px"
    }}>
      <h2>Menu</h2>

      <p><Link to="/dashboard">Dashboard</Link></p>
      <p><Link to="/claims">Claims</Link></p>
      <p><Link to="/submit">Submit Claim</Link></p>
      <p><Link to="/investigation">Investigation</Link></p>
      <p><Link to="/reports">Reports</Link></p>
    </div>
  );
}
