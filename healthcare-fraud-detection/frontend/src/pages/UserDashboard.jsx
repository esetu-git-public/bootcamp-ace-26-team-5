import { useEffect, useState } from 'react';
import { 
  Grid, Card, Box, Typography, Stack, Table, TableHead, TableRow, TableCell, TableBody, 
  LinearProgress, Chip, Button, Divider, List, ListItem, ListItemText, ListItemIcon 
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import HourglassEmptyOutlinedIcon from '@mui/icons-material/HourglassEmptyOutlined';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import ShieldOutlinedIcon from '@mui/icons-material/ShieldOutlined';
import PaymentOutlinedIcon from '@mui/icons-material/PaymentOutlined';
import HistoryOutlinedIcon from '@mui/icons-material/HistoryOutlined';
import CircleNotificationsOutlinedIcon from '@mui/icons-material/CircleNotificationsOutlined';
import DashboardLayout from '../components/layout/DashboardLayout';
import KpiCard from '../components/common/KpiCard';
import { StatusChip } from '../components/common/RiskChip';
import EmptyState from '../components/common/EmptyState';
import * as claimsService from '../services/claimsService';
import { computeDashboard } from '../services/mockData';
import { useAuth } from '../context/AuthContext';
import theme from '../theme/theme';

export default function UserDashboard() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchClaims = () => {
      claimsService.getClaims({ ownerId: user.id }).then((claims) => {
        setData(computeDashboard(claims));
        setLoading(false);
      }).catch(err => {
        console.error("Dashboard poll error:", err);
      });
    };

    fetchClaims();
    const interval = setInterval(fetchClaims, 4000); // 4-second polling for dynamic sync during demo
    return () => clearInterval(interval);
  }, [user.id]);

  if (loading) {
    return (
      <DashboardLayout title="My Dashboard">
        <LinearProgress />
      </DashboardLayout>
    );
  }

  const { kpis, recentClaims } = data;

  // Simple Notification List derived from claims
  const notifications = recentClaims
    .filter(c => c.status !== 'Pending Review')
    .slice(0, 3)
    .map(c => ({
      id: c.id,
      text: `Claim ${c.id} status updated to ${c.status}.`,
      date: c.dates.claimDate
    }));

  return (
    <DashboardLayout title="My Dashboard">
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ xs: 'flex-start', sm: 'center' }} spacing={1.5} sx={{ mb: 2.5 }}>
        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
          Welcome back, <strong>{user.name}</strong>. Here is the active status of your insurance profile and claims.
        </Typography>
        <Button variant="contained" startIcon={<AddCircleOutlineIcon />} onClick={() => navigate('/claims/submit')}>
          Submit New Claim
        </Button>
      </Stack>

      <Grid container spacing={2.5}>
        {/* KPI Row */}
        <Grid item xs={12} sm={4}>
          <KpiCard label="My Total Claims" value={kpis.total} icon={<DescriptionOutlinedIcon />} accent={theme.tokens.blue} />
        </Grid>
        <Grid item xs={12} sm={4}>
          <KpiCard label="Approved Claims" value={kpis.genuine} icon={<CheckCircleOutlineIcon />} accent={theme.tokens.low} />
        </Grid>
        <Grid item xs={12} sm={4}>
          <KpiCard label="Claims Under Review" value={kpis.pending} icon={<HourglassEmptyOutlinedIcon />} accent={theme.tokens.medium} />
        </Grid>

        {/* Policy Summary Card */}
        <Grid item xs={12} md={6}>
          <Card sx={{ p: 2.5, height: '100%' }}>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
              <ShieldOutlinedIcon color="primary" />
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>Active Policy Summary</Typography>
            </Stack>
            <Divider sx={{ mb: 2 }} />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="caption" color="text.secondary">POLICY NUMBER</Typography>
                <Typography variant="body1" sx={{ fontWeight: 600 }}>POL-MOCK-1234</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="caption" color="text.secondary">INSURANCE TYPE</Typography>
                <Typography variant="body1" sx={{ fontWeight: 600 }}>Private Health</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="caption" color="text.secondary">TOTAL COVERAGE</Typography>
                <Typography variant="body1" sx={{ fontWeight: 600, color: 'success.main' }}>$700,000.00</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="caption" color="text.secondary">ANNUAL PREMIUM</Typography>
                <Typography variant="body1" sx={{ fontWeight: 600 }}>$15,000.00</Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="caption" color="text.secondary">POLICY STATUS</Typography>
                <Box sx={{ mt: 0.5 }}>
                  <Chip size="small" label="ACTIVE" color="success" />
                </Box>
              </Grid>
            </Grid>
          </Card>
        </Grid>

        {/* Quick Actions & Notifications */}
        <Grid item xs={12} md={6}>
          <Card sx={{ p: 2.5, height: '100%' }}>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
              <CircleNotificationsOutlinedIcon color="primary" />
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>Notifications &amp; Activity</Typography>
            </Stack>
            <Divider sx={{ mb: 2 }} />
            {notifications.length === 0 ? (
              <EmptyState 
                title="All caught up" 
                description="No new status notifications at this time." 
                icon={<CircleNotificationsOutlinedIcon sx={{ fontSize: 32 }} />}
              />
            ) : (
              <List disablePadding>
                {notifications.map((n, i) => (
                  <Box key={i}>
                    <ListItem alignItems="flex-start" sx={{ px: 0, py: 1 }}>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <CircleNotificationsOutlinedIcon color="info" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText 
                        primary={n.text}
                        secondary={n.date}
                        primaryTypographyProps={{ variant: 'body2', fontWeight: 500 }}
                        secondaryTypographyProps={{ variant: 'caption' }}
                      />
                    </ListItem>
                    {i < notifications.length - 1 && <Divider component="li" />}
                  </Box>
                ))}
              </List>
            )}
          </Card>
        </Grid>

        {/* Recent Claims Table */}
        <Grid item xs={12}>
          <Card sx={{ p: 2.5 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
              <Stack direction="row" alignItems="center" spacing={1}>
                <HistoryOutlinedIcon color="primary" />
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>My Recent Claims</Typography>
              </Stack>
              <Chip size="small" label="View all" onClick={() => navigate('/claims')} sx={{ cursor: 'pointer' }} />
            </Stack>
            {recentClaims.length === 0 ? (
              <EmptyState
                title="No claims yet"
                description="You haven't submitted any claims. Submit one to see its status here."
                icon={<DescriptionOutlinedIcon sx={{ fontSize: 40 }} />}
              />
            ) : (
              <Box sx={{ overflowX: 'auto' }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600 }}>Claim ID</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Diagnosis</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Amount</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Submission Date</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recentClaims.map((c) => (
                      <TableRow key={c.id} hover sx={{ cursor: 'pointer' }} onClick={() => navigate(`/claims/${c.id}`)}>
                        <TableCell sx={{ fontWeight: 600, color: 'primary.main' }}>{c.id}</TableCell>
                        <TableCell>{c.medical.diagnosis}</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>${c.financial.claimAmount.toLocaleString()}</TableCell>
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
