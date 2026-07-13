import { useEffect, useState } from 'react';
import { Card, Grid, Typography, Stack, Button, LinearProgress } from '@mui/material';
import FileDownloadOutlinedIcon from '@mui/icons-material/FileDownloadOutlined';
import PictureAsPdfOutlinedIcon from '@mui/icons-material/PictureAsPdfOutlined';
import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend,
} from 'recharts';
import DashboardLayout from '../components/layout/DashboardLayout';
import * as dashboardService from '../services/dashboardService';
import theme, { riskColor } from '../theme/theme';

const PALETTE = [theme.tokens.blue, theme.tokens.teal, '#7C9CBF', '#B7C9DE', '#0B2545'];

function downloadCsv(rows, filename) {
  if (!rows.length) return;
  const headers = Object.keys(rows[0]);
  const csv = [headers.join(','), ...rows.map((r) => headers.map((h) => `"${r[h]}"`).join(','))].join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

export default function Reports() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardService.getReports().then((d) => { setData(d); setLoading(false); });
  }, []);

  if (loading) {
    return <DashboardLayout title="Reports"><LinearProgress /></DashboardLayout>;
  }

  const { monthlyClaims, riskDistribution, providerDistribution, insuranceDistribution, kpis } = data;

  const exportCsv = () => downloadCsv(
    monthlyClaims.map((m) => ({ Month: m.month, TotalClaims: m.claims, FraudClaims: m.fraud })),
    'claimguard_monthly_report.csv'
  );

  const exportPdf = () => window.print();

  return (
    <DashboardLayout title="Reports">
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2.5 }}>
        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
          {kpis.total} claims analyzed · {kpis.fraudPct}% flagged as fraud
        </Typography>
        <Stack direction="row" spacing={1.5}>
          <Button variant="outlined" startIcon={<FileDownloadOutlinedIcon />} onClick={exportCsv}>Export CSV</Button>
          <Button variant="contained" startIcon={<PictureAsPdfOutlinedIcon />} onClick={exportPdf}>Export PDF</Button>
        </Stack>
      </Stack>

      <Grid container spacing={2.5}>
        <Grid item xs={12} md={7}>
          <Card sx={{ p: 2.5, height: 340 }}>
            <Typography variant="subtitle1" sx={{ mb: 2 }}>Monthly Claims Trend</Typography>
            <ResponsiveContainer width="100%" height="85%">
              <LineChart data={monthlyClaims}>
                <CartesianGrid strokeDasharray="3 3" stroke="#EDF1F5" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="claims" name="Total Claims" stroke={theme.tokens.blue} strokeWidth={2} />
                <Line type="monotone" dataKey="fraud" name="Fraud %" stroke={theme.tokens.high} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Grid>

        <Grid item xs={12} md={5}>
          <Card sx={{ p: 2.5, height: 340 }}>
            <Typography variant="subtitle1" sx={{ mb: 2 }}>Risk Levels</Typography>
            <ResponsiveContainer width="100%" height="85%">
              <PieChart>
                <Pie data={riskDistribution} dataKey="count" nameKey="level" outerRadius={90} label>
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

        <Grid item xs={12} md={6}>
          <Card sx={{ p: 2.5, height: 340 }}>
            <Typography variant="subtitle1" sx={{ mb: 2 }}>Provider Distribution</Typography>
            <ResponsiveContainer width="100%" height="85%">
              <BarChart data={providerDistribution} margin={{ bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#EDF1F5" />
                <XAxis dataKey="provider" tick={{ fontSize: 10 }} angle={-25} textAnchor="end" interval={0} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="claims" radius={[6, 6, 0, 0]}>
                  {providerDistribution.map((_, idx) => (
                    <Cell key={idx} fill={PALETTE[idx % PALETTE.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card sx={{ p: 2.5, height: 340 }}>
            <Typography variant="subtitle1" sx={{ mb: 2 }}>Insurance Type Distribution</Typography>
            <ResponsiveContainer width="100%" height="85%">
              <PieChart>
                <Pie data={insuranceDistribution} dataKey="claims" nameKey="type" outerRadius={90} label>
                  {insuranceDistribution.map((_, idx) => (
                    <Cell key={idx} fill={PALETTE[idx % PALETTE.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Grid>
      </Grid>
    </DashboardLayout>
  );
}
