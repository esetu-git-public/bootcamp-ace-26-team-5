import { useEffect, useState } from 'react';
import { Card, Grid, Typography, Stack, LinearProgress, TextField, MenuItem, Box, Divider } from '@mui/material';
import DashboardLayout from '../components/layout/DashboardLayout';
import KpiCard from '../components/common/KpiCard';
import { RiskChip, StatusChip } from '../components/common/RiskChip';
import EmptyState from '../components/common/EmptyState';
import * as claimsService from '../services/claimsService';
import * as dashboardService from '../services/dashboardService';
import { useNavigate } from 'react-router-dom';
import theme from '../theme/theme';
import HourglassEmptyOutlinedIcon from '@mui/icons-material/HourglassEmptyOutlined';
import ReportProblemOutlinedIcon from '@mui/icons-material/ReportProblemOutlined';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import PriorityHighOutlinedIcon from '@mui/icons-material/PriorityHighOutlined';

export default function Investigation() {
  const [claims, setClaims] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [risk, setRisk] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = () => {
      // 1. Fetch claims in investigation queue
      claimsService.getClaims({ riskOnly: true, risk }).then((data) => {
        setClaims(data);
      }).catch(err => console.error("Error fetching officer claims:", err));

      // 2. Fetch officer dashboard statistics
      dashboardService.getDashboard('claims officer').then((d) => {
        setStats(d);
        setLoading(false);
      }).catch(err => {
        console.error("Error fetching officer stats:", err);
        setLoading(false);
      });
    };

    fetchData();
    const interval = setInterval(fetchData, 4000); // 4-second poll interval for real-time demo sync
    return () => clearInterval(interval);
  }, [risk]);

  const kpis = stats?.kpis || { pending: 0, mediumRisk: 0, highRisk: 0, reviewedClaims: 0 };

  return (
    <DashboardLayout title="Claims Operations">
      {/* KPI Section */}
      <Grid container spacing={2.5} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard 
            label="Pending Queue" 
            value={kpis.pending} 
            icon={<HourglassEmptyOutlinedIcon />} 
            accent={theme.tokens.blue} 
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard 
            label="Medium Risk" 
            value={kpis.mediumRisk} 
            icon={<ReportProblemOutlinedIcon />} 
            accent={theme.tokens.medium} 
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard 
            label="High Risk Flagged" 
            value={kpis.highRisk || stats?.kpis?.highRisk || 0} 
            icon={<PriorityHighOutlinedIcon />} 
            accent={theme.tokens.high} 
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard 
            label="Reviewed Today" 
            value={kpis.reviewedClaims || 0} 
            icon={<CheckCircleOutlineIcon />} 
            accent={theme.tokens.low} 
          />
        </Grid>
      </Grid>

      <Divider sx={{ mb: 3 }} />

      {/* Header and Filter */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2.5 }}>
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>Investigation Queue</Typography>
          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
            Claims flagged Medium or High risk requiring manual review and adjudication.
          </Typography>
        </Box>
        <TextField 
          select 
          size="small" 
          label="Filter by Risk" 
          value={risk} 
          onChange={(e) => setRisk(e.target.value)} 
          sx={{ minWidth: 180 }}
        >
          <MenuItem value="">All Flagged Risks</MenuItem>
          <MenuItem value="High">High Risk Only</MenuItem>
          <MenuItem value="Medium">Medium Risk Only</MenuItem>
        </TextField>
      </Stack>

      {loading && claims.length === 0 && <LinearProgress sx={{ mb: 2 }} />}

      {!loading && claims.length === 0 ? (
        <EmptyState title="Queue is clear" description="No claims currently require investigation." />
      ) : (
        <Grid container spacing={2.5}>
          {claims.map((c) => (
            <Grid item xs={12} sm={6} lg={4} key={c.id}>
              <Card
                sx={{ 
                  p: 2.5, 
                  cursor: 'pointer', 
                  height: '100%', 
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  '&:hover': { 
                    transform: 'translateY(-2px)',
                    boxShadow: 3,
                    borderColor: 'primary.main' 
                  } 
                }}
                onClick={() => navigate(`/claims/${c.id}`)}
              >
                <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 1.5 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, color: 'text.secondary' }}>
                    {c.id}
                  </Typography>
                  <RiskChip level={c.prediction.riskLevel} />
                </Stack>
                
                <Typography variant="body1" sx={{ fontWeight: 600, mb: 0.5 }}>{c.patient.name}</Typography>
                
                <Stack spacing={0.5} sx={{ mb: 2 }}>
                  <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                    Diagnosis: <strong>{c.medical.diagnosis}</strong>
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                    Provider: <strong>{c.medical.provider}</strong>
                  </Typography>
                </Stack>

                <Divider sx={{ my: 1.5 }} />

                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Box>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>CLAIM AMOUNT</Typography>
                    <Typography variant="body1" sx={{ fontWeight: 700 }}>
                      ${c.financial.claimAmount.toLocaleString()}
                    </Typography>
                  </Box>
                  <StatusChip status={c.status} />
                </Stack>

                <Box sx={{ mt: 2, p: 1, bgcolor: '#F8FAFC', borderRadius: 1 }}>
                  <Typography variant="caption" sx={{ color: 'text.secondary', display: 'flex', justifyContent: 'space-between' }}>
                    <span>AI Fraud Probability:</span>
                    <strong style={{ color: c.prediction.probability >= 0.7 ? '#D6483C' : '#D8A400' }}>
                      {Math.round(c.prediction.probability * 100)}%
                    </strong>
                  </Typography>
                </Box>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </DashboardLayout>
  );
}
