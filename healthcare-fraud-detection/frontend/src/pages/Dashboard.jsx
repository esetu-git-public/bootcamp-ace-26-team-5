import { useEffect, useState } from 'react';
import { 
  Grid, Card, Box, Typography, Stack, Table, TableHead, TableRow, TableCell, TableBody, 
  LinearProgress, Chip, Divider, List, ListItem, ListItemText, ListItemIcon 
} from '@mui/material';
import { ComposedChart, Area, Line, PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined';
import ReportProblemOutlinedIcon from '@mui/icons-material/ReportProblemOutlined';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import HourglassEmptyOutlinedIcon from '@mui/icons-material/HourglassEmptyOutlined';
import PriorityHighOutlinedIcon from '@mui/icons-material/PriorityHighOutlined';
import PeopleOutlinedIcon from '@mui/icons-material/PeopleOutlined';
import ShieldOutlinedIcon from '@mui/icons-material/ShieldOutlined';
import HistoryOutlinedIcon from '@mui/icons-material/HistoryOutlined';
import AdminPanelSettingsOutlinedIcon from '@mui/icons-material/AdminPanelSettingsOutlined';
import DashboardLayout from '../components/layout/DashboardLayout';
import KpiCard from '../components/common/KpiCard';
import { RiskChip, StatusChip } from '../components/common/RiskChip';
import EmptyState from '../components/common/EmptyState';
import * as dashboardService from '../services/dashboardService';
import * as claimsService from '../services/claimsService';
import { useNavigate } from 'react-router-dom';
import theme, { riskColor } from '../theme/theme';
import { useAuth, ROLES } from '../context/AuthContext';
import UserDashboard from './UserDashboard';

const STATUS_COLORS = ['#1E9E6B', '#D6483C', '#D8A400'];

const fallbackMockLogs = [
  { log_id: 1, action: 'USER_LOGIN', user_name: 'Claims Officer', details: 'User officer@fraudshield.com logged in.', timestamp: new Date().toISOString() },
  { log_id: 2, action: 'CLAIM_CREATION', user_name: 'Ava Thompson', details: 'Claim CLM-992381 created for policy POL-MOCK-1234.', timestamp: new Date(Date.now() - 60000).toISOString() },
  { log_id: 3, action: 'CLAIM_AUTO_APPROVAL', user_name: 'System', details: 'Claim CLM-992381 auto-approved (probability 12%).', timestamp: new Date(Date.now() - 58000).toISOString() },
  { log_id: 4, action: 'CLAIM_ROUTE_FOR_REVIEW', user_name: 'System', details: 'Claim CLM-5002 routed for review (risk=High).', timestamp: new Date(Date.now() - 120000).toISOString() },
  { log_id: 5, action: 'CLAIM_APPROVED', user_name: 'Claims Officer', details: 'Claims Officer approved claim CLM-5001.', timestamp: new Date(Date.now() - 300000).toISOString() }
];

export default function Dashboard() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [recentClaims, setRecentClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const isPolicyholder = user?.role === ROLES.CUSTOMER;

  useEffect(() => {
    if (user?.role === ROLES.EMPLOYEE) {
      navigate('/investigation', { replace: true });
      return;
    }
    if (isPolicyholder) return;

    const fetchData = () => {
      // 1. Fetch dashboard KPI statistics
      dashboardService.getDashboard('admin').then((d) => {
        setData(d);
      }).catch(err => console.error("Error fetching dashboard stats:", err));

      // 2. Fetch recent claims list
      claimsService.getClaims({ page: 1, per_page: 5 }).then((claims) => {
        setRecentClaims(claims.slice(0, 5));
        setLoading(false);
      }).catch(err => {
        console.error("Error fetching claims for dashboard:", err);
        setLoading(false);
      });
    };

    fetchData();
    const interval = setInterval(fetchData, 4000); // 4-second poll interval for real-time demo sync
    return () => clearInterval(interval);
  }, [isPolicyholder, user, navigate]);

  if (isPolicyholder) {
    return <UserDashboard />;
  }

  if (loading && !data) {
    return (
      <DashboardLayout title="Dashboard">
        <LinearProgress />
      </DashboardLayout>
    );
  }

  const { kpis, monthlyClaims, riskDistribution, statusDistribution, recentLogs } = data || {
    kpis: { total: 0, totalUsers: 0, totalPolicies: 0, genuine: 0, pending: 0, highRisk: 0, fraudPct: 0 },
    monthlyClaims: [],
    riskDistribution: [],
    statusDistribution: [],
    recentLogs: []
  };

  const activeLogs = recentLogs.length > 0 ? recentLogs : fallbackMockLogs;

  return (
    <DashboardLayout title="Executive Analytics Dashboard">
      <Grid container spacing={2.5}>
        {/* KPI Counter Row */}
        <Grid item xs={12} sm={4} md={2}>
          <KpiCard label="Total Users" value={kpis.totalUsers || 2} icon={<PeopleOutlinedIcon />} accent={theme.tokens.blue} />
        </Grid>
        <Grid item xs={12} sm={4} md={2}>
          <KpiCard label="Active Policies" value={kpis.totalPolicies || 3} icon={<ShieldOutlinedIcon />} accent={theme.tokens.teal} />
        </Grid>
        <Grid item xs={12} sm={4} md={2}>
          <KpiCard label="Total Claims" value={kpis.total} icon={<DescriptionOutlinedIcon />} accent={theme.tokens.blue} />
        </Grid>
        <Grid item xs={12} sm={4} md={2}>
          <KpiCard label="Approved Claims" value={kpis.genuine} icon={<CheckCircleOutlineIcon />} accent={theme.tokens.low} />
        </Grid>
        <Grid item xs={12} sm={4} md={2}>
          <KpiCard label="Pending Review" value={kpis.pending} icon={<HourglassEmptyOutlinedIcon />} accent={theme.tokens.medium} />
        </Grid>
        <Grid item xs={12} sm={4} md={2}>
          <KpiCard label="High Risk Flagged" value={kpis.highRisk} icon={<PriorityHighOutlinedIcon />} accent={theme.tokens.high} />
        </Grid>

        {/* Charts Row */}
        <Grid item xs={12} md={7}>
          <Card sx={{ p: 2.5, height: 350 }}>
            <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>Monthly Claims &amp; Fraud Trend</Typography>
            {monthlyClaims.length === 0 ? (
              <EmptyState title="No monthly data" description="Data will appear once claims are submitted." />
            ) : (
              <ResponsiveContainer width="100%" height="85%">
                <ComposedChart data={monthlyClaims}>
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
                </ComposedChart>
              </ResponsiveContainer>
            )}
          </Card>
        </Grid>

        <Grid item xs={12} md={5}>
          <Card sx={{ p: 2.5, height: 350 }}>
            <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>Risk Distribution</Typography>
            {riskDistribution.length === 0 ? (
              <EmptyState title="No risk data" description="Data will appear once claims are scored." />
            ) : (
              <ResponsiveContainer width="100%" height="85%">
                <PieChart>
                  <Pie data={riskDistribution} dataKey="count" nameKey="level" innerRadius={60} outerRadius={90} paddingAngle={4} label>
                    {riskDistribution.map((entry) => (
                      <Cell key={entry.level} fill={riskColor(entry.level)} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            )}
          </Card>
        </Grid>

        {/* Lower Row: Audit Logs vs Recent Claims */}
        <Grid item xs={12} md={5}>
          <Card sx={{ p: 2.5, height: 420, overflow: 'hidden' }}>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
              <AdminPanelSettingsOutlinedIcon color="primary" />
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>Recent Activities &amp; Audit Logs</Typography>
            </Stack>
            <Divider sx={{ mb: 1.5 }} />
            <Box sx={{ overflowY: 'auto', height: 'calc(100% - 60px)' }}>
              <List disablePadding>
                {activeLogs.map((log) => (
                  <Box key={log.log_id} sx={{ mb: 1.5 }}>
                    <ListItem alignItems="flex-start" sx={{ p: 0 }}>
                      <ListItemText
                        primary={
                          <Stack direction="row" justifyContent="space-between" alignItems="center">
                            <Chip size="small" label={log.action} color={log.action.includes('FRAUD') || log.action.includes('REJECT') ? 'error' : (log.action.includes('APPROV') ? 'success' : 'primary')} sx={{ height: 20, fontSize: '0.65rem', fontWeight: 600 }} />
                            <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                              {new Date(log.timestamp).toLocaleTimeString()}
                            </Typography>
                          </Stack>
                        }
                        secondary={
                          <Box sx={{ mt: 0.5 }}>
                            <Typography variant="body2" color="text.primary" sx={{ fontWeight: 500 }}>
                              {log.details}
                            </Typography>
                            <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                              By: {log.user_name || 'System'}
                            </Typography>
                          </Box>
                        }
                        secondaryTypographyProps={{ component: 'div' }}
                      />
                    </ListItem>
                    <Divider sx={{ mt: 1 }} />
                  </Box>
                ))}
              </List>
            </Box>
          </Card>
        </Grid>

        <Grid item xs={12} md={7}>
          <Card sx={{ p: 2.5, height: 420 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
              <Stack direction="row" alignItems="center" spacing={1}>
                <HistoryOutlinedIcon color="primary" />
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>Recent Claims Queue</Typography>
              </Stack>
              <Chip size="small" label="View all claims" onClick={() => navigate('/claims')} sx={{ cursor: 'pointer' }} />
            </Stack>
            <Divider sx={{ mb: 1.5 }} />
            {recentClaims.length === 0 ? (
              <EmptyState title="No claims yet" description="Submitted claims will appear here." />
            ) : (
              <Box sx={{ overflowX: 'auto' }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600 }}>Claim ID</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Patient</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Amount</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Risk</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Date</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recentClaims.map((c) => (
                      <TableRow key={c.id} hover sx={{ cursor: 'pointer' }} onClick={() => navigate(`/claims/${c.id}`)}>
                        <TableCell sx={{ fontWeight: 600, color: 'primary.main' }}>{c.id}</TableCell>
                        <TableCell>{c.patient.name}</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>${c.financial.claimAmount.toLocaleString()}</TableCell>
                        <TableCell><RiskChip level={c.prediction.riskLevel} /></TableCell>
                        <TableCell><StatusChip status={c.status} /></TableCell>
                        <TableCell>{c.dates.claimDate}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Box>
            )}
          </Card>
        </Grid>
      </Grid>
    </DashboardLayout>
  );
}
