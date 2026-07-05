import { useState } from "react";
import MainLayout from "../layouts/MainLayout";

export default function SubmitClaim() {
  const [formData, setFormData] = useState({
    patientName: "",
    age: "",
    gender: "",
    claimAmount: "",
    diagnosis: "",
    hospital: "",
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    console.log(formData);

    alert("Claim submitted successfully! (Backend integration coming next)");
  };

  return (
    <MainLayout>
      <div
        style={{
          background: "#fff",
          padding: "30px",
          borderRadius: "12px",
          boxShadow: "0 5px 15px rgba(0,0,0,0.08)",
        }}
      >
        <h1>Submit Insurance Claim</h1>

        <p style={{ color: "gray", marginBottom: "30px" }}>
          Enter claim details for fraud prediction.
        </p>

        <form onSubmit={handleSubmit}>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(2,1fr)",
              gap: "20px",
            }}
          >
            <div>
              <label>Patient Name</label>

              <input
                type="text"
                name="patientName"
                value={formData.patientName}
                onChange={handleChange}
                style={styles.input}
                required
              />
            </div>

            <div>
              <label>Age</label>

              <input
                type="number"
                name="age"
                value={formData.age}
                onChange={handleChange}
                style={styles.input}
                required
              />
            </div>

            <div>
              <label>Gender</label>

              <select
                name="gender"
                value={formData.gender}
                onChange={handleChange}
                style={styles.input}
              >
                <option value="">Select</option>
                <option>Male</option>
                <option>Female</option>
              </select>
            </div>

            <div>
              <label>Claim Amount ($)</label>

              <input
                type="number"
                name="claimAmount"
                value={formData.claimAmount}
                onChange={handleChange}
                style={styles.input}
              />
            </div>

            <div>
              <label>Diagnosis</label>

              <input
                type="text"
                name="diagnosis"
                value={formData.diagnosis}
                onChange={handleChange}
                style={styles.input}
              />
            </div>

            <div>
              <label>Hospital Name</label>

              <input
                type="text"
                name="hospital"
                value={formData.hospital}
                onChange={handleChange}
                style={styles.input}
              />
            </div>
          </div>

          <button
            type="submit"
            style={{
              marginTop: "30px",
              padding: "12px 30px",
              background: "#2563eb",
              color: "white",
              border: "none",
              borderRadius: "8px",
              cursor: "pointer",
              fontSize: "16px",
            }}
          >
            Submit Claim
          </button>
        </form>
      </div>
    </MainLayout>
  );
}

const styles = {
  input: {
    width: "100%",
    padding: "10px",
    marginTop: "8px",
    borderRadius: "6px",
    border: "1px solid #ccc",
    boxSizing: "border-box",
  },
};