import { useEffect, useState } from 'react';
import { Grid, Card, Box, Typography, Stack, Table, TableHead, TableRow, TableCell, TableBody, LinearProgress, Chip } from '@mui/material';
import { LineChart, Line, AreaChart, Area, PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined';
import ReportProblemOutlinedIcon from '@mui/icons-material/ReportProblemOutlined';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import HourglassEmptyOutlinedIcon from '@mui/icons-material/HourglassEmptyOutlined';
import PriorityHighOutlinedIcon from '@mui/icons-material/PriorityHighOutlined';
import PercentOutlinedIcon from '@mui/icons-material/PercentOutlined';
import DashboardLayout from '../components/layout/DashboardLayout';
import KpiCard from '../components/common/KpiCard';
import { RiskChip, StatusChip } from '../components/common/RiskChip';
import EmptyState from '../components/common/EmptyState';
import * as dashboardService from '../services/dashboardService';
import { useNavigate } from 'react-router-dom';
import theme, { riskColor } from '../theme/theme';
import { useAuth, ROLES } from '../context/AuthContext';
import UserDashboard from './UserDashboard';

const STATUS_COLORS = ['#1E9E6B', '#D8A400', '#1B4F9C', '#D6483C'];

export default function Dashboard() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Customers get a scoped dashboard showing only their own claims.
  const isPolicyholder = user?.role === ROLES.CUSTOMER;

  useEffect(() => {
    if (user?.role === ROLES.EMPLOYEE) {
      navigate('/investigation', { replace: true });
      return;
    }
    if (isPolicyholder) return;
    dashboardService.getDashboard().then((d) => { setData(d); setLoading(false); });
  }, [isPolicyholder, user, navigate]);

  if (isPolicyholder) {
    return <UserDashboard />;
  }

  if (loading) {
    return (
      <DashboardLayout title="Dashboard">
        <LinearProgress />
      </DashboardLayout>
    );
  }

  const { kpis, monthlyClaims, riskDistribution, statusDistribution, recentClaims } = data;

  return (
    <DashboardLayout title="Dashboard">
      <Grid container spacing={2.5}>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <KpiCard label="Total Claims" value={kpis.total} icon={<DescriptionOutlinedIcon />} accent={theme.tokens.blue} />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <KpiCard label="Fraud Claims" value={kpis.fraud} icon={<ReportProblemOutlinedIcon />} accent={theme.tokens.high} />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <KpiCard label="Genuine Claims" value={kpis.genuine} icon={<CheckCircleOutlineIcon />} accent={theme.tokens.low} />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <KpiCard label="Pending Claims" value={kpis.pending} icon={<HourglassEmptyOutlinedIcon />} accent={theme.tokens.medium} />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <KpiCard label="High Risk" value={kpis.highRisk} icon={<PriorityHighOutlinedIcon />} accent={theme.tokens.high} />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <KpiCard label="Fraud %" value={kpis.fraudPct} suffix="%" icon={<PercentOutlinedIcon />} accent={theme.tokens.teal} />
        </Grid>

        <Grid item xs={12} md={7}>
          <Card sx={{ p: 2.5, height: 340 }}>
            <Typography variant="subtitle1" sx={{ mb: 2 }}>Monthly Claims &amp; Fraud Trend</Typography>
            <ResponsiveContainer width="100%" height="85%">
              <AreaChart data={monthlyClaims}>
                <defs>
                  <linearGradient id="claimsGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={theme.tokens.blue} stopOpacity={0.35} />
                    <stop offset="95%" stopColor={theme.tokens.blue} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#EDF1F5" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="claims" name="Total Claims" stroke={theme.tokens.blue} fill="url(#claimsGrad)" strokeWidth={2} />
                <Line type="monotone" dataKey="fraud" name="Fraud Claims" stroke={theme.tokens.high} strokeWidth={2} dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </Card>
        </Grid>

        <Grid item xs={12} md={5}>
          <Card sx={{ p: 2.5, height: 340 }}>
            <Typography variant="subtitle1" sx={{ mb: 2 }}>Risk Distribution</Typography>
            <ResponsiveContainer width="100%" height="85%">
              <PieChart>
                <Pie data={riskDistribution} dataKey="count" nameKey="level" innerRadius={55} outerRadius={85} paddingAngle={3}>
                  {riskDistribution.map((entry) => (
                    <Cell key={entry.level} fill={riskColor(entry.level)} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Grid>

        <Grid item xs={12} md={5}>
          <Card sx={{ p: 2.5, height: 320 }}>
            <Typography variant="subtitle1" sx={{ mb: 2 }}>Claim Status</Typography>
            <ResponsiveContainer width="100%" height="85%">
              <BarChart data={statusDistribution} layout="vertical" margin={{ left: 24 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#EDF1F5" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 12 }} />
                <YAxis type="category" dataKey="status" tick={{ fontSize: 11 }} width={110} />
                <Tooltip />
                <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                  {statusDistribution.map((entry, idx) => (
                    <Cell key={entry.status} fill={STATUS_COLORS[idx % STATUS_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Grid>

        <Grid item xs={12} md={7}>
          <Card sx={{ p: 2.5 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="subtitle1">Recent Claims</Typography>
              <Chip size="small" label="View all" onClick={() => navigate('/claims')} sx={{ cursor: 'pointer' }} />
            </Stack>
            {recentClaims.length === 0 ? (
              <EmptyState title="No claims yet" description="Submitted claims will appear here." />
            ) : (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Claim ID</TableCell>
                    <TableCell>Patient</TableCell>
                    <TableCell>Amount</TableCell>
                    <TableCell>Risk</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Date</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recentClaims.map((c) => (
                    <TableRow key={c.id} hover sx={{ cursor: 'pointer' }} onClick={() => navigate(`/claims/${c.id}`)}>
                      <TableCell sx={{ fontWeight: 600 }}>{c.id}</TableCell>
                      <TableCell>{c.patient.name}</TableCell>
                      <TableCell>${c.financial.claimAmount.toLocaleString()}</TableCell>
                      <TableCell><RiskChip level={c.prediction.riskLevel} /></TableCell>
                      <TableCell><StatusChip status={c.status} /></TableCell>
                      <TableCell>{c.dates.claimDate}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </Card>
        </Grid>
      </Grid>
    </DashboardLayout>
  );
}
