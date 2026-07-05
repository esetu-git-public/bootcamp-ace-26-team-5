import MainLayout from "../layouts/MainLayout";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const monthlyData = [
  { month: "Jan", claims: 120 },
  { month: "Feb", claims: 160 },
  { month: "Mar", claims: 140 },
  { month: "Apr", claims: 190 },
  { month: "May", claims: 220 },
  { month: "Jun", claims: 180 },
];

const pieData = [
  { name: "Approved", value: 1100 },
  { name: "Fraud", value: 85 },
  { name: "Pending", value: 65 },
];

const COLORS = ["#22c55e", "#ef4444", "#f59e0b"];

export default function Reports() {
  return (
    <MainLayout>
      <h1>Reports & Analytics</h1>

      <p style={{ color: "#666", marginBottom: "25px" }}>
        Healthcare Insurance Claim Statistics
      </p>

      {/* Summary Cards */}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))",
          gap: "20px",
          marginBottom: "30px",
        }}
      >
        <Card title="Total Claims" value="1250" color="#2563eb" />
        <Card title="Approved" value="1100" color="#22c55e" />
        <Card title="Fraud Cases" value="85" color="#ef4444" />
        <Card title="Pending" value="65" color="#f59e0b" />
      </div>

      {/* Charts */}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "2fr 1fr",
          gap: "25px",
        }}
      >
        <div
          style={{
            background: "white",
            padding: "20px",
            borderRadius: "12px",
            boxShadow: "0 5px 10px rgba(0,0,0,.08)",
          }}
        >
          <h3>Monthly Claims</h3>

          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="claims" fill="#2563eb" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div
          style={{
            background: "white",
            padding: "20px",
            borderRadius: "12px",
            boxShadow: "0 5px 10px rgba(0,0,0,.08)",
          }}
        >
          <h3>Claim Status</h3>

          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                dataKey="value"
                outerRadius={90}
                label
              >
                {pieData.map((entry, index) => (
                  <Cell
                    key={index}
                    fill={COLORS[index]}
                  />
                ))}
              </Pie>

              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </MainLayout>
  );
}

function Card({ title, value, color }) {
  return (
    <div
      style={{
        background: "white",
        padding: "20px",
        borderRadius: "12px",
        boxShadow: "0 5px 10px rgba(0,0,0,.08)",
      }}
    >
      <h4 style={{ color: "#666" }}>{title}</h4>

      <h1 style={{ color, marginTop: "10px" }}>{value}</h1>
    </div>
  );
}