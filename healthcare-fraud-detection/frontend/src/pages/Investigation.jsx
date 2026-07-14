import { useEffect, useState } from 'react';
import { Card, Grid, Typography, Stack, LinearProgress, TextField, MenuItem } from '@mui/material';
import DashboardLayout from '../components/layout/DashboardLayout';
import { RiskChip, StatusChip } from '../components/common/RiskChip';
import EmptyState from '../components/common/EmptyState';
import * as claimsService from '../services/claimsService';
import { useNavigate } from 'react-router-dom';

export default function Investigation() {
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [risk, setRisk] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    setLoading(true);
    claimsService.getClaims({ riskOnly: true, risk }).then((data) => {
      setClaims(data);
      setLoading(false);
    });
  }, [risk]);

  return (
    <DashboardLayout title="Investigation Queue">
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2.5 }}>
        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
          Claims flagged High or Medium risk, awaiting review.
        </Typography>
        <TextField select size="small" label="Risk" value={risk} onChange={(e) => setRisk(e.target.value)} sx={{ minWidth: 160 }}>
          <MenuItem value="">All</MenuItem>
          <MenuItem value="High">High</MenuItem>
          <MenuItem value="Medium">Medium</MenuItem>
        </TextField>
      </Stack>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {!loading && claims.length === 0 ? (
        <EmptyState title="Queue is clear" description="No claims currently require investigation." />
      ) : (
        <Grid container spacing={2}>
          {claims.map((c) => (
            <Grid item xs={12} sm={6} lg={4} key={c.id}>
              <Card
                sx={{ p: 2.5, cursor: 'pointer', height: '100%', '&:hover': { borderColor: 'primary.main' } }}
                onClick={() => navigate(`/claims/${c.id}`)}
              >
                <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 1 }}>
                  <Typography variant="subtitle1">{c.id}</Typography>
                  <RiskChip level={c.prediction.riskLevel} />
                </Stack>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>{c.patient.name}</Typography>
                <Typography variant="caption" sx={{ color: 'text.secondary' }}>{c.medical.diagnosis}</Typography>
                <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mt: 2 }}>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>${c.financial.claimAmount.toLocaleString()}</Typography>
                  <StatusChip status={c.status} />
                </Stack>
                <Typography variant="caption" sx={{ display: 'block', mt: 1, color: 'text.secondary' }}>
                  Fraud probability: {Math.round(c.prediction.probability * 100)}%
                </Typography>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </DashboardLayout>
  );
}
