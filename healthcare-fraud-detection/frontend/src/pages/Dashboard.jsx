import {
  FaFileInvoice,
  FaUserCheck,
  FaExclamationTriangle,
  FaSearch,
} from "react-icons/fa";
import MainLayout from "../layouts/MainLayout";

export default function Dashboard() {
  const cards = [
    {
      title: "Total Claims",
      value: "1,250",
      color: "#2563eb",
      icon: <FaFileInvoice size={28} />,
    },
    {
      title: "Approved",
      value: "1,100",
      color: "#16a34a",
      icon: <FaUserCheck size={28} />,
    },
    {
      title: "Fraud Detected",
      value: "85",
      color: "#dc2626",
      icon: <FaExclamationTriangle size={28} />,
    },
    {
      title: "Pending Review",
      value: "65",
      color: "#f59e0b",
      icon: <FaSearch size={28} />,
    },
  ];

  return (
    <MainLayout>
      <div
        style={{
          minHeight: "100vh",
          background: "#f5f7fb",
          padding: "30px",
        }}
      >
        <h1
          style={{
            marginBottom: "5px",
            color: "#1e293b",
          }}
        >
          Healthcare Fraud Detection Dashboard
        </h1>

        <p
          style={{
            color: "#64748b",
            marginBottom: "30px",
          }}
        >
          Welcome back, Admin 👋
        </p>

        {/* Dashboard Cards */}

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))",
            gap: "20px",
          }}
        >
          {cards.map((card, index) => (
            <div
              key={index}
              style={{
                background: "#fff",
                padding: "22px",
                borderRadius: "16px",
                boxShadow: "0 8px 20px rgba(0,0,0,.08)",
                transition: ".3s",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div>
                  <p
                    style={{
                      color: "#64748b",
                      marginBottom: "8px",
                    }}
                  >
                    {card.title}
                  </p>

                  <h2
                    style={{
                      margin: 0,
                    }}
                  >
                    {card.value}
                  </h2>
                </div>

                <div
                  style={{
                    background: `${card.color}20`,
                    padding: "15px",
                    borderRadius: "12px",
                    color: card.color,
                  }}
                >
                  {card.icon}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Recent Claims */}

        <div
          style={{
            marginTop: "40px",
            background: "#fff",
            borderRadius: "16px",
            padding: "25px",
            boxShadow: "0 8px 20px rgba(0,0,0,.08)",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "20px",
            }}
          >
            <div>
              <h2
                style={{
                  margin: 0,
                }}
              >
                Recent Claims
              </h2>

              <p
                style={{
                  color: "#64748b",
                  marginTop: "5px",
                }}
              >
                Latest insurance claims received
              </p>
            </div>

            <button
              style={{
                background: "#2563eb",
                color: "#fff",
                border: "none",
                padding: "10px 18px",
                borderRadius: "8px",
                cursor: "pointer",
              }}
            >
              View All
            </button>
          </div>

          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
            }}
          >
            <thead>
              <tr
                style={{
                  background: "#f8fafc",
                }}
              >
                <th style={styles.th}>Claim ID</th>
                <th style={styles.th}>Patient</th>
                <th style={styles.th}>Amount</th>
                <th style={styles.th}>Risk</th>
                <th style={styles.th}>Status</th>
              </tr>
            </thead>

            <tbody>
              <tr>
                <td style={styles.td}>CLM001</td>
                <td style={styles.td}>John Doe</td>
                <td style={styles.td}>$4,500</td>

                <td style={styles.td}>
                  <span style={styles.highRisk}>High</span>
                </td>

                <td style={styles.td}>
                  <span style={styles.pending}>Pending</span>
                </td>
              </tr>

              <tr>
                <td style={styles.td}>CLM002</td>
                <td style={styles.td}>Sarah Smith</td>
                <td style={styles.td}>$2,250</td>

                <td style={styles.td}>
                  <span style={styles.lowRisk}>Low</span>
                </td>

                <td style={styles.td}>
                  <span style={styles.approved}>Approved</span>
                </td>
              </tr>

              <tr>
                <td style={styles.td}>CLM003</td>
                <td style={styles.td}>David Miller</td>
                <td style={styles.td}>$6,850</td>

                <td style={styles.td}>
                  <span style={styles.mediumRisk}>Medium</span>
                </td>

                <td style={styles.td}>
                  <span style={styles.review}>Under Review</span>
                </td>
              </tr>

              <tr>
                <td style={styles.td}>CLM004</td>
                <td style={styles.td}>Emily Clark</td>
                <td style={styles.td}>$8,200</td>

                <td style={styles.td}>
                  <span style={styles.highRisk}>High</span>
                </td>

                <td style={styles.td}>
                  <span style={styles.rejected}>Rejected</span>
                </td>
              </tr>

              <tr>
                <td style={styles.td}>CLM005</td>
                <td style={styles.td}>Michael Brown</td>
                <td style={styles.td}>$3,100</td>

                <td style={styles.td}>
                  <span style={styles.lowRisk}>Low</span>
                </td>

                <td style={styles.td}>
                  <span style={styles.approved}>Approved</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </MainLayout>
  );
}

const styles = {
  th: {
    padding: "15px",
    textAlign: "left",
    color: "#475569",
    fontWeight: "600",
    borderBottom: "2px solid #e2e8f0",
  },

  td: {
    padding: "16px",
    borderBottom: "1px solid #e2e8f0",
  },

  highRisk: {
    background: "#fee2e2",
    color: "#dc2626",
    padding: "6px 14px",
    borderRadius: "20px",
    fontWeight: "bold",
    fontSize: "14px",
  },

  mediumRisk: {
    background: "#fef3c7",
    color: "#d97706",
    padding: "6px 14px",
    borderRadius: "20px",
    fontWeight: "bold",
    fontSize: "14px",
  },

  lowRisk: {
    background: "#dcfce7",
    color: "#16a34a",
    padding: "6px 14px",
    borderRadius: "20px",
    fontWeight: "bold",
    fontSize: "14px",
  },

  approved: {
    background: "#dcfce7",
    color: "#16a34a",
    padding: "6px 14px",
    borderRadius: "20px",
    fontWeight: "600",
    fontSize: "14px",
  },

  pending: {
    background: "#fef3c7",
    color: "#d97706",
    padding: "6px 14px",
    borderRadius: "20px",
    fontWeight: "600",
    fontSize: "14px",
  },

  review: {
    background: "#dbeafe",
    color: "#2563eb",
    padding: "6px 14px",
    borderRadius: "20px",
    fontWeight: "600",
    fontSize: "14px",
  },

  rejected: {
    background: "#fee2e2",
    color: "#dc2626",
    padding: "6px 14px",
    borderRadius: "20px",
    fontWeight: "600",
    fontSize: "14px",
  },
};