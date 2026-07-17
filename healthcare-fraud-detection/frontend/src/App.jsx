import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import theme from './theme/theme';
import { AuthProvider, ROLES } from './context/AuthContext';
import ProtectedRoute from './components/common/ProtectedRoute';

import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import UserDashboard from './pages/UserDashboard';
import SubmitClaim from './pages/SubmitClaim';
import ClaimHistory from './pages/ClaimHistory';
import ClaimDetails from './pages/ClaimDetails';
import Investigation from './pages/Investigation';
import Reports from './pages/Reports';
import ModelPerformance from './pages/ModelPerformance';
import Notifications from './pages/Notifications';
import Profile from './pages/Profile';

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            {/* Standard Authentication */}
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />

            {/* Dedicated Role-Prefilled Demo Entry Portals */}
            <Route path="/customer" element={<Login prefilledRole="customer" />} />
            <Route path="/officer" element={<Login prefilledRole="officer" />} />
            <Route path="/admin" element={<Login prefilledRole="admin" />} />

            {/* Standard Combined Routing Endpoint */}
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />

            {/* Explicit Role-Specific Protected Dashboards */}
            <Route
              path="/customer/dashboard"
              element={<ProtectedRoute roles={[ROLES.CUSTOMER]}><UserDashboard /></ProtectedRoute>}
            />
            <Route
              path="/officer/dashboard"
              element={<ProtectedRoute roles={[ROLES.EMPLOYEE, ROLES.ADMIN]}><Investigation /></ProtectedRoute>}
            />
            <Route
              path="/admin/dashboard"
              element={<ProtectedRoute roles={[ROLES.ADMIN]}><Dashboard /></ProtectedRoute>}
            />

            <Route
              path="/claims/submit"
              element={<ProtectedRoute roles={[ROLES.CUSTOMER]}><SubmitClaim /></ProtectedRoute>}
            />
            <Route path="/claims" element={<ProtectedRoute><ClaimHistory /></ProtectedRoute>} />
            <Route path="/claims/:id" element={<ProtectedRoute><ClaimDetails /></ProtectedRoute>} />

            <Route
              path="/investigation"
              element={<ProtectedRoute roles={[ROLES.EMPLOYEE, ROLES.ADMIN]}><Investigation /></ProtectedRoute>}
            />
            <Route
              path="/reports"
              element={<ProtectedRoute roles={[ROLES.ADMIN]}><Reports /></ProtectedRoute>}
            />
            <Route
              path="/model-performance"
              element={<ProtectedRoute roles={[ROLES.EMPLOYEE, ROLES.ADMIN]}><ModelPerformance /></ProtectedRoute>}
            />

            <Route path="/notifications" element={<ProtectedRoute><Notifications /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />

            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  );
}
