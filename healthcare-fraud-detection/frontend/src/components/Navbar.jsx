export default function Navbar() {
  return (
    <div
      style={{
        height: "70px",
        background: "white",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "0 30px",
        boxShadow: "0 2px 10px rgba(0,0,0,.08)"
      }}
    >
      <h2>Healthcare Fraud Detection System</h2>

      <div>
        👤 Admin
      </div>
    </div>
  );
}