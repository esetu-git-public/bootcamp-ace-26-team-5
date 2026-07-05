import { useState } from "react";
import MainLayout from "../layouts/MainLayout";

export default function Investigation() {
  const [claims, setClaims] = useState([
    {
      id: "CLM001",
      patient: "John Doe",
      amount: "$4500",
      risk: "High",
      reason: "Duplicate Claims",
      status: "Pending",
    },
    {
      id: "CLM004",
      patient: "Emily",
      amount: "$6100",
      risk: "High",
      reason: "Suspicious Billing",
      status: "Pending",
    },
    {
      id: "CLM007",
      patient: "Robert",
      amount: "$8000",
      risk: "High",
      reason: "Multiple Hospital Visits",
      status: "Pending",
    },
  ]);

  const updateStatus = (id, status) => {
    setClaims(
      claims.map((claim) =>
        claim.id === id ? { ...claim, status } : claim
      )
    );
  };

  return (
    <MainLayout>
      <h1>Investigation Queue</h1>

      <p style={{ color: "gray", marginBottom: "20px" }}>
        Review high-risk insurance claims detected by the ML model.
      </p>

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
              <th style={styles.th}>Reason</th>
              <th style={styles.th}>Status</th>
              <th style={styles.th}>Action</th>
            </tr>
          </thead>

          <tbody>
            {claims.map((claim) => (
              <tr key={claim.id}>
                <td style={styles.td}>{claim.id}</td>
                <td style={styles.td}>{claim.patient}</td>
                <td style={styles.td}>{claim.amount}</td>

                <td
                  style={{
                    ...styles.td,
                    color: "red",
                    fontWeight: "bold",
                  }}
                >
                  {claim.risk}
                </td>

                <td style={styles.td}>{claim.reason}</td>

                <td style={styles.td}>{claim.status}</td>

                <td style={styles.td}>
                  <button
                    onClick={() => updateStatus(claim.id, "Approved")}
                    style={styles.approve}
                  >
                    Approve
                  </button>

                  <button
                    onClick={() => updateStatus(claim.id, "Rejected")}
                    style={styles.reject}
                  >
                    Reject
                  </button>
                </td>
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

  approve: {
    background: "#16a34a",
    color: "white",
    border: "none",
    padding: "8px 12px",
    marginRight: "10px",
    borderRadius: "6px",
    cursor: "pointer",
  },

  reject: {
    background: "#dc2626",
    color: "white",
    border: "none",
    padding: "8px 12px",
    borderRadius: "6px",
    cursor: "pointer",
  },
};