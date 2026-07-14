import { useEffect, useState } from 'react';
import { Grid, Card, Box, Typography, Stack, Table, TableHead, TableRow, TableCell, TableBody, LinearProgress, Chip, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import HourglassEmptyOutlinedIcon from '@mui/icons-material/HourglassEmptyOutlined';
import PriorityHighOutlinedIcon from '@mui/icons-material/PriorityHighOutlined';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import DashboardLayout from '../components/layout/DashboardLayout';
import KpiCard from '../components/common/KpiCard';
import { RiskChip, StatusChip } from '../components/common/RiskChip';
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
    claimsService.getClaims({ ownerId: user.id }).then((claims) => {
      setData(computeDashboard(claims));
      setLoading(false);
    });
  }, [user.id]);

  if (loading) {
    return (
      <DashboardLayout title="My Dashboard">
        <LinearProgress />
      </DashboardLayout>
    );
  }

  const { kpis, recentClaims } = data;

  return (
    <DashboardLayout title="My Dashboard">
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ xs: 'flex-start', sm: 'center' }} spacing={1.5} sx={{ mb: 2.5 }}>
        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
          Welcome back, {user.name}. Here&apos;s a summary of the claims you&apos;ve submitted.
        </Typography>
        <Button variant="contained" startIcon={<AddCircleOutlineIcon />} onClick={() => navigate('/claims/submit')}>
          Submit New Claim
        </Button>
      </Stack>

      <Grid container spacing={2.5}>
        <Grid item xs={12} sm={4} md={4}>
          <KpiCard label="My Claims" value={kpis.total} icon={<DescriptionOutlinedIcon />} accent={theme.tokens.blue} />
        </Grid>
        <Grid item xs={12} sm={4} md={4}>
          <KpiCard label="Approved" value={kpis.genuine} icon={<CheckCircleOutlineIcon />} accent={theme.tokens.low} />
        </Grid>
        <Grid item xs={12} sm={4} md={4}>
          <KpiCard label="Pending Review" value={kpis.pending} icon={<HourglassEmptyOutlinedIcon />} accent={theme.tokens.medium} />
        </Grid>

        <Grid item xs={12}>
          <Card sx={{ p: 2.5 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="subtitle1">My Recent Claims</Typography>
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
                      <TableCell>Claim ID</TableCell>
                      <TableCell>Diagnosis</TableCell>
                      <TableCell>Amount</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Date</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recentClaims.map((c) => (
                      <TableRow key={c.id} hover sx={{ cursor: 'pointer' }} onClick={() => navigate(`/claims/${c.id}`)}>
                        <TableCell sx={{ fontWeight: 600 }}>{c.id}</TableCell>
                        <TableCell>{c.medical.diagnosis}</TableCell>
                        <TableCell>${c.financial.claimAmount.toLocaleString()}</TableCell>
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
