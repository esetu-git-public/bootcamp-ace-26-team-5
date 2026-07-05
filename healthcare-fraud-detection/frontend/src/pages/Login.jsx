import { useNavigate } from "react-router-dom";
import { useState } from "react";

export default function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = (e) => {
    e.preventDefault();
    navigate("/dashboard");
  };

  return (
    <div style={{height:"100vh",display:"flex",justifyContent:"center",alignItems:"center",background:"#f4f7fa"}}>
      <div style={{width:"350px",background:"#fff",padding:"30px",borderRadius:"10px",boxShadow:"0 5px 15px rgba(0,0,0,.15)"}}>
        <h2 style={{textAlign:"center",marginBottom:"20px"}}>Healthcare Fraud Detection</h2>

        <form onSubmit={handleLogin}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e)=>setEmail(e.target.value)}
            style={{width:"100%",padding:"10px",marginBottom:"15px"}}
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e)=>setPassword(e.target.value)}
            style={{width:"100%",padding:"10px",marginBottom:"20px"}}
          />

          <button
            type="submit"
            style={{width:"100%",padding:"12px",background:"#2563eb",color:"white",border:"none",borderRadius:"5px",cursor:"pointer"}}
          >
            Login
          </button>
        </form>
      </div>
    </div>
  );
}
