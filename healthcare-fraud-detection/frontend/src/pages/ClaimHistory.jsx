import { useState } from "react";
import MainLayout from "../layouts/MainLayout";

export default function ClaimHistory() {
  const [search, setSearch] = useState("");

  const claims = [
    {
      id: "CLM001",
      patient: "John Doe",
      amount: "$4,500",
      risk: "High",
      status: "Pending",
    },
    {
      id: "CLM002",
      patient: "Smith",
      amount: "$1,250",
      risk: "Low",
      status: "Approved",
    },
    {
      id: "CLM003",
      patient: "David",
      amount: "$2,750",
      risk: "Medium",
      status: "Under Review",
    },
    {
      id: "CLM004",
      patient: "Emily",
      amount: "$6,100",
      risk: "High",
      status: "Rejected",
    },
  ];

  const filteredClaims = claims.filter(
    (claim) =>
      claim.patient.toLowerCase().includes(search.toLowerCase()) ||
      claim.id.toLowerCase().includes(search.toLowerCase())
  );

  const riskColor = (risk) => {
    if (risk === "High") return "red";
    if (risk === "Medium") return "orange";
    return "green";
  };

  return (
    <MainLayout>
      <h1>Claim History</h1>

      <p style={{ color: "gray" }}>
        View and search all insurance claims.
      </p>

      <input
        type="text"
        placeholder="Search by Claim ID or Patient..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        style={{
          width: "100%",
          padding: "12px",
          margin: "20px 0",
          borderRadius: "8px",
          border: "1px solid #ccc",
        }}
      />

      <div
        style={{
          background: "white",
          borderRadius: "12px",
          padding: "20px",
          boxShadow: "0 5px 12px rgba(0,0,0,.08)",
        }}
      >
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
          }}
        >
          <thead>
            <tr style={{ background: "#f3f4f6" }}>
              <th style={styles.th}>Claim ID</th>
              <th style={styles.th}>Patient</th>
              <th style={styles.th}>Amount</th>
              <th style={styles.th}>Risk</th>
              <th style={styles.th}>Status</th>
            </tr>
          </thead>

          <tbody>
            {filteredClaims.map((claim) => (
              <tr key={claim.id}>
                <td style={styles.td}>{claim.id}</td>
                <td style={styles.td}>{claim.patient}</td>
                <td style={styles.td}>{claim.amount}</td>

                <td
                  style={{
                    ...styles.td,
                    color: riskColor(claim.risk),
                    fontWeight: "bold",
                  }}
                >
                  {claim.risk}
                </td>

                <td style={styles.td}>{claim.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </MainLayout>
  );
}

const styles = {
  th: {
    padding: "12px",
    textAlign: "left",
    borderBottom: "1px solid #ddd",
  },
  td: {
    padding: "12px",
    borderBottom: "1px solid #eee",
  },
};