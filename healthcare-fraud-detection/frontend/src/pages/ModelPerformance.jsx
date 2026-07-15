import { useEffect, useState } from 'react';
import {
  Grid, Card, Box, Typography, Stack, Table, TableHead, TableRow, TableCell, TableBody,
  LinearProgress, Chip, Button
} from '@mui/material';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useNavigate } from 'react-router-dom';
import TroubleshootOutlinedIcon from '@mui/icons-material/TroubleshootOutlined';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import RateReviewOutlinedIcon from '@mui/icons-material/RateReviewOutlined';
import AutoAwesomeOutlinedIcon from '@mui/icons-material/AutoAwesomeOutlined';
import ArrowBackIosNewOutlinedIcon from '@mui/icons-material/ArrowBackIosNewOutlined';
import DashboardLayout from '../components/layout/DashboardLayout';
import KpiCard from '../components/common/KpiCard';
import EmptyState from '../components/common/EmptyState';
import * as feedbackService from '../services/feedbackService';
import theme from '../theme/theme';

const COLORS = [theme.tokens.high, theme.tokens.blue];

export default function ModelPerformance() {
  const [stats, setStats] = useState(null);
  const [feedbackList, setFeedbackList] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsRes, listRes] = await Promise.all([
        feedbackService.getFeedbackStats(),
        feedbackService.getFeedbackList()
      ]);
      setStats(statsRes.data);
      setFeedbackList(listRes.data);
    } catch (err) {
      console.error("Failed to load model performance data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <DashboardLayout title="Model Performance">
        <LinearProgress />
      </DashboardLayout>
    );
  }

  if (!stats) {
    return (
      <DashboardLayout title="Model Performance">
        <EmptyState title="No metrics available" description="Ensure predictions have been executed and feedback is submitted." />
      </DashboardLayout>
    );
  }

  const disagreementClaims = feedbackList.filter(f => f.is_incorrect);

  return (
    <DashboardLayout title="Model Performance &amp; Failure Dashboard">
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 3 }}>
        <Button startIcon={<ArrowBackIosNewOutlinedIcon sx={{ fontSize: 12 }} />} onClick={() => navigate('/dashboard')} variant="outlined" size="small">
          Back to Dashboard
        </Button>
      </Stack>

      <Grid container spacing={2.5}>
        {/* KPI Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            label="Model Accuracy"
            value={`${stats.accuracy}%`}
            icon={<CheckCircleOutlineIcon />}
            accent={theme.tokens.low}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            label="Disagreement Rate"
            value={`${stats.disagreementRate}%`}
            icon={<TroubleshootOutlinedIcon />}
            accent={theme.tokens.high}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            label="Model Failures Flagged"
            value={stats.disagreements}
            icon={<RateReviewOutlinedIcon />}
            accent={theme.tokens.medium}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            label="Total Predictions Logged"
            value={stats.totalPredictions}
            icon={<AutoAwesomeOutlinedIcon />}
            accent={theme.tokens.blue}
          />
        </Grid>

        {/* Charts & Breakdown */}
        <Grid item xs={12} md={5}>
          <Card sx={{ p: 2.5, height: 350, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="subtitle1" sx={{ mb: 1 }}>Prediction Error Breakdown</Typography>
            <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>
              Distributions of user disagreements with the AI classifications
            </Typography>

            <Box sx={{ flex: 1, minHeight: 200, position: 'relative' }}>
              {stats.disagreements === 0 ? (
                <Box sx={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center' }}>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>No failures flagged yet.</Typography>
                </Box>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={stats.labelDistribution}
                      cx="50%"
                      cy="45%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {stats.labelDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [`${value} claims`, 'Count']} />
                    <Legend verticalAlign="bottom" height={36} />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </Box>
          </Card>
        </Grid>

        <Grid item xs={12} md={7}>
          <Card sx={{ p: 2.5, height: 350, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="subtitle1" sx={{ mb: 1 }}>Error Types Metrics</Typography>
            <Typography variant="body2" sx={{ color: 'text.secondary', mb: 3 }}>
              Detailed counts of False Positives vs. False Negatives
            </Typography>

            <Stack spacing={3} sx={{ flex: 1, justifyContent: 'center' }}>
              <Box>
                <Stack direction="row" justifyContent="space-between" sx={{ mb: 1 }}>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>False Alarms (False Positives)</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.secondary' }}>
                    {stats.falsePositives} claims
                  </Typography>
                </Stack>
                <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block', mb: 0.5 }}>
                  Model predicted <strong>Fraud</strong> but the user verified it as <strong>Genuine</strong>.
                </Typography>
              </Box>

              <Box sx={{ borderTop: '1px solid #EDF1F5', pt: 2.5 }}>
                <Stack direction="row" justifyContent="space-between" sx={{ mb: 1 }}>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>Missed Frauds (False Negatives)</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.secondary' }}>
                    {stats.falseNegatives} claims
                  </Typography>
                </Stack>
                <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block', mb: 0.5 }}>
                  Model predicted <strong>Not Fraud</strong> but the user flagged it as <strong>Fraud</strong>.
                </Typography>
              </Box>
            </Stack>
          </Card>
        </Grid>

        {/* Failures Log */}
        <Grid item xs={12}>
          <Card sx={{ p: 2.5 }}>
            <Typography variant="subtitle1" sx={{ mb: 1.5 }}>AI Model Failures Log ({disagreementClaims.length})</Typography>
            {disagreementClaims.length === 0 ? (
              <EmptyState title="No model failures logged" description="All model predictions currently match user evaluations." />
            ) : (
              <Box sx={{ overflowX: 'auto' }}>
                <Table sx={{ minWidth: 650 }}>
                  <TableHead>
                    <TableRow sx={{ bgcolor: '#F8FAFC' }}>
                      <TableCell sx={{ fontWeight: 700 }}>Claim Number</TableCell>
                      <TableCell sx={{ fontWeight: 700 }}>Model Prediction</TableCell>
                      <TableCell sx={{ fontWeight: 700 }}>Actual User Label</TableCell>
                      <TableCell sx={{ fontWeight: 700 }}>Disagreement Comment / Reason</TableCell>
                      <TableCell sx={{ fontWeight: 700 }}>Flagged By</TableCell>
                      <TableCell sx={{ fontWeight: 700 }}>Date</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {disagreementClaims.map((row) => (
                      <TableRow key={row.feedback_id} hover sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                        <TableCell>
                          <Button size="small" onClick={() => navigate(`/claims/${row.claim_id}`)} sx={{ fontWeight: 600 }}>
                            {row.claim_number}
                          </Button>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={row.predicted_label || 'Unknown'}
                            color={row.predicted_label === 'Fraud' ? 'error' : 'success'}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={row.actual_label}
                            color={row.actual_label === 'Fraud' ? 'error' : 'success'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell sx={{ maxWidth: 300, whiteSpace: 'normal', wordBreak: 'break-word' }}>
                          <Typography variant="body2">{row.feedback_text || '—'}</Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>{row.user_name || 'Staff'}</Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                            {new Date(row.created_at).toLocaleDateString()}
                          </Typography>
                        </TableCell>
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
