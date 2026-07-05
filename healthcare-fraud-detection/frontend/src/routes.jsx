import { Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import SubmitClaim from "./pages/SubmitClaim";
import ClaimHistory from "./pages/ClaimHistory";
import Investigation from "./pages/Investigation";
import Reports from "./pages/Reports";
import NotFound from "./pages/NotFound";

export default function AppRoutes() {
  return (
  <Routes>
    <Route path="/" element={<Login />} />
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/submit" element={<SubmitClaim />} />
    <Route path="/claims" element={<ClaimHistory />} />
    <Route path="/investigation" element={<Investigation />} />
    <Route path="/reports" element={<Reports />} />
    <Route path="*" element={<NotFound />} />
  </Routes>
  );
}
